# ADEPT Algorithm

## Overview

ADEPT (A Density-based Empirical likelihood ratio Test for the change-Point problem) is a fast, scalable, non-parametric method for single and multiple change point detection in time series data. In the context of this nanopore analysis pipeline, ADEPT is specifically adapted for analyzing short translocation events characterized by exponentially rising and falling pulses.

## Algorithm Background

### Traditional ADEPT (Change Point Detection)

The original ADEPT algorithm was developed as a statistical method for change point detection using:

- **Non-parametric approach**: No assumptions about underlying data distribution
- **Empirical likelihood ratio tests**: Based on density estimation to detect distributional changes
- **Computational efficiency**: Scales well with large datasets
- **Multiple change point detection**: Can simultaneously identify several change points
- **Robust performance**: Works across different types of distributional changes including mean, variance, and higher-order moments

### ADEPT in Nanopore Context

In this pipeline, ADEPT has been adapted for modeling fast nanopore translocation events that don't reach steady state. The implementation focuses on **pulse-like events** rather than traditional change point detection.

## Mathematical Models

### General Multistate ADEPT Model

The core mathematical model describes current as a function of time with multiple exponential transitions:

```
i(t) = i₀ - Σⱼ aⱼ × (1 - exp(-(t - μⱼ)/τⱼ)) × H(t - μⱼ)
```

Where:
- `i₀` = baseline current (typically high for inverted traces)
- `aⱼ` = positive amplitude (magnitude of current drop) for state j
- `μⱼ` = time delay for transition to state j
- `τⱼ` = time constant for state j
- `H(x)` = Heaviside step function

### Simplified 2-State ADEPT Model

For single translocation events, a specialized 2-state model is used:

```
i(t) = i₀ + a × [term₁ + term₂]
```

Where:
- `term₁ = (1 - exp(-((t-μ₁)/τᵣᵢₛₑ)^βᵣᵢₛₑ)) × H(t-μ₁)` (entry phase)
- `term₂ = (exp(-((t-μ₂)/τfₐₗₗ)^βfₐₗₗ) - 1) × H(t-μ₂)` (exit phase)

This model includes:
- **Separate time constants**: `τᵣᵢₛₑ` and `τfₐₗₗ` for entry and exit phases
- **Shape parameters**: `βᵣᵢₛₑ` and `βfₐₗₗ` for non-ideal exponential behavior
- **Two transitions**: `μ₁` (entry) and `μ₂` (exit) timing parameters

## Implementation Details

### Key Functions

#### `adept_multistate_model(t, *params)`
- **Purpose**: General multistate fitting function
- **Input**: Time vector and parameter list [i₀, a₁, μ₁, τ₁, a₂, μ₂, τ₂, ...]
- **Features**: 
  - Handles inverted traces (current drops)
  - Numerical stability protection
  - NaN/infinity handling

#### `adept_2state_model(t, i₀, a, μ₁, μ₂, τ_rise, τ_fall, β_rise, β_fall)`
- **Purpose**: Simplified model for single translocation events
- **Features**:
  - Separate rise/fall dynamics
  - Shape parameter support for non-exponential behavior
  - Optimized for fast events

#### `adept_analyze_event(data, event_idx, start, end, ...)`
- **Purpose**: Main analysis function for event characterization
- **Process**:
  1. Parameter estimation from event shape
  2. Time constant calculation (τ = time to 63.2% of peak)
  3. Shape parameter estimation from curve residuals
  4. Non-linear curve fitting with bounds
  5. Goodness-of-fit calculation (R², reduced χ²)

### Parameter Estimation Strategy

1. **Baseline Detection**: Uses normalized data (baseline ≈ 0)
2. **Peak Finding**: Identifies maximum deviation from baseline
3. **Time Constant Estimation**:
   - Rise time: Time to reach 63.2% of peak value
   - Fall time: Time to decay to 36.8% of peak value
4. **Shape Parameter Estimation**:
   - Compares actual curve to ideal exponential
   - β < 1: Slower than exponential
   - β > 1: Faster than exponential
   - Bounded between 0.3 and 3.0

### Fitting Process

1. **Initial Parameter Guesses**:
   - Amplitude from peak current
   - Timing from peak position
   - Time constants from curve analysis
2. **Bounded Optimization**:
   - Positive time constants (≥ 1e-6)
   - Physical transition times (0 to event duration)
   - Reasonable shape parameters (0.3 to 3.0)
3. **Fallback Strategy**:
   - If multistate fitting fails, try 2-state model
   - If all fitting fails, return basic event metrics

## Output Parameters

### Event Characterization
- `dwell_time`: Event duration in data points
- `dwell_time_ms`: Event duration in milliseconds
- `peak_current`: Maximum current value
- `event_area`: Integrated current relative to baseline
- `asymmetry`: Measure of rise/fall time asymmetry

### Fitted Parameters
- `baseline_current`: Fitted baseline level
- `amplitude`: Event amplitude
- `tau_rise`/`tau_fall`: Time constants
- `beta_rise`/`beta_fall`: Shape parameters
- `mu_1`/`mu_2`: Transition timing

### Quality Metrics
- `r_squared`: Coefficient of determination
- `reduced_chi_squared`: Normalized residual sum of squares
- `fitted_values`: Model prediction for visualization

## Applications in Nanopore Analysis

### Ideal Use Cases
- **Short events**: Pulse-like translocations that don't reach equilibrium
- **Fast transitions**: Events with characteristic exponential rise/fall
- **Single molecules**: Individual translocation events
- **High SNR data**: Clear signal above noise floor

### Advantages
- Models physical translocation dynamics
- Handles non-ideal exponential behavior
- Provides quantitative kinetic parameters
- Robust fitting with fallback strategies
- Suitable for automated analysis

### Limitations
- Assumes exponential kinetics
- May struggle with very noisy data
- Not suitable for multi-level step events
- Requires sufficient temporal resolution

## Integration with Pipeline

ADEPT analysis is triggered by the event classification system when events are determined to be:
- Short duration (typically < 50-100 data points)
- Pulse-like rather than step-like
- High signal-to-noise ratio
- Single-peak characteristics

The results integrate with the broader pipeline for:
- Comparative analysis with CUSUM results
- Statistical characterization across datasets
- Quality control and method validation
- Export to structured CSV format

## See Also
- [CUSUM.md](CUSUM.md) - For step-like event analysis
- `Event_classification.py` - For algorithm selection logic
- `main.py` - For configuration and pipeline integration