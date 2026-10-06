"""
utils/feature_extraction.py

Rhythm-domain feature extraction operating directly on pre-extracted
mel spectrograms (mel_spec: np.ndarray, shape (128, 130)).
No audio loading, no re-extraction of spectrograms.
"""

from typing import Dict, Tuple
import numpy as np


# ----------------------------------------------------------------------
# 1. Temporal Energy
# ----------------------------------------------------------------------

def temporal_energy_envelope(mel_spec: np.ndarray) -> np.ndarray:
    """Frame-wise energy envelope (sum over mel bins per time frame)."""
    return np.sum(mel_spec, axis=0)


def temporal_energy_features(mel_spec: np.ndarray) -> Dict[str, float]:
    """Summary statistics of the temporal energy envelope."""
    env = temporal_energy_envelope(mel_spec)
    return {
        "energy_mean": float(np.mean(env)),
        "energy_std": float(np.std(env)),
        "energy_max": float(np.max(env)),
        "energy_min": float(np.min(env)),
        "energy_range": float(np.max(env) - np.min(env)),
        "energy_skew": float(_skewness(env)),
    }


def _skewness(x: np.ndarray) -> float:
    mu, sigma = np.mean(x), np.std(x) + 1e-10
    return float(np.mean(((x - mu) / sigma) ** 3))


# ----------------------------------------------------------------------
# 2. Spectral Flux
# ----------------------------------------------------------------------

def spectral_flux(mel_spec: np.ndarray) -> np.ndarray:
    """Frame-to-frame positive spectral change (half-wave rectified)."""
    diff = np.diff(mel_spec, axis=1)
    flux = np.sum(np.maximum(diff, 0), axis=0)
    return flux


def spectral_flux_features(mel_spec: np.ndarray) -> Dict[str, float]:
    flux = spectral_flux(mel_spec)
    return {
        "flux_mean": float(np.mean(flux)),
        "flux_std": float(np.std(flux)),
        "flux_max": float(np.max(flux)),
        "flux_sum": float(np.sum(flux)),
    }


# ----------------------------------------------------------------------
# 3. Autocorrelation
# ----------------------------------------------------------------------

def autocorrelation(signal: np.ndarray, max_lag: int = 64) -> np.ndarray:
    """Normalized autocorrelation of a 1D signal up to max_lag."""
    signal = signal - np.mean(signal)
    n = len(signal)
    max_lag = min(max_lag, n - 1)
    ac = np.array([
        np.sum(signal[: n - lag] * signal[lag:]) for lag in range(max_lag + 1)
    ])
    denom = ac[0] if ac[0] != 0 else 1e-10
    return ac / denom


def autocorrelation_features(mel_spec: np.ndarray, max_lag: int = 64) -> Dict[str, float]:
    env = temporal_energy_envelope(mel_spec)
    ac = autocorrelation(env, max_lag=max_lag)
    peak_lag = int(np.argmax(ac[1:]) + 1) if len(ac) > 1 else 0
    return {
        "ac_peak_lag": float(peak_lag),
        "ac_peak_value": float(ac[peak_lag]) if len(ac) > 1 else 0.0,
        "ac_mean": float(np.mean(ac)),
        "ac_std": float(np.std(ac)),
    }


# ----------------------------------------------------------------------
# 4. Temporal Entropy
# ----------------------------------------------------------------------

def temporal_entropy(mel_spec: np.ndarray) -> float:
    """Shannon entropy of the normalized temporal energy envelope."""
    env = temporal_energy_envelope(mel_spec)
    env = env - np.min(env) + 1e-10
    p = env / np.sum(env)
    entropy = -np.sum(p * np.log2(p + 1e-10))
    return float(entropy)


def frame_entropy(mel_spec: np.ndarray) -> np.ndarray:
    """Per-frame spectral entropy across mel bins."""
    spec = mel_spec - np.min(mel_spec, axis=0, keepdims=True) + 1e-10
    p = spec / np.sum(spec, axis=0, keepdims=True)
    entropy = -np.sum(p * np.log2(p + 1e-10), axis=0)
    return entropy


def temporal_entropy_features(mel_spec: np.ndarray) -> Dict[str, float]:
    fe = frame_entropy(mel_spec)
    return {
        "temporal_entropy": temporal_entropy(mel_spec),
        "frame_entropy_mean": float(np.mean(fe)),
        "frame_entropy_std": float(np.std(fe)),
    }


# ----------------------------------------------------------------------
# 5. Energy Modulation
# ----------------------------------------------------------------------

def energy_modulation_spectrum(mel_spec: np.ndarray) -> np.ndarray:
    """Magnitude spectrum of the energy envelope (modulation spectrum)."""
    env = temporal_energy_envelope(mel_spec)
    env = env - np.mean(env)
    spectrum = np.abs(np.fft.rfft(env))
    return spectrum


def energy_modulation_features(mel_spec: np.ndarray) -> Dict[str, float]:
    spectrum = energy_modulation_spectrum(mel_spec)
    dom_idx = int(np.argmax(spectrum[1:]) + 1) if len(spectrum) > 1 else 0
    return {
        "modulation_dominant_freq_bin": float(dom_idx),
        "modulation_dominant_mag": float(spectrum[dom_idx]) if len(spectrum) > 1 else 0.0,
        "modulation_energy": float(np.sum(spectrum ** 2)),
        "modulation_centroid": float(_spectral_centroid_1d(spectrum)),
    }


def _spectral_centroid_1d(spectrum: np.ndarray) -> float:
    idx = np.arange(len(spectrum))
    denom = np.sum(spectrum) + 1e-10
    return float(np.sum(idx * spectrum) / denom)


