"""Module to calculate MOS score between reference and degraded audio files."""

import numpy as np
import scipy.signal
from pesq import pesq
from pydub import AudioSegment


def load_audio_with_pydub(file_path, target_sr=16000):
    """
    Reemplazo de librosa.load usando Pydub.
    1. Carga audio (wav, mp3, m4a, etc).
    2. Convierte a Mono.
    3. Resamplea a 16000Hz (target_sr).
    4. Convierte a numpy array de float32.
    """
    try:
        # Cargar archivo (pydub detecta formato automáticamente)
        audio = AudioSegment.from_file(file_path)

        # Convertir a mono y resamplear
        audio = audio.set_channels(1).set_frame_rate(target_sr)

        # Convertir a array de numpy
        # Pydub maneja audio como enteros (int16 comúnmente),
        # PESQ y operaciones matemáticas prefieren float.
        samples = np.array(audio.get_array_of_samples())

        # Convertir a float32 para procesamiento
        samples = samples.astype(np.float32)

        return samples
    except (ValueError) as e:
        print(f"Error cargando audio con pydub: {e}")
        return np.array([], dtype=np.float32)


def synchronize_signals(ref, deg):
    """
    Algoritmo de alineación temporal (Igual que antes).
    """
    if len(ref) == 0 or len(deg) == 0:
        return ref, deg

    # Correlación cruzada
    correlation = scipy.signal.correlate(deg, ref, mode="full")
    lags = scipy.signal.correlation_lags(len(deg), len(ref), mode="full")
    lag = lags[np.argmax(correlation)]

    if lag > 0:
        deg_aligned = deg[lag:]
    else:
        ref = ref[abs(lag):]
        deg_aligned = deg

    min_len = min(len(ref), len(deg_aligned))
    return ref[:min_len], deg_aligned[:min_len]


def calculate_custom_mos(ref_path, deg_path):
    """Calcula MOS usando PESQ con preprocesamiento personalizado."""
    TARGET_SR = 16000  # pylint: disable=invalid-name

    try:
        # --- CAMBIO AQUÍ: Usamos la nueva función ---
        ref_audio = load_audio_with_pydub(ref_path, target_sr=TARGET_SR)
        deg_audio = load_audio_with_pydub(deg_path, target_sr=TARGET_SR)

        if len(ref_audio) == 0 or len(deg_audio) == 0:
            raise ValueError("Audio vacío o corrupto")

        # 2. Normalización de Energía (Volumen)
        # Importante: Pydub devuelve valores altos (ej. 32000),
        # al dividir por el máximo, normalizamos a rango -1.0 a 1.0
        max_ref = np.max(np.abs(ref_audio))
        max_deg = np.max(np.abs(deg_audio))

        if max_ref > 0:
            ref_audio = ref_audio / max_ref
        if max_deg > 0:
            deg_audio = deg_audio / max_deg

        # 3. Alineación Temporal
        ref_sync, deg_sync = synchronize_signals(ref_audio, deg_audio)

        # Validación extra de longitud para PESQ
        if len(ref_sync) < 100:  # PESQ falla con audios muy cortos
            return None

        # 4. Cálculo PESQ (Wideband)
        raw_pesq_score = pesq(TARGET_SR, ref_sync, deg_sync, "wb")

        # 5. Mapeo a Escala MOS 1-5
        mos_score = max(1.0, min(5.0, raw_pesq_score))

        quality_label = "Malo"
        if mos_score > 4.2:
            quality_label = "Excelente"
        elif mos_score > 3.6:
            quality_label = "Bueno"
        elif mos_score > 3.0:
            quality_label = "Aceptable"
        elif mos_score > 2.0:
            quality_label = "Pobre"

        return {
            "mos_score": round(mos_score, 2),
            "raw_pesq": round(raw_pesq_score, 3),
            "quality": quality_label,
            "latency_sample_lag": int(len(ref_audio) - len(ref_sync)),
        }

    except (ValueError) as e:
        print(f"Error en cálculo MOS: {e}")
        return None
