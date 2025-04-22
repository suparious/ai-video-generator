# Flow Shift Parameter Tuning in FramePack

This document describes the implementation of optimized flow shift parameters based on the FramePack paper: [Packing Input Frame Context in Next-Frame Prediction Models for Video Generation](https://arxiv.org/abs/2504.12626).

## Background

The paper notes: *"because next-frame prediction supports more balanced diffusion schedulers with less extreme flow shift timesteps. We observe that the resulting less aggressive schedulers may lead to improved visual quality."*

Flow shift parameters control how the diffusion sampling process unfolds over time. More balanced parameters lead to more natural and higher-quality video generation.

## Implementation

### 1. Optimized Flow Shift Parameters

We've implemented content-specific flow shift parameters that are optimized for different types of motion:

- **Balanced**: Default settings for general use (mu=calculated based on context, sigma=1.0)
- **Subtle Movement**: Less aggressive settings for subtle movements (reduced mu, increased sigma)
- **Dynamic Movement**: Slightly more aggressive for dynamic motion (increased mu, reduced sigma)
- **Talking**: Specialized for facial expressions and talking (reduced mu, slightly increased sigma)
- **Dance**: Fine-tuned for dance movements (slightly reduced mu)
- **Hand Detail**: Significantly less aggressive for hand detail (greatly reduced mu, increased sigma)

The implementation calculates the optimal parameters based on:
1. Content type (what kind of motion is being generated)
2. Detail level (standard, high, extreme)
3. Context length (frame sequence length)

### 2. Key Components

- **Mu Parameter**: Controls the magnitude of the flow shift. Lower values result in less aggressive diffusion schedules.
- **Sigma Parameter**: Controls the shape of the flow shift curve. Higher values result in smoother transitions.

### 3. Configuration System

The flow shift parameters are configured through presets in the UI:
- Each preset (Dance, Talking, Action, etc.) uses optimized flow parameters
- Advanced users can select different flow shift presets independently

## Technical Details

### Flux Time Shift Function

```python
def flux_time_shift(t, mu=1.15, sigma=1.0):
    """
    Applies time shift to the scheduler based on mu and sigma parameters.
    """
    return math.exp(mu) / (math.exp(mu) + (1 / t - 1) ** sigma)
```

### Optimized Parameter Calculation

```python
def calculate_optimized_mu(context_length, content_type="balanced", detail_level="standard"):
    """
    Calculate optimized mu parameter for different content types and detail levels.
    """
    # Base calculation
    x1, y1 = 256, 0.5
    x2, y2 = 4096, 1.15
    exp_max = 7.0
    
    # Calculate base mu
    k = (y2 - y1) / (x2 - x1)
    b = y1 - k * x1
    base_mu = k * context_length + b
    
    # Apply content-specific adjustments
    content_type_adjustments = {
        "balanced": 0.0,      # Default
        "subtle": -0.2,       # Less aggressive
        "dynamic": 0.1,       # More aggressive
        "talking": -0.15,     # Less aggressive
        "dance": -0.05,       # Slightly less aggressive
        "handdetail": -0.25,  # Much less aggressive
    }
    
    # Apply detail level adjustments
    detail_level_adjustments = {
        "standard": 0.0,      # Default
        "high": -0.1,         # Less aggressive
        "extreme": -0.2,      # Much less aggressive
    }
    
    # Calculate final mu
    final_mu = base_mu + content_type_adjustments[content_type] + detail_level_adjustments[detail_level]
    
    # Safety bounds
    final_mu = min(final_mu, math.log(exp_max))
    final_mu = max(final_mu, 0.3)
    
    return final_mu
```

## Usage in UI

The Flow Shift presets are exposed in the UI under "Advanced Generation Settings". Different presets are automatically applied when selecting video generation presets (Dance, Talking, etc.).

## Benefits

- **Improved Visual Quality**: More balanced schedulers lead to more natural and detailed results
- **Content-Specific Optimization**: Different types of motion benefit from different flow shift parameters
- **Detail Preservation**: Specialized presets for hand movements and detailed actions
- **No Model Retraining Required**: These improvements are achieved without changing the underlying model

## References

Zhang, L., & Agrawala, M. (2025). *Packing Input Frame Context in Next-Frame Prediction Models for Video Generation*. arXiv preprint arXiv:2504.12626.
