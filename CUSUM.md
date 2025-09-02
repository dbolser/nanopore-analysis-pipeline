# CUSUM Algorithm

## Overview

CUSUM (Cumulative Sum) is a sequential analysis technique introduced by E.S. Page in 1954, originally designed for statistical process control and change point detection. In this nanopore analysis pipeline, CUSUM is adapted for detecting and analyzing complex multi-level translocation events that exhibit step-like behavior with discrete state transitions.

## Algorithm Background

### Historical Foundation

The CUSUM algorithm was first published by E.S. Page in *Biometrika* (1954) as a method for monitoring changes in the underlying parameters of a process over time. Page defined the Average Run Length (A.R.L.) metric as "the expected number of articles sampled before action is taken," which remains a key performance measure today.

### Core Principle

CUSUM involves the calculation of a cumulative sum of deviations from a reference value. Unlike traditional control charts that focus on individual data points, CUSUM accumulates information over time, making it particularly sensitive to small but persistent shifts that might otherwise go unnoticed.

### Mathematical Foundation

The CUSUM statistic is calculated as:

```
S⁺ₙ = max(0, S⁺ₙ₋₁ + (xₙ - μ₀) - k)
S⁻ₙ = max(0, S⁻ₙ₋₁ - (xₙ - μ₀) - k)
```

Where:
- `S⁺ₙ` detects upward shifts
- `S⁻ₙ` detects downward shifts  
- `xₙ` is the current observation
- `μ₀` is the reference level
- `k` is the reference value (allowable slack)

A change is detected when either `S⁺ₙ > h` or `S⁻ₙ > h`, where `h` is the decision threshold.

## Key Advantages

### Small Shift Detection
CUSUM charts are specifically designed for detecting small process shifts that traditional Shewhart control charts might miss. The retention of memory from recent results allows CUSUM to detect even small persistent shifts in rates.

### Statistical Optimality
When the probability distributions before and after a change are known, CUSUM is an optimal procedure due to its short detection delay and minimal false alarm rate.

### Memory Retention
Each CUSUM value summarizes what is happening in the current and all previous points, providing superior sensitivity to gradual process changes.

## Implementation in Nanopore Analysis

### Core Detection Function

#### `cusum_detector(data, k=0.5, h=3, min_distance=3, adaptive_threshold=True, window_size=50, noise_std=None)`

**Parameters:**
- `k`: Reference value multiplier (shift detection sensitivity)
- `h`: Decision threshold multiplier (detection threshold)
- `min_distance`: Minimum separation between detected change points
- `adaptive_threshold`: Use local noise estimation
- `window_size`: Window for rolling statistics
- `noise_std`: Noise standard deviation for thresholding

**Algorithm Steps:**
1. **Initialization**: Set up CUSUM statistics S⁺ and S⁻
2. **Noise Estimation**: Calculate or use provided noise standard deviation
3. **Adaptive Thresholding**: Compute rolling standard deviation using pandas/numpy
4. **CUSUM Loop**: For each data point:
   - Calculate deviation from reference level
   - Update CUSUM statistics
   - Check against threshold
   - Detect change points with minimum distance constraint
   - Reset statistics after detection
5. **Refinement**: Improve change point locations by finding maximum gradients

### Level Grouping and Analysis

#### `group_levels(data, change_points, min_level_points=5)`

Groups data segments between change points into discrete levels:

**Level Characterization:**
- `current`: Median current value (robust to outliers)
- `std`: Standard deviation within level
- `stability`: Relative noise metric (std/current)
- `duration`: Number of data points
- `dwell_time_ms`: Duration in milliseconds

**Level Merging:** Adjacent levels with similar current values (within noise threshold) are automatically merged to reduce over-segmentation.

#### `identify_carrier_levels(levels, noise_std, min_carrier_fraction=0.05, min_level_separation=2.0)`

Identifies significant "carrier" levels based on:
- **Duration**: Must occupy minimum fraction of event
- **Separation**: Must be distinct from other carriers by noise-based threshold
- **Stability**: Preference for levels with low noise

### Sub-peak Detection

#### `detect_subpeaks(event_data, carrier_level, ...)`

For each carrier level, detects transient sub-peaks using `scipy.signal.find_peaks`:

