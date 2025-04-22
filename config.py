"""
Configuration settings for FramePack AI Video Generator
"""

# Flow shift configurations
FLOW_SHIFT_CONFIGS = {
    "standard": {
        "flow_preset": "Default"
    },
    "dance": {
        "flow_preset": "Dance"
    },
    "talking": {
        "flow_preset": "Talking"
    },
    "action": {
        "flow_preset": "Action"
    },
    "subtle": {
        "flow_preset": "Subtle Movement"
    },
    "hand_detail": {
        "flow_preset": "Hand Detail"
    }
}

# Preset configurations for different video types
PRESET_CONFIGS = {
    "Default": {
        "prompt": "",
        "use_teacache": True,
        "steps": 25,
        "gs": 10.0,
        "gpu_memory_preservation": 6,
        "flow_preset": "standard"
    },
    "Dance": {
        "prompt": "The person dances gracefully, with clear movements, full of charm.",
        "use_teacache": False,  # Disable TeaCache for better hand details
        "steps": 30,
        "gs": 12.0,
        "gpu_memory_preservation": 6,
        "flow_preset": "dance"
    },
    "Talking": {
        "prompt": "The person is talking, with clear facial expressions, gesturing naturally.",
        "use_teacache": True,
        "steps": 22,
        "gs": 8.0,
        "gpu_memory_preservation": 6,
        "flow_preset": "talking"
    },
    "Action": {
        "prompt": "The person performs an action with flowing movement. High quality, detailed.", 
        "use_teacache": False,  # Disable TeaCache for better hand details
        "steps": 30, 
        "gs": 12.0,
        "gpu_memory_preservation": 6,
        "flow_preset": "action"
    },
    "Subtle Movement": {
        "prompt": "The person makes subtle movements with minimal change. Slow, deliberate motion.",
        "use_teacache": True,
        "steps": 20,
        "gs": 7.0,
        "gpu_memory_preservation": 6,
        "flow_preset": "subtle"
    },
    "Hand Movement": {
        "prompt": "The person makes detailed hand gestures and finger movements, demonstrating fine motor control.",
        "use_teacache": False,  # Disable TeaCache completely for best hand details
        "steps": 35,
        "gs": 14.0,
        "gpu_memory_preservation": 8,
        "flow_preset": "hand_detail"
    }
}

# Example prompts for different scenarios
EXAMPLE_PROMPTS = [
    "The person dances gracefully, with clear movements, full of charm.",
    "The person performs a spinning motion with arms extended.",
    "The person talks animatedly, using hand gestures to emphasize points.",
    "The person makes subtle movements, with a calm expression.",
    "The person demonstrates a yoga pose with balanced form.",
    "The person plays an invisible piano with detailed finger movements.",
    "The person waves hello with a friendly smile.",
    "The person walks forward confidently, maintaining eye contact.",
]

# TeaCache configurations
TEACACHE_CONFIG = {
    "standard": {
        "rel_l1_thresh": 0.15,  # Standard threshold - 2.1x speedup with good quality
    },
    "hand_optimized": {
        "rel_l1_thresh": 0.25,  # Higher threshold for better hand details
    },
    "quality_first": {
        "rel_l1_thresh": 0.35,  # Maximum quality preservation with minimal speedup
    }
}

# Default UI settings
DEFAULT_UI_SETTINGS = {
    "seed": 31337,
    "total_second_length": 5.0,
    "latent_window_size": 9,
    "steps": 25,
    "cfg": 1.0,
    "gs": 10.0,
    "rs": 0.0,
    "gpu_memory_preservation": 6,
    "use_teacache": True,
    "hand_optimization": True,
    "mp4_crf": 16,
    "flow_preset": "standard"  # Default flow shift preset
}
