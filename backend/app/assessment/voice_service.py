import io
import numpy as np
import librosa
import soundfile as sf


def extract_voice_features(audio_bytes: bytes) -> dict:
    """
    Extract acoustic features from recorded voice audio.

    Parameters
    ----------
    audio_bytes : bytes
        Raw audio file bytes.

    Returns
    -------
    dict
        Extracted voice features.
    """

    if not audio_bytes:
        raise ValueError("Audio data is empty.")

    # Load audio directly from memory.
    audio_buffer = io.BytesIO(audio_bytes)

    try:
        audio, sample_rate = sf.read(
            audio_buffer,
            dtype="float32"
        )
    except Exception as exc:
        raise ValueError(
            f"Unable to read audio data: {exc}"
        ) from exc

    # Convert stereo audio to mono.
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)

    # Remove invalid values.
    audio = np.nan_to_num(audio)

    if len(audio) == 0:
        raise ValueError("Audio contains no samples.")

    # Normalize very large amplitudes.
    max_amplitude = np.max(np.abs(audio))

    if max_amplitude > 0:
        audio = audio / max_amplitude

    # ---------------------------------------------------------
    # 1. Duration
    # ---------------------------------------------------------
    duration = float(
        librosa.get_duration(
            y=audio,
            sr=sample_rate
        )
    )

    # ---------------------------------------------------------
    # 2. RMS Energy
    # ---------------------------------------------------------
    rms = librosa.feature.rms(
        y=audio
    )

    rms_mean = float(
        np.mean(rms)
    )

    rms_std = float(
        np.std(rms)
    )

    # ---------------------------------------------------------
    # 3. Zero Crossing Rate
    # ---------------------------------------------------------
    zcr = librosa.feature.zero_crossing_rate(
        audio
    )

    zcr_mean = float(
        np.mean(zcr)
    )

    # ---------------------------------------------------------
    # 4. Fundamental Frequency / Pitch
    # ---------------------------------------------------------
    try:
        f0, voiced_flag, voiced_prob = librosa.pyin(
            audio,
            fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7"),
            sr=sample_rate
        )

        valid_pitch = f0[
            np.isfinite(f0)
        ]

        if len(valid_pitch) > 0:
            pitch_mean = float(
                np.mean(valid_pitch)
            )

            pitch_std = float(
                np.std(valid_pitch)
            )

            pitch_min = float(
                np.min(valid_pitch)
            )

            pitch_max = float(
                np.max(valid_pitch)
            )

        else:
            pitch_mean = 0.0
            pitch_std = 0.0
            pitch_min = 0.0
            pitch_max = 0.0

    except Exception as exc:
        print(
            f"Pitch extraction warning: {exc}"
        )

        pitch_mean = 0.0
        pitch_std = 0.0
        pitch_min = 0.0
        pitch_max = 0.0

    # ---------------------------------------------------------
    # 5. MFCC
    # ---------------------------------------------------------
    mfcc = librosa.feature.mfcc(
        y=audio,
        sr=sample_rate,
        n_mfcc=13
    )

    mfcc_means = np.mean(
        mfcc,
        axis=1
    )

    # ---------------------------------------------------------
    # Build feature dictionary
    # ---------------------------------------------------------
    features = {
        "duration": duration,

        "rms_mean": rms_mean,
        "rms_std": rms_std,

        "zcr_mean": zcr_mean,

        "pitch_mean": pitch_mean,
        "pitch_std": pitch_std,
        "pitch_min": pitch_min,
        "pitch_max": pitch_max,
    }

    # Add MFCC means.
    for index, value in enumerate(
        mfcc_means,
        start=1
    ):
        features[f"mfcc_{index}"] = float(
            value
        )

    return features