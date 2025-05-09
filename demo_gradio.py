from diffusers_helper.hf_login import login

import os
from config import PRESET_CONFIGS, EXAMPLE_PROMPTS, TEACACHE_CONFIG, DEFAULT_UI_SETTINGS, FLOW_SHIFT_CONFIGS

os.environ['HF_HOME'] = os.path.abspath(os.path.realpath(os.path.join(os.path.dirname(__file__), './hf_download')))

# Set up paths
ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
STATIC_DIR = os.path.join(ROOT_DIR, 'static')
OUTPUTS_DIR = os.path.join(ROOT_DIR, 'outputs')

import gradio as gr
import torch
import traceback
import einops
import safetensors.torch as sf
import numpy as np
import argparse
import math

from PIL import Image
from diffusers import AutoencoderKLHunyuanVideo
from transformers import LlamaModel, CLIPTextModel, LlamaTokenizerFast, CLIPTokenizer
from diffusers_helper.hunyuan import encode_prompt_conds, vae_decode, vae_encode, vae_decode_fake
from diffusers_helper.utils import save_bcthw_as_mp4, crop_or_pad_yield_mask, soft_append_bcthw, resize_and_center_crop, state_dict_weighted_merge, state_dict_offset_merge, generate_timestamp
from diffusers_helper.models.hunyuan_video_packed import HunyuanVideoTransformer3DModelPacked
from diffusers_helper.pipelines.k_diffusion_hunyuan import sample_hunyuan
from diffusers_helper.memory import cpu, gpu, get_cuda_free_memory_gb, move_model_to_device_with_memory_preservation, offload_model_from_device_for_memory_preservation, fake_diffusers_current_device, DynamicSwapInstaller, unload_complete_models, load_model_as_complete
from diffusers_helper.thread_utils import AsyncStream, async_run
from diffusers_helper.gradio.progress_bar import make_progress_bar_css, make_progress_bar_html
from diffusers_helper.gradio.enhanced_progress_bar import get_enhanced_progress_bar_css, make_enhanced_progress_bar_html
from transformers import SiglipImageProcessor, SiglipVisionModel
from diffusers_helper.clip_vision import hf_clip_vision_encode
from diffusers_helper.bucket_tools import find_nearest_bucket


parser = argparse.ArgumentParser()
parser.add_argument('--share', action='store_true')
parser.add_argument("--server", type=str, default='0.0.0.0')
parser.add_argument("--port", type=int, required=False)
parser.add_argument("--inbrowser", action='store_true')
args = parser.parse_args()

# for win desktop probably use --server 127.0.0.1 --inbrowser
# For linux server probably use --server 127.0.0.1 or do not use any cmd flags

print(args)

free_mem_gb = get_cuda_free_memory_gb(gpu)
high_vram = free_mem_gb > 60

print(f'Free VRAM {free_mem_gb} GB')
print(f'High-VRAM Mode: {high_vram}')

text_encoder = LlamaModel.from_pretrained("hunyuanvideo-community/HunyuanVideo", subfolder='text_encoder', torch_dtype=torch.float16).cpu()
text_encoder_2 = CLIPTextModel.from_pretrained("hunyuanvideo-community/HunyuanVideo", subfolder='text_encoder_2', torch_dtype=torch.float16).cpu()
tokenizer = LlamaTokenizerFast.from_pretrained("hunyuanvideo-community/HunyuanVideo", subfolder='tokenizer')
tokenizer_2 = CLIPTokenizer.from_pretrained("hunyuanvideo-community/HunyuanVideo", subfolder='tokenizer_2')
vae = AutoencoderKLHunyuanVideo.from_pretrained("hunyuanvideo-community/HunyuanVideo", subfolder='vae', torch_dtype=torch.float16).cpu()

