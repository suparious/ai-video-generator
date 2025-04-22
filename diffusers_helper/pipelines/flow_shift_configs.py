"""
Optimized Flow Shift configurations for different video generation scenarios.

Based on findings from the FramePack paper:
'Packing Input Frame Context in Next-Frame Prediction Models for Video Generation'
(Zhang & Agrawala, 2025, https://arxiv.org/abs/2504.12626)

The paper observes: "...because next-frame prediction supports more balanced diffusion schedulers 
with less extreme flow shift timesteps. We observe that the resulting less aggressive schedulers 
may lead to improved visual quality."
"""

import math


# Base flux time shift function
def flux_time_shift(t, mu=1.15, sigma=1.0):
    """
    Applies time shift to the scheduler based on mu and sigma parameters.
    
    Args:
        t: Time step values (between 0 and 1)
        mu: Flow shift magnitude parameter (higher = more extreme shift)
        sigma: Flow shift curve parameter (affects the shape of the curve)
    
    Returns:
        Shifted time values
    """
    return math.exp(mu) / (math.exp(mu) + (1 / t - 1) ** sigma)


# Optimized calculation of mu based on content type
def calculate_optimized_mu(context_length, content_type="balanced", detail_level="standard"):
    """
    Calculate optimized mu parameter for different content types and detail levels.
    
    Args:
        context_length: Length of the context (sequence length)
        content_type: Type of content (balanced, subtle, dynamic)
        detail_level: Level of detail desired (standard, high, extreme)
    
    Returns:
        Optimized mu value
    """
    # Base calculation from original implementation
    x1, y1 = 256, 0.5
    x2, y2 = 4096, 1.15
    exp_max = 7.0
    
    # Calculate base mu
    k = (y2 - y1) / (x2 - x1)
    b = y1 - k * x1
    base_mu = k * context_length + b
    
    # Content type adjustments (based on paper findings)
    # More balanced schedulers = lower mu values
    content_type_adjustments = {
        "balanced": 0.0,      # Default, no adjustment
        "subtle": -0.2,       # Less aggressive for subtle motion
        "dynamic": 0.1,       # Slightly more aggressive for dynamic motion
        "talking": -0.15,     # Less aggressive for talking faces
        "dance": -0.05,       # Slightly less aggressive for dance
        "handdetail": -0.25,  # Much less aggressive for hand details
    }
    
    # Detail level adjustments
    detail_level_adjustments = {
        "standard": 0.0,      # Default, no adjustment
        "high": -0.1,         # Less aggressive for high detail
        "extreme": -0.2,      # Much less aggressive for extreme detail
    }
    
    # Calculate final mu with adjustments
    final_mu = base_mu + content_type_adjustments.get(content_type, 0.0) + detail_level_adjustments.get(detail_level, 0.0)
    
    # Ensure we don't exceed maximum
    final_mu = min(final_mu, math.log(exp_max))
    
    # Ensure we don't go too low
    final_mu = max(final_mu, 0.3)
    
    return final_mu


# Optimized calculation of sigma based on content type
def calculate_optimized_sigma(content_type="balanced", detail_level="standard"):
    """
    Calculate optimized sigma parameter for different content types and detail levels.
    
    Args:
        content_type: Type of content (balanced, subtle, dynamic)
        detail_level: Level of detail desired (standard, high, extreme)
    
    Returns:
        Optimized sigma value
    """
    # Base sigma is 1.0
    base_sigma = 1.0
    
    # Content type adjustments
    content_type_adjustments = {
        "balanced": 0.0,      # Default, no adjustment
        "subtle": 0.1,        # Higher sigma for subtle motion (smoother curve)
        "dynamic": -0.05,     # Lower sigma for dynamic motion (steeper curve)
        "talking": 0.05,      # Slightly higher sigma for talking faces
        "dance": -0.02,       # Slight adjustment for dance
        "handdetail": 0.15,   # Higher sigma for hand details (smoother curve)
    }
    
    # Detail level adjustments
    detail_level_adjustments = {
        "standard": 0.0,      # Default, no adjustment
        "high": 0.05,         # Higher sigma for high detail
        "extreme": 0.1,       # Even higher sigma for extreme detail
    }
    
    # Calculate final sigma with adjustments
    final_sigma = base_sigma + content_type_adjustments.get(content_type, 0.0) + detail_level_adjustments.get(detail_level, 0.0)
    
    # Ensure we don't go too low
    final_sigma = max(final_sigma, 0.7)
    
    # Ensure we don't go too high
    final_sigma = min(final_sigma, 1.3)
    
    return final_sigma


# Flow shift presets for different content types
FLOW_SHIFT_PRESETS = {
    "Default": {
        "content_type": "balanced",
        "detail_level": "standard",
        "description": "Balanced settings suitable for most content"
    },
    "Dance": {
        "content_type": "dance",
        "detail_level": "high",
        "description": "Optimized for dance movements with good detail preservation"
    },
    "Talking": {
        "content_type": "talking",
        "detail_level": "standard",
        "description": "Fine-tuned for facial expressions and talking animations"
    },
    "Action": {
        "content_type": "dynamic",
        "detail_level": "standard",
        "description": "Enhanced for dynamic movements and actions"
    },
    "Subtle Movement": {
        "content_type": "subtle",
        "detail_level": "high",
        "description": "Gentler settings for minimal, gradual movements"
    },
    "Hand Detail": {
        "content_type": "handdetail",
        "detail_level": "extreme",
        "description": "Specialized for detailed hand gestures and finger movements"
    }
}