**Detection Criteria:**
- **Height**: Minimum amplitude above carrier level (typically 2×noise_std)
- **Prominence**: Peak must stand out from local baseline
- **Distance**: Minimum separation between peaks
- **Width**: Minimum peak width in data points

**Sub-peak Characterization:**
- Peak current and amplitude relative to carrier
- Dwell time and area above carrier
- Prominence and significance metrics
- Temporal position within event

## Adaptive Parameter Selection

The implementation uses adaptive parameters based on event characteristics:

### Short Events (< 50 points)
```python
k_value = 0.4        # High sensitivity
h_value = 4.5        # Moderate threshold  
min_dist = 2         # Close spacing allowed
adaptive_threshold = False  # Insufficient data for rolling stats
```

### Medium Events (50-200 points)
```python
k_value = 0.5        # Balanced sensitivity
h_value = 5.0        # Standard threshold
min_dist = 4         # Moderate spacing
adaptive_threshold = True   # Enable local noise estimation
```

### Long Events (> 200 points)
```python
k_value = 0.6        # Conservative sensitivity
h_value = 5.5        # Higher threshold
min_dist = 5         # Wider spacing
adaptive_threshold = True   # Full adaptive mode
```

## Main Analysis Function

### `cusum_analyze_event(data_normalised, event_start_idx, event_end_idx, baseline_current, noise_std)`

**Complete Analysis Pipeline:**

1. **Parameter Selection**: Adaptive parameters based on event length
2. **Change Point Detection**: Apply CUSUM algorithm
3. **Level Identification**: Group data into discrete levels
4. **Carrier Level Selection**: Identify significant current levels
5. **Sub-peak Detection**: Find transient features within carriers
6. **Metrics Calculation**: Compute event characterization parameters

**Output Parameters:**

### Event Metrics
- `dwell_time_ms`: Total event duration
- `carrier_current`: Weighted average of carrier levels
- `event_area`: Integrated current relative to baseline
- `num_levels`: Number of detected carrier levels
- `num_subpeaks`: Number of detected sub-peaks

### Detailed Analysis
- `carrier_levels`: List of detected current levels with properties
- `subpeaks`: List of transient peaks with characterization
- `change_points`: Raw change point indices
- `event_statistics`: Mean, median, std, min, max values

## Applications in Nanopore Analysis

### Ideal Use Cases
- **Multi-level events**: Translocations with discrete current states
- **Long duration events**: Events with sufficient data for level detection
- **Step-like transitions**: Clear transitions between current levels
- **Complex molecules**: Multi-domain proteins or DNA secondary structures

### Advantages
- **Change point detection**: Identifies transition boundaries objectively
- **Multi-level analysis**: Characterizes multiple current states
- **Sub-peak detection**: Finds transient features within levels
- **Adaptive parameters**: Adjusts sensitivity based on event characteristics
- **Noise robustness**: Uses local noise estimation and filtering

### Limitations
- **Minimum duration**: Requires sufficient data points for reliable detection
- **Computational cost**: More intensive than simple threshold methods
- **Parameter sensitivity**: Performance depends on k, h parameter selection
- **Over-segmentation risk**: May detect spurious change points in noisy data

## Statistical Performance

### Detection Metrics
- **Sensitivity**: Ability to detect true change points
- **Specificity**: Avoidance of false change point detection
- **Detection delay**: Time between actual change and detection
- **False alarm rate**: Frequency of spurious detections

### Quality Control
The implementation includes multiple validation steps:
- Minimum level duration requirements
- Level merging for similar current values
- Significance filtering for sub-peaks
- Adaptive thresholding based on local noise

## Integration with Pipeline

CUSUM analysis is selected when events exhibit:
- Long duration (typically > 50-100 data points)
- Step-like rather than pulse-like behavior
- Multiple current levels or complex structure
- Sufficient signal-to-noise ratio for level detection

The results complement ADEPT analysis by handling different event types and providing detailed multi-level characterization for complex translocation events.

## See Also
- [ADEPT.md](ADEPT.md) - For pulse-like event analysis
- `Event_classification.py` - For algorithm selection logic  
- `main.py` - For configuration and pipeline integration

## References
1. Page, E.S. (1954). Continuous Inspection Schemes. *Biometrika*, 41(1/2), 100-115.
2. OpenNanopore project concepts and implementations
3. Scipy signal processing documentation for peak detection