feature_extractor = SiglipImageProcessor.from_pretrained("Suparious/FLUX.1-Redux-dev-adaptor-bfl", subfolder='feature_extractor')
image_encoder = SiglipVisionModel.from_pretrained("Suparious/FLUX.1-Redux-dev-adaptor-bfl", subfolder='image_encoder', torch_dtype=torch.float16).cpu()

transformer = HunyuanVideoTransformer3DModelPacked.from_pretrained('Suparious/FP-image-to-video-FLUX.1-HV-bf16', torch_dtype=torch.bfloat16).cpu()

vae.eval()
text_encoder.eval()
text_encoder_2.eval()
image_encoder.eval()
transformer.eval()

if not high_vram:
    vae.enable_slicing()
    vae.enable_tiling()

transformer.high_quality_fp32_output_for_inference = True
print('transformer.high_quality_fp32_output_for_inference = True')

transformer.to(dtype=torch.bfloat16)
vae.to(dtype=torch.float16)
image_encoder.to(dtype=torch.float16)
text_encoder.to(dtype=torch.float16)
text_encoder_2.to(dtype=torch.float16)

vae.requires_grad_(False)
text_encoder.requires_grad_(False)
text_encoder_2.requires_grad_(False)
image_encoder.requires_grad_(False)
transformer.requires_grad_(False)

if not high_vram:
    # DynamicSwapInstaller is same as huggingface's enable_sequential_offload but 3x faster
    DynamicSwapInstaller.install_model(transformer, device=gpu)
    DynamicSwapInstaller.install_model(text_encoder, device=gpu)
else:
    text_encoder.to(gpu)
    text_encoder_2.to(gpu)
    image_encoder.to(gpu)
    vae.to(gpu)
    transformer.to(gpu)

stream = AsyncStream()

os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)


