"""Servicio de inferencia del modelo CNN de detección de anomalías.

Se instancia una sola vez al arrancar la app (singleton) y se reutiliza en cada
request. Todo el preprocesamiento (mel-espectrograma) se hace aquí con librosa,
usando EXACTAMENTE los parámetros de model_config.json para que coincidan con el
entrenamiento. Si esos parámetros no coinciden, la predicción es incorrecta.
"""

import io
import json
import logging

import librosa
import numpy as np
from tensorflow import keras

logger = logging.getLogger(__name__)


class CNNService:
    def __init__(self, modelo_path: str, config_path: str):
        with open(config_path, "r") as f:
            self.config = json.load(f)

        self.mel_config = self.config["preprocesamiento_audio"]
        self.clases = self.config["clases"]
        self.input_shape = tuple(self.config["input_espectrograma"]["shape"])

        self.model = keras.models.load_model(modelo_path)
        logger.info(
            "Modelo CNN cargado: %s (accuracy val: %s%%)",
            self.config["version"],
            self.config["accuracy_validacion"],
        )

    @property
    def version(self) -> str:
        return self.config["version"]

    def _audio_a_espectrograma(self, audio_bytes: bytes) -> np.ndarray:
        cfg = self.mel_config

        y, _ = librosa.load(
            io.BytesIO(audio_bytes),
            sr=cfg["sample_rate"],
            duration=cfg["duration_seconds"],
        )

        # Recortar/rellenar a la duración exacta esperada por el modelo.
        target_len = int(cfg["sample_rate"] * cfg["duration_seconds"])
        if len(y) < target_len:
            y = np.pad(y, (0, target_len - len(y)))
        else:
            y = y[:target_len]

        mel = librosa.feature.melspectrogram(
            y=y,
            sr=cfg["sample_rate"],
            n_fft=cfg["n_fft"],
            hop_length=cfg["hop_length"],
            n_mels=cfg["n_mels"],
            fmin=cfg["fmin"],
            fmax=cfg["fmax"],
        )

        if cfg.get("normalize_db", True):
            mel = librosa.power_to_db(mel, ref=np.max)

        mel_min, mel_max = mel.min(), mel.max()
        if mel_max - mel_min > 0:
            mel = (mel - mel_min) / (mel_max - mel_min)
        else:
            mel = np.zeros_like(mel)

        # Ajustar el eje temporal al ancho exacto que espera el modelo.
        expected_t = self.input_shape[1]
        if mel.shape[1] < expected_t:
            mel = np.pad(mel, ((0, 0), (0, expected_t - mel.shape[1])))
        elif mel.shape[1] > expected_t:
            mel = mel[:, :expected_t]

        return mel

    def _normalizar_cilindraje(self, cilindraje: int) -> float:
        return (cilindraje - 125) / 75.0

    def predecir(self, audio_bytes: bytes, cilindraje: int) -> dict:
        """audio_bytes + cilindraje -> {clase, confianza, valor_raw}."""
        mel = self._audio_a_espectrograma(audio_bytes)

        spec_input = mel[np.newaxis, ..., np.newaxis]  # (1, 128, T, 1)
        cil_input = np.array(
            [[self._normalizar_cilindraje(cilindraje)]], dtype=np.float32
        )

        raw = float(self.model.predict([spec_input, cil_input], verbose=0)[0][0])

        clase = "anomalia" if raw >= 0.5 else "normal"
        confianza = min(round(abs(raw - 0.5) * 200, 2), 100.0)

        return {"clase": clase, "confianza": confianza, "valor_raw": round(raw, 6)}

    @staticmethod
    def _magma(x: np.ndarray) -> np.ndarray:
        """Colormap tipo 'magma' por interpolación de anclas. x en [0, 1]."""
        stops = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0])
        r = np.array([0, 40, 101, 159, 212, 245, 252])
        g = np.array([0, 11, 21, 42, 72, 125, 253])
        b = np.array([4, 84, 110, 99, 66, 21, 191])
        rgb = np.stack(
            [np.interp(x, stops, r), np.interp(x, stops, g), np.interp(x, stops, b)],
            axis=-1,
        )
        return rgb.astype(np.uint8)

    def generar_espectrograma_png(self, audio_bytes: bytes, output_path: str) -> str:
        """Guarda como PNG el MISMO espectrograma que entra al modelo.

        Reutiliza _audio_a_espectrograma (matriz normalizada [0,1], forma
        (n_mels, T)) para que la imagen sea idéntica a la entrada de la CNN.
        Usa Pillow (sin matplotlib) para mantener la imagen liviana.
        """
        from PIL import Image

        mel = self._audio_a_espectrograma(audio_bytes)

        # Frecuencias bajas abajo (como en un espectrograma clásico).
        img = self._magma(np.flipud(mel))
        imagen = Image.fromarray(img, mode="RGB")

        # Escalar para que se vea nítido en pantalla sin perder la relación.
        alto_destino = 256
        escala = alto_destino / imagen.height
        imagen = imagen.resize(
            (int(imagen.width * escala), alto_destino), Image.BILINEAR
        )
        imagen.save(output_path, format="PNG")
        return output_path
