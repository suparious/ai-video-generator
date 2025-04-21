# ai-video-generator

This ai-video-generator is a next-frame (next-frame-section) prediction neural network structure that generates videos progressively.

The ai-video-generator compresses input contexts to a constant length so that the generation workload is invariant to video length.

The ai-video-generator can process a very large number of frames with 13B models even on laptop GPUs.

ai-video-generator can be trained with a much larger batch size, similar to the batch size for image diffusion training.

## Requirements

Note that this repo is a functional desktop software with minimal standalone high-quality sampling system and memory management.

- Nvidia GPU in RTX 30XX, 40XX, 50XX series that supports fp16 and bf16. The GTX 10XX/20XX are not tested.
- Linux or Windows operating system.
- At least 6GB GPU memory.

To generate 1-minute video (60 seconds) at 30fps (1800 frames) using 13B model, the minimal required GPU memory is 6GB. (Yes 6 GB, not a typo. Laptop GPUs are okay.)

About speed, on my RTX 4090 desktop it generates at a speed of 2.5 seconds/frame (unoptimized) or 1.5 seconds/frame (teacache). On my laptops like 3070ti laptop or 3060 laptop, it is about 4x to 8x slower.

In any case, you will directly see the generated frames since it is next-frame(-section) prediction. So you will get lots of visual feedback before the entire video is generated.

## Installation

On a Debian / Ubuntu system, install dev dependencies:

```bash
sudo apt update

sudo apt install build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl git libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

sudo apt install python3-full python3-pip python3-wheel python3-venv

sudo apt install libavutil-dev libavformat-dev libavcodec-dev libavdevice-dev libavfilter-dev libswscale-dev gfortran libopenblas-dev cmake libxsimd-dev

sudo apt install llvm
```

We recommend having an independent Python 3.13.

- Explicitly setup your torch ahead of the requirements, if you have special needs, such as ROCm or older / newer NVIDIA
  `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128`

- Then install requirements the normal way
  `pip install -r requirements.txt`

To start the GUI, run:

`python demo_gradio.py`

Note that it supports `--share`, `--port`, `--server`, and so on.

The software supports PyTorch attention, xformers, flash-attn, sage-attention. By default, it will just use PyTorch attention. You can install those attention kernels if you know how. If you have problems with the defaults, comment them out form the `requirements.txt`.

For example, to install a specific version of sage-attention, comment it out from the `requirements.txt` and then run:

`pip install sageattention==1.0.6`

However, you are highly recommended to first try without sage-attention since it will influence results, though the influence is minimal.

Building the wheels for all of these kernels can take a long time.

## GUI

On the left you upload an image and write a prompt.

On the right are the generated videos and latent previews.

Because this is a next-frame-section prediction model, videos will be generated longer and longer.

You will see the progress bar for each section and the latent preview for the next section.

Note that the initial progress may be slower than later diffusion as the device may need some warmup.

## Prompting Guideline

Many people would ask how to write better prompts.

Below is a ChatGPT template that I personally often use to get prompts:

```plaintext
You are an assistant that writes short, motion-focused prompts for animating images.

When the user sends an image, respond with a single, concise prompt describing visual motion (such as human activity, moving objects, or camera movements). Focus only on how the scene could come alive and become dynamic using brief phrases.

Larger and more dynamic motions (like dancing, jumping, running, etc.) are preferred over smaller or more subtle ones (like standing still, sitting, etc.).

Describe subject, then motion, then other things. For example: "The girl dances gracefully, with clear movements, full of charm."

If there is something that can dance (like a man, girl, robot, etc.), then prefer to describe it as dancing.

Stay in a loop: one image in, one motion prompt out. Do not explain, ask questions, or generate multiple options.
```

You paste the instruct to ChatGPT and then feed it an image to get prompt like this:

_The man dances powerfully, striking sharp poses and gliding smoothly across the reflective floor._

Usually this will give you a prompt that works well.

You can also write prompts yourself. Concise prompts are usually preferred, for example:

_The girl dances gracefully, with clear movements, full of charm._

_The man dances powerfully, with clear movements, full of energy._

and so on.

## Citation

@article{zhang2025ai-video-generator,
title={Packing Input Frame Contexts in Next-Frame Prediction Models for Video Generation},
author={Lvmin Zhang and Maneesh Agrawala},
journal={Arxiv},
year={2025}
}