@torch.no_grad()
def worker(input_image, prompt, n_prompt, seed, total_second_length, latent_window_size, steps, cfg, gs, rs, gpu_memory_preservation, use_teacache, hand_optimization, flow_preset, mp4_crf):
    total_latent_sections = (total_second_length * 30) / (latent_window_size * 4)
    total_latent_sections = int(max(round(total_latent_sections), 1))

    job_id = generate_timestamp()

    stream.output_queue.push(('progress', (None, '', make_enhanced_progress_bar_html(0, 'Starting ...'))))

    try:
        # Clean GPU
        if not high_vram:
            unload_complete_models(
                text_encoder, text_encoder_2, image_encoder, vae, transformer
            )

        # Text encoding

        stream.output_queue.push(('progress', (None, '', make_enhanced_progress_bar_html(0, 'Text encoding ...'))))

        if not high_vram:
            fake_diffusers_current_device(text_encoder, gpu)  # since we only encode one text - that is one model move and one encode, offload is same time consumption since it is also one load and one encode.
            load_model_as_complete(text_encoder_2, target_device=gpu)

        llama_vec, clip_l_pooler = encode_prompt_conds(prompt, text_encoder, text_encoder_2, tokenizer, tokenizer_2)

        if cfg == 1:
            llama_vec_n, clip_l_pooler_n = torch.zeros_like(llama_vec), torch.zeros_like(clip_l_pooler)
        else:
            llama_vec_n, clip_l_pooler_n = encode_prompt_conds(n_prompt, text_encoder, text_encoder_2, tokenizer, tokenizer_2)

        llama_vec, llama_attention_mask = crop_or_pad_yield_mask(llama_vec, length=512)
        llama_vec_n, llama_attention_mask_n = crop_or_pad_yield_mask(llama_vec_n, length=512)

        # Processing input image

        stream.output_queue.push(('progress', (None, '', make_enhanced_progress_bar_html(0, 'Image processing ...'))))

        H, W, C = input_image.shape
        height, width = find_nearest_bucket(H, W, resolution=640)
        input_image_np = resize_and_center_crop(input_image, target_width=width, target_height=height)

        Image.fromarray(input_image_np).save(os.path.join(OUTPUTS_DIR, f'{job_id}.png'))

        input_image_pt = torch.from_numpy(input_image_np).float() / 127.5 - 1
        input_image_pt = input_image_pt.permute(2, 0, 1)[None, :, None]

        # VAE encoding

        stream.output_queue.push(('progress', (None, '', make_enhanced_progress_bar_html(0, 'VAE encoding ...'))))

        if not high_vram:
            load_model_as_complete(vae, target_device=gpu)

        start_latent = vae_encode(input_image_pt, vae)

        # CLIP Vision

        stream.output_queue.push(('progress', (None, '', make_enhanced_progress_bar_html(0, 'CLIP Vision encoding ...'))))

        if not high_vram:
            load_model_as_complete(image_encoder, target_device=gpu)

        image_encoder_output = hf_clip_vision_encode(input_image_np, feature_extractor, image_encoder)
        image_encoder_last_hidden_state = image_encoder_output.last_hidden_state

        # Dtype

        llama_vec = llama_vec.to(transformer.dtype)
        llama_vec_n = llama_vec_n.to(transformer.dtype)
        clip_l_pooler = clip_l_pooler.to(transformer.dtype)
        clip_l_pooler_n = clip_l_pooler_n.to(transformer.dtype)
        image_encoder_last_hidden_state = image_encoder_last_hidden_state.to(transformer.dtype)

        # Sampling

        stream.output_queue.push(('progress', (None, '', make_enhanced_progress_bar_html(0, 'Start sampling ...'))))

        rnd = torch.Generator("cpu").manual_seed(seed)
        num_frames = latent_window_size * 4 - 3

        history_latents = torch.zeros(size=(1, 16, 1 + 2 + 16, height // 8, width // 8), dtype=torch.float32).cpu()
        history_pixels = None
        total_generated_latent_frames = 0

        latent_paddings = reversed(range(total_latent_sections))

        if total_latent_sections > 4:
            # In theory the latent_paddings should follow the above sequence, but it seems that duplicating some
            # items looks better than expanding it when total_latent_sections > 4
            # One can try to remove below trick and just
            # use `latent_paddings = list(reversed(range(total_latent_sections)))` to compare
            latent_paddings = [3] + [2] * (total_latent_sections - 3) + [1, 0]

        for latent_padding in latent_paddings:
            is_last_section = latent_padding == 0
            latent_padding_size = latent_padding * latent_window_size

            if stream.input_queue.top() == 'end':
                stream.output_queue.push(('end', None))
                return

            print(f'latent_padding_size = {latent_padding_size}, is_last_section = {is_last_section}')

            indices = torch.arange(0, sum([1, latent_padding_size, latent_window_size, 1, 2, 16])).unsqueeze(0)
            clean_latent_indices_pre, blank_indices, latent_indices, clean_latent_indices_post, clean_latent_2x_indices, clean_latent_4x_indices = indices.split([1, latent_padding_size, latent_window_size, 1, 2, 16], dim=1)
            clean_latent_indices = torch.cat([clean_latent_indices_pre, clean_latent_indices_post], dim=1)

            clean_latents_pre = start_latent.to(history_latents)
            clean_latents_post, clean_latents_2x, clean_latents_4x = history_latents[:, :, :1 + 2 + 16, :, :].split([1, 2, 16], dim=2)
            clean_latents = torch.cat([clean_latents_pre, clean_latents_post], dim=2)

            if not high_vram:
                unload_complete_models()
                move_model_to_device_with_memory_preservation(transformer, target_device=gpu, preserved_memory_gb=gpu_memory_preservation)

            # Handle TeaCache settings based on user preferences
            # If hand optimization is enabled and TeaCache is enabled, we use modified TeaCache settings
            if use_teacache:
                if hand_optimization:
                    # Use the hand-optimized threshold from config
                    rel_l1_thresh = TEACACHE_CONFIG["hand_optimized"]["rel_l1_thresh"]
                    transformer.initialize_teacache(enable_teacache=True, num_steps=steps, rel_l1_thresh=rel_l1_thresh)
                    print(f"TeaCache enabled with hand optimization (rel_l1_thresh={rel_l1_thresh})")
                else:
                    # Use standard TeaCache settings from config
                    rel_l1_thresh = TEACACHE_CONFIG["standard"]["rel_l1_thresh"]
                    transformer.initialize_teacache(enable_teacache=True, num_steps=steps, rel_l1_thresh=rel_l1_thresh)
                    print(f"TeaCache enabled with standard settings (rel_l1_thresh={rel_l1_thresh})")
            else:
                transformer.initialize_teacache(enable_teacache=False)
                print("TeaCache disabled")
                
            # Get the actual flow preset name from the config if needed
            actual_flow_preset = flow_preset
            if actual_flow_preset in FLOW_SHIFT_CONFIGS:
                actual_flow_preset = FLOW_SHIFT_CONFIGS[actual_flow_preset]["flow_preset"]
            
            print(f"Using flow preset: {actual_flow_preset}")

            def callback(d):
                preview = d['denoised']
                preview = vae_decode_fake(preview)

                preview = (preview * 255.0).detach().cpu().numpy().clip(0, 255).astype(np.uint8)
                preview = einops.rearrange(preview, 'b c t h w -> (b h) (t w) c')

                if stream.input_queue.top() == 'end':
                    stream.output_queue.push(('end', None))
                    raise KeyboardInterrupt('User ends the task.')

                current_step = d['i'] + 1
                percentage = int(100.0 * current_step / steps)
                hint = f'Sampling {current_step}/{steps}'
                desc = f'Total generated frames: {int(max(0, total_generated_latent_frames * 4 - 3))}, Video length: {max(0, (total_generated_latent_frames * 4 - 3) / 30) :.2f} seconds (FPS-30). The video is being extended now ...'
                stream.output_queue.push(('progress', (preview, desc, make_enhanced_progress_bar_html(percentage, hint))))
                return

            generated_latents = sample_hunyuan(
                transformer=transformer,
                sampler='unipc',
                width=width,
                height=height,
                frames=num_frames,
                real_guidance_scale=cfg,
                distilled_guidance_scale=gs,
                guidance_rescale=rs,
                # shift=3.0,  # Replaced with flow_preset
                flow_preset=actual_flow_preset,  # Use optimized flow shift parameters
                num_inference_steps=steps,
                generator=rnd,
                prompt_embeds=llama_vec,
                prompt_embeds_mask=llama_attention_mask,
                prompt_poolers=clip_l_pooler,
                negative_prompt_embeds=llama_vec_n,
                negative_prompt_embeds_mask=llama_attention_mask_n,
                negative_prompt_poolers=clip_l_pooler_n,
                device=gpu,
                dtype=torch.bfloat16,
                image_embeddings=image_encoder_last_hidden_state,
                latent_indices=latent_indices,
                clean_latents=clean_latents,
                clean_latent_indices=clean_latent_indices,
                clean_latents_2x=clean_latents_2x,
                clean_latent_2x_indices=clean_latent_2x_indices,
                clean_latents_4x=clean_latents_4x,
                clean_latent_4x_indices=clean_latent_4x_indices,
                callback=callback,
            )

            if is_last_section:
                generated_latents = torch.cat([start_latent.to(generated_latents), generated_latents], dim=2)

            total_generated_latent_frames += int(generated_latents.shape[2])
            history_latents = torch.cat([generated_latents.to(history_latents), history_latents], dim=2)

            if not high_vram:
                offload_model_from_device_for_memory_preservation(transformer, target_device=gpu, preserved_memory_gb=8)
                load_model_as_complete(vae, target_device=gpu)

            real_history_latents = history_latents[:, :, :total_generated_latent_frames, :, :]

            if history_pixels is None:
                history_pixels = vae_decode(real_history_latents, vae).cpu()
            else:
                section_latent_frames = (latent_window_size * 2 + 1) if is_last_section else (latent_window_size * 2)
                overlapped_frames = latent_window_size * 4 - 3

                current_pixels = vae_decode(real_history_latents[:, :, :section_latent_frames], vae).cpu()
                history_pixels = soft_append_bcthw(current_pixels, history_pixels, overlapped_frames)

            if not high_vram:
                unload_complete_models()

            output_filename = os.path.join(OUTPUTS_DIR, f'{job_id}_{total_generated_latent_frames}.mp4')

            save_bcthw_as_mp4(history_pixels, output_filename, fps=30, crf=mp4_crf)

            print(f'Decoded. Current latent shape {real_history_latents.shape}; pixel shape {history_pixels.shape}')

            stream.output_queue.push(('file', output_filename))

            if is_last_section:
                break
    except:
        traceback.print_exc()

        if not high_vram:
            unload_complete_models(
                text_encoder, text_encoder_2, image_encoder, vae, transformer
            )

    stream.output_queue.push(('end', None))
    return


def process(input_image, prompt, n_prompt, seed, total_second_length, latent_window_size, steps, cfg, gs, rs, gpu_memory_preservation, use_teacache, hand_optimization, flow_preset, mp4_crf):
    global stream
    assert input_image is not None, 'No input image!'

    yield None, None, '', '', gr.update(interactive=False), gr.update(interactive=True)

    stream = AsyncStream()

    async_run(worker, input_image, prompt, n_prompt, seed, total_second_length, latent_window_size, steps, cfg, gs, rs, gpu_memory_preservation, use_teacache, hand_optimization, flow_preset, mp4_crf)

    output_filename = None

    while True:
        flag, data = stream.output_queue.next()

        if flag == 'file':
            output_filename = data
            yield output_filename, gr.update(), gr.update(), gr.update(), gr.update(interactive=False), gr.update(interactive=True)

        if flag == 'progress':
            preview, desc, html = data
            yield gr.update(), gr.update(visible=True, value=preview), desc, html, gr.update(interactive=False), gr.update(interactive=True)

        if flag == 'end':
            yield output_filename, gr.update(visible=False), gr.update(), '', gr.update(interactive=True), gr.update(interactive=False)
            break


def end_process():
    stream.input_queue.push('end')


# Quick prompts are loaded from config.py
quick_prompts = [[x] for x in EXAMPLE_PROMPTS]


# Combine progress bar CSS with custom CSS
custom_css_path = os.path.join(STATIC_DIR, 'custom.css')
custom_css = """
"""

# Try to read custom CSS file if it exists
if os.path.exists(custom_css_path):
    try:
        with open(custom_css_path, 'r') as f:
            custom_css = f.read()
    except Exception as e:
        print(f"Could not read custom CSS file: {e}")

# Combine CSS
css = make_progress_bar_css() + get_enhanced_progress_bar_css() + custom_css

# Create Gradio interface
block = gr.Blocks(css=css).queue()
with block:
    gr.Markdown('# FramePack AI Video Generator')
    with gr.Row():
        with gr.Column():
            input_image = gr.Image(sources='upload', type="numpy", label="Image", height=320)
            prompt = gr.Textbox(label="Prompt", value='')
            example_quick_prompts = gr.Dataset(samples=quick_prompts, label='Quick List', samples_per_page=1000, components=[prompt])
            example_quick_prompts.click(lambda x: x[0], inputs=[example_quick_prompts], outputs=prompt, show_progress=False, queue=False)

            with gr.Row():
                with gr.Column(scale=4):
                    start_button = gr.Button(value="Start Generation", variant="primary")
                with gr.Column(scale=2):
                    end_button = gr.Button(value="End Generation", interactive=False, variant="stop")

            with gr.Group():
                with gr.Accordion("Presets", open=True):
                    preset_dropdown = gr.Dropdown(
                        label="Preset Configurations", 
                        choices=list(PRESET_CONFIGS.keys()), 
                        value="Default",
                        info="Select a preset to automatically configure parameters for specific types of videos",
                        elem_id="preset_dropdown"
                    )
                
                with gr.Accordion("Basic Settings", open=True):
                    n_prompt = gr.Textbox(label="Negative Prompt", value="", visible=False)  # Not used
                    seed = gr.Number(
                        label="Seed", 
                        value=DEFAULT_UI_SETTINGS["seed"], 
                        precision=0, 
                        info="Random seed for generation. Use the same seed to get consistent results."
                    )
                    total_second_length = gr.Slider(
                        label="Total Video Length (Seconds)", 
                        minimum=1, 
                        maximum=120, 
                        value=DEFAULT_UI_SETTINGS["total_second_length"], 
                        step=0.1,
                        info="Length of the generated video in seconds. Longer videos take more time to generate."
                    )
                    latent_window_size = gr.Slider(
                        label="Latent Window Size", 
                        minimum=1, 
                        maximum=33, 
                        value=DEFAULT_UI_SETTINGS["latent_window_size"], 
                        step=1, 
                        visible=False
                    )  # Should not change
                
                with gr.Accordion("Performance Settings", open=False):
                    with gr.Row():
                        use_teacache = gr.Checkbox(
                            label='Use TeaCache', 
                            value=DEFAULT_UI_SETTINGS["use_teacache"], 
                            info='Speeds up generation by 1.5-2x, but may affect detail quality in some cases.'
                        )
                        hand_optimization = gr.Checkbox(
                            label='Optimize for Hands/Details', 
                            value=DEFAULT_UI_SETTINGS["hand_optimization"], 
                            info='Improves hand and fine detail quality but slightly reduces speed when TeaCache is enabled.'
                        )
                    
                    gpu_memory_preservation = gr.Slider(
                        label="GPU Memory Preservation (GB)", 
                        minimum=6, 
                        maximum=128, 
                        value=DEFAULT_UI_SETTINGS["gpu_memory_preservation"], 
                        step=0.1, 
                        info="Increase this value if you encounter Out-of-Memory errors. Higher values reduce speed."
                    )
                    
                    mp4_crf = gr.Slider(
                        label="MP4 Compression Quality", 
                        minimum=0, 
                        maximum=50, 
                        value=DEFAULT_UI_SETTINGS["mp4_crf"], 
                        step=1, 
                        info="Lower values mean higher quality video. 0 is uncompressed. Values between 15-25 are recommended."
                    )
                
                with gr.Accordion("Advanced Generation Settings", open=False):
                    with gr.Column():
                        steps = gr.Slider(
                            label="Diffusion Steps", 
                            minimum=10, 
                            maximum=100, 
                            value=DEFAULT_UI_SETTINGS["steps"], 
                            step=1, 
                            info='Higher values generally improve quality but increase generation time. 20-30 is a good range.'
                        )
                        
                        flow_preset = gr.Dropdown(
                            label="Flow Shift Preset",
                            choices=list(FLOW_SHIFT_CONFIGS.keys()),
                            value=DEFAULT_UI_SETTINGS["flow_preset"],
                            info="Controls the diffusion scheduler behavior. Different options are optimized for different types of content."
                        )
                    
                    with gr.Column(visible=False):  # Hidden settings
                        cfg = gr.Slider(
                            label="CFG Scale", 
                            minimum=1.0, 
                            maximum=32.0, 
                            value=DEFAULT_UI_SETTINGS["cfg"], 
                            step=0.01, 
                            visible=False
                        )  # Should not change
                        
                        gs = gr.Slider(
                            label="Guidance Scale", 
                            minimum=1.0, 
                            maximum=32.0, 
                            value=DEFAULT_UI_SETTINGS["gs"], 
                            step=0.1, 
                            info='Controls how closely output follows prompt. Higher values give stronger prompt adherence but may reduce naturalness.'
                        )
                        
                        rs = gr.Slider(
                            label="CFG Re-Scale", 
                            minimum=0.0, 
                            maximum=1.0, 
                            value=DEFAULT_UI_SETTINGS["rs"], 
                            step=0.01, 
                            visible=False
                        )  # Should not change

        with gr.Column():
            preview_image = gr.Image(label="Next Latents", height=200, visible=False)
            result_video = gr.Video(label="Finished Frames", autoplay=True, show_share_button=False, height=512, loop=True)
            gr.Markdown('Note that the ending actions will be generated before the starting actions due to the inverted sampling. If the starting action is not in the video, you just need to wait, and it will be generated later.')
            progress_desc = gr.Markdown('', elem_classes='no-generating-animation')
            progress_bar = gr.HTML('', elem_classes='no-generating-animation')
            
            with gr.Accordion("Help & Tips", open=False, elem_id="help_tips"):
                gr.Markdown("""
                ### Tips for Better Results
                
                - **For hand movements**: Disable TeaCache or enable Hand Optimization for better quality with hands and detailed movements
                - **For talking faces**: Use the "Talking" preset which is optimized for facial expressions
                - **For smoother videos**: Try increasing Steps to 30-35 for higher quality, but this will increase generation time
                - **For memory issues**: If you encounter Out-of-Memory errors, increase the GPU Memory Preservation value
                - **Seed control**: Use the same seed value to get consistent results across multiple generations
                
                ### About Inverted Sampling
                The ending actions will be generated before the starting actions due to inverted sampling. If the beginning of your video isn't visible yet, just wait - it will be generated later in the process.
                """)

    gr.HTML('<div style="text-align:center; margin-top:20px;">Share your results and find ideas at the <a href="https://x.com/search?q=framepack&f=live" target="_blank">FramePack Twitter (X) thread</a></div>')

    ips = [input_image, prompt, n_prompt, seed, total_second_length, latent_window_size, steps, cfg, gs, rs, gpu_memory_preservation, use_teacache, hand_optimization, flow_preset, mp4_crf]
    start_button.click(fn=process, inputs=ips, outputs=[result_video, preview_image, progress_desc, progress_bar, start_button, end_button])
    end_button.click(fn=end_process)
    
    # Function to apply preset configurations
    def apply_preset(preset_name):
        preset = PRESET_CONFIGS.get(preset_name, PRESET_CONFIGS["Default"])
        return [
            gr.update(value=preset["prompt"]),  # prompt
            gr.update(),  # n_prompt (no change)
            gr.update(),  # seed (no change)
            gr.update(),  # total_second_length (no change)
            gr.update(),  # latent_window_size (no change)
            gr.update(value=preset["steps"]),  # steps
            gr.update(),  # cfg (no change)
            gr.update(value=preset["gs"]),  # gs
            gr.update(),  # rs (no change)
            gr.update(value=preset["gpu_memory_preservation"]),  # gpu_memory_preservation
            gr.update(value=preset["use_teacache"]),  # use_teacache
            # Enable hand optimization for certain presets that need it
            gr.update(value=not preset["use_teacache"]),  # If TeaCache is disabled, no need for hand optimization
            gr.update(value=preset["flow_preset"] if "flow_preset" in preset else "standard"),  # flow_preset
            gr.update()   # mp4_crf (no change)
        ]
    
    # Connect the preset dropdown to update the parameters
    preset_dropdown.change(
        fn=apply_preset,
        inputs=[preset_dropdown],
        outputs=[prompt, n_prompt, seed, total_second_length, latent_window_size, 
                steps, cfg, gs, rs, gpu_memory_preservation, use_teacache, hand_optimization, flow_preset, mp4_crf]
    )


block.launch(
    server_name=args.server,
    server_port=args.port,
    share=args.share,
    inbrowser=args.inbrowser,
)