# ----------------------------------------------------------------------
# 6. Rhythm Histogram
# ----------------------------------------------------------------------

def rhythm_histogram(mel_spec: np.ndarray, max_lag: int = 64, n_bins: int = 16) -> np.ndarray:
    """Histogram of autocorrelation peak strengths across lag bins."""
    env = temporal_energy_envelope(mel_spec)
    ac = autocorrelation(env, max_lag=max_lag)
    ac = ac[1:]  # drop lag-0
    if len(ac) == 0:
        return np.zeros(n_bins)
    bin_edges = np.linspace(0, len(ac), n_bins + 1).astype(int)
    hist = np.array([
        np.sum(np.abs(ac[bin_edges[i]:bin_edges[i + 1]]))
        for i in range(n_bins)
    ])
    total = np.sum(hist) + 1e-10
    return hist / total


def rhythm_histogram_features(mel_spec: np.ndarray, max_lag: int = 64, n_bins: int = 16) -> Dict[str, float]:
    hist = rhythm_histogram(mel_spec, max_lag=max_lag, n_bins=n_bins)
    dominant_bin = int(np.argmax(hist))
    return {
        "rhythm_hist_dominant_bin": float(dominant_bin),
        "rhythm_hist_dominant_value": float(hist[dominant_bin]),
        "rhythm_hist_entropy": float(-np.sum(hist * np.log2(hist + 1e-10))),
        "rhythm_hist_std": float(np.std(hist)),
    }


# ----------------------------------------------------------------------
# 7. Tempogram Approximation
# ----------------------------------------------------------------------

def tempogram_approx(mel_spec: np.ndarray, win_size: int = 32, hop: int = 8,
                      max_lag: int = 32) -> np.ndarray:
    """
    Approximate tempogram: sliding-window autocorrelation of the
    energy envelope, stacked across windows. Shape: (max_lag+1, n_windows).
    """
    env = temporal_energy_envelope(mel_spec)
    n = len(env)
    columns = []
    start = 0
    while start + win_size <= n:
        window = env[start:start + win_size]
        ac = autocorrelation(window, max_lag=min(max_lag, win_size - 1))
        if len(ac) < max_lag + 1:
            ac = np.pad(ac, (0, max_lag + 1 - len(ac)))
        columns.append(ac)
        start += hop
    if not columns:
        return np.zeros((max_lag + 1, 1))
    return np.stack(columns, axis=1)


def tempogram_features(mel_spec: np.ndarray, win_size: int = 32, hop: int = 8,
                        max_lag: int = 32) -> Dict[str, float]:
    tg = tempogram_approx(mel_spec, win_size=win_size, hop=hop, max_lag=max_lag)
    mean_profile = np.mean(tg, axis=1)
    dominant_lag = int(np.argmax(mean_profile[1:]) + 1) if len(mean_profile) > 1 else 0
    return {
        "tempogram_dominant_lag": float(dominant_lag),
        "tempogram_stability": float(1.0 / (1e-10 + np.std(np.argmax(tg, axis=0)))),
        "tempogram_mean_energy": float(np.mean(tg)),
        "tempogram_var": float(np.var(tg)),
    }


# ----------------------------------------------------------------------
# 8. Estimated Onset Strength
# ----------------------------------------------------------------------

def onset_strength_envelope(mel_spec: np.ndarray) -> np.ndarray:
    """
    Estimated onset strength: half-wave rectified first difference of the
    temporal energy envelope (spectral-flux-like, but on summed energy).
    """
    env = temporal_energy_envelope(mel_spec)
    diff = np.diff(env)
    onset = np.maximum(diff, 0)
    return onset


def onset_strength_features(mel_spec: np.ndarray) -> Dict[str, float]:
    onset = onset_strength_envelope(mel_spec)
    if len(onset) == 0:
        return {
            "onset_mean": 0.0,
            "onset_std": 0.0,
            "onset_max": 0.0,
            "onset_peak_count": 0.0,
            "onset_density": 0.0,
        }
    threshold = np.mean(onset) + np.std(onset)
    peaks = _count_peaks_above_threshold(onset, threshold)
    return {
        "onset_mean": float(np.mean(onset)),
        "onset_std": float(np.std(onset)),
        "onset_max": float(np.max(onset)),
        "onset_peak_count": float(peaks),
        "onset_density": float(peaks / len(onset)),
    }


def _count_peaks_above_threshold(signal: np.ndarray, threshold: float) -> int:
    """Count local maxima above a threshold in a 1D signal."""
    count = 0
    for i in range(1, len(signal) - 1):
        if signal[i] > threshold and signal[i] >= signal[i - 1] and signal[i] >= signal[i + 1]:
            count += 1
    return count


# ----------------------------------------------------------------------
# Combined extraction for a single sample
# ----------------------------------------------------------------------

def extract_rhythm_features(mel_spec: np.ndarray) -> Dict[str, float]:
    """
    Run all rhythm feature groups on a single mel_spec sample
    (shape (128, 130)) and return a flat dict of features.
    """
    features: Dict[str, float] = {}
    features.update(temporal_energy_features(mel_spec))
    features.update(spectral_flux_features(mel_spec))
    features.update(autocorrelation_features(mel_spec))
    features.update(temporal_entropy_features(mel_spec))
    features.update(energy_modulation_features(mel_spec))
    features.update(rhythm_histogram_features(mel_spec))
    features.update(tempogram_features(mel_spec))
    features.update(onset_strength_features(mel_spec))
    return features