# Dose Rate Dependency Correction for ArcCheck Type 3 Diodes

Documentation: https://kkaan.github.io/drdcorrectionforAC/

## Overview

ArcCheck devices, particularly those utilizing Type 3 diodes, exhibit a significant dose rate dependency. This dependency can be problematic when measuring dose for Volumetric Modulated Arc Therapy (VMAT) delivered by Elekta linear accelerators. This repository provides tools to implement a correction methodology based on the findings published by Jäger et al. (2021) to mitigate these dose rate effects.

The primary goal is to correct the raw accumulated counts from the ArcCheck device to provide a more accurate representation of the delivered dose. This involves applying corrections for pulse rate (PR) and dose per pulse (DPP), followed by an optional intrinsic correction.

## Dose Correction Methodology

The correction process implemented in `src/corrections.py` follows the methodology proposed by Jäger et al. It involves two main correction factors: one for pulse rate dependency and another for dose per pulse dependency.

### 1. Preliminary Calculations

Before applying the Jäger corrections, several steps are performed:

1.  **Calculate Instantaneous Counts:** The instantaneous count (or count rate, proportional to dose rate) is determined by taking the difference between successive accumulated count readings from the `counts_accumulated_df`.
    ```
    count_df = counts_accumulated_df.diff()
    ```
    The first row of `count_df` will be NaN as a result of the `diff()` operation and is subsequently dropped.

2.  **Background Subtraction:** Background radiation values, obtained from the `bkrnd_and_calibration_df` (typically from an `.acm` file), are subtracted from the `count_df`.
    ```python
    background_values = bkrnd_and_calibration_df['Background'].values.astype(float)
    # ... (handling reference detector value)
    count_df = count_df.subtract(background_values_series, axis='columns')
    ```

3.  **Calibration Scaling:** The background-subtracted counts are then scaled using calibration factors, also obtained from `bkrnd_and_calibration_df`.
    ```python
    calibration_values = bkrnd_and_calibration_df['Calibration'].values.astype(float)
    # ... (handling reference detector value)
    count_df = count_df.multiply(calibration_values_series, axis='columns')
    ```
    This `count_df` now represents the calibrated dose rate per measurement interval for each detector.

### 2. Jäger Correction Factors (JCF)

The core of the correction lies in applying the Jäger Correction Factors. These factors are calculated separately for pulse rate and dose per pulse dependencies. The general form of the Jäger correction factor (JCF) is:

`JCF = c - a * exp(-b * D)`

Where:
*   `D` is the calibrated dose rate (represented by `count_df` in the code after background subtraction and calibration).
*   `a`, `b`, and `c` are coefficients specific to either the pulse rate or dose per pulse correction.

The corrected dose rate (`D_corrected`) is then calculated as:

`D_corrected = D / JCF`

#### a. Pulse Rate (PR) Correction

This correction addresses the dependency of the diode response on the pulse repetition frequency of the linear accelerator.

*   **Coefficients (as defined in `apply_jager_corrections`):**
    *   `a_pr = 0.035`
    *   `b_pr = 5.21 * 10^-5`
    *   `c_pr = 1`

*   **Formula Applied (`pulse_rate_correction` function):**
    `JCF_pr = c_pr - a_pr * exp(-b_pr * count_df)`
    `pr_corrected_count_df = count_df / JCF_pr`

The function then returns the sum of `pr_corrected_count_df` for each detector, representing the total corrected dose after PR correction.

#### b. Dose Per Pulse (DPP) Correction

This correction addresses the dependency of the diode response on the dose delivered by each individual radiation pulse.

*   **Coefficients (as defined in `apply_jager_corrections`):**
    *   `a_dpp = 0.0978`
    *   `b_dpp = 3.33 * 10^-5`
    *   `c_dpp = 1.011`

*   **Formula Applied (`dose_per_pulse_correction` function):**
    `JCF_dpp = c_dpp - a_dpp * exp(-b_dpp * count_df)`
    `dpp_corrected_count_df = count_df / JCF_dpp`

The function then returns the sum of `dpp_corrected_count_df` for each detector, representing the total corrected dose after DPP correction.

### 3. Combining Corrections

The `apply_jager_corrections` function calculates both `pr_corrected_count_sum` and `dpp_corrected_count_sum`. These represent two independently corrected versions of the total dose. The current implementation returns both in a DataFrame and subsequently an array, but typically one of these (or a combined/further processed version) would be chosen for final analysis.

### 4. Intrinsic Correction (Optional)

An additional correction, termed "Intrinsic Correction," can be applied. This correction is derived from the device's own calibration or reference data.

*   **Calculation (`get_intrinsic_corrections` function):**
    The intrinsic correction factor for each detector is calculated as:
    `Intrinsic_Correction_Factor = Corrected_Counts / Raw_Counts`
    This is performed element-wise, excluding header/footer rows and specific columns containing positional data.

*   **Application (`apply_jager_corrections` function):**
    If an `intrinsic_corrections` array (generated by `get_intrinsic_corrections`) is provided, it is applied *after* the Jäger corrections. The Jäger-corrected dose values (currently, the code applies it to an array formed from both PR and DPP corrected sums, which might need clarification based on intended use) are multiplied element-wise by the `numeric_intrinsic` factors.
    ```python
    # Assuming corrected_count_array contains Jäger-corrected values
    corrected_count_array *= numeric_intrinsic
    ```

## Implementation Details

The primary script for these corrections is `src/corrections.py`.

*   `apply_jager_corrections()`: Orchestrates the application of PR and DPP corrections and optionally the intrinsic correction.
*   `pulse_rate_correction()`: Calculates and applies the PR-specific Jäger correction.
*   `dose_per_pulse_correction()`: Calculates and applies the DPP-specific Jäger correction.
*   `get_intrinsic_corrections()`: Calculates the intrinsic correction factors from 'Corrected Counts' and 'Raw Counts' data.

Input data typically consists of:
*   `counts_accumulated_df`: A Pandas DataFrame with accumulated counts over time for each detector.
*   `bkrnd_and_calibration_df`: A Pandas DataFrame containing background and calibration values for each detector.
*   `array_data` (for intrinsic corrections): A dictionary containing NumPy arrays for 'Corrected Counts' and 'Raw Counts'.

The output is typically a NumPy array (or DataFrame) of corrected dose values.

## Reference

The correction methodology implemented is based on the work by:

Jäger, R., Kapsch, R. P., & Karger, C. P. (2021). A correction method for the dose rate dependent response of silicon diode arrays for measurements in pulsed photon beams with varying pulse frequency and pulse dose. *Physics in Medicine & Biology*, *66*(20), 205015.
(Available at: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8504598/ - *Note: Direct programmatic access to this URL may be restricted*)

This README aims to provide a comprehensive understanding of the dose correction formulas and their implementation within this project.
