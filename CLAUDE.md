# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

This project uses `uv` for dependency management:

```bash
# Install dependencies
uv sync

# Run the analysis pipeline
uv run python main.py

# Add new dependencies
uv add <package>

# Add development dependencies (testing/linting)
uv add --dev ruff pytest

# Run linting and formatting (ruff handles both)
uv run ruff check .
uv run ruff format .

# Run tests
uv run pytest
```

Note: Ruff is both a linter and formatter that replaces multiple tools (flake8, black, isort, etc.)

## Project Architecture

This is a scientific Python pipeline for analyzing nanopore translocation events. The architecture follows a modular workflow:

### Core Pipeline Flow (main.py:10-240)
1. **Data Loading** → 2. **Preprocessing** → 3. **Event Detection** → 4. **Classification** → 5. **Analysis** → 6. **Output**

### Key Modules

- **Data_Load_Preprocessing.py**: Handles ABF file import via pyabf, signal filtering (Butterworth), downsampling, and baseline correction using Asymmetric Least Squares (ALS), Savitzky-Golay, or moving average methods.

- **Event_Detection.py**: Implements Gaussian noise characterization and threshold-based event detection. Uses `stdv_gaus()` to fit noise distribution and `detect_events()` for boundary determination via Signal Overlap (SO) or FWHM methods.

- **Event_classification.py**: Rule-based classifier that categorizes events as ADEPT (short, pulse-like) or CUSUM (long, multi-level) based on duration, SNR, and steady-state analysis using `_detect_steady_state()`.

- **ADEPT.py**: Non-linear curve fitting for short translocation events using multistate exponential models. Core function: `adept_multistate_model()` with Heaviside step functions.

- **CUSUM.py**: Statistical change-point detection for complex multi-level events. Implements adaptive thresholding and peak detection to identify discrete state transitions.

- **Visualisation_Output.py**: Generates QC plots and exports structured CSV results via `save_event_params_csv()`.

### Configuration
All analysis parameters are configured in `main.py` including:
- File paths and data loading methods (ABF vs pre-processed numpy)
- Signal processing (filtering, downsampling, baseline correction)
- Detection thresholds and classification criteria
- Output settings and debugging options

### Data Flow
The pipeline expects .abf files (Axon Binary Format) from electrophysiology experiments or pre-processed .npy files. Events are detected, classified into two algorithmic approaches, analyzed with appropriate models, and results saved to CSV with optional interactive plotting.