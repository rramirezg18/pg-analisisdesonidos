"""
Módulo de inferencia para el CNN de detección de anomalías.
Usar como servicio singleton en FastAPI.

Uso:
    from cnn_service import CNNService
    
    # Al arrancar la app (lifespan)
    cnn = CNNService("modelos/modelo_cnn_v1.keras", "modelos/model_config.json")
    
    # En el endpoint
    resultado = cnn.predecir(audio_bytes, cilindraje=150)
    # → {"clase": "anomalia", "confianza": 87.3, "valor_raw": 0.9365}
"""

import numpy as np
import librosa
import json
import io
from tensorflow import keras


class CNNService:
    """Singleton que carga el modelo CNN y ejecuta inferencias."""
    
    def __init__(self, modelo_path: str, config_path: str):
        """Carga el modelo y la configuración una sola vez."""
        with open(config_path, "r") as f:
            self.config = json.load(f)
        
        self.mel_config = self.config["preprocesamiento_audio"]
        self.clases = self.config["clases"]
        self.input_shape = tuple(self.config["input_espectrograma"]["shape"])
        
        self.model = keras.models.load_model(modelo_path)
        print(f"✓ Modelo CNN cargado: {self.config['version']}")
        print(f"  Accuracy de validación: {self.config['accuracy_validacion']}%")
    
    def _audio_a_espectrograma(self, audio_bytes: bytes) -> np.ndarray:
        """Convierte bytes de audio a espectrograma de Mel normalizado."""
        cfg = self.mel_config
        
        # Cargar audio desde bytes
        y, sr = librosa.load(
            io.BytesIO(audio_bytes),
            sr=cfg["sample_rate"],
            duration=cfg["duration_seconds"]
        )
        
        # Pad si es más corto
        target_len = int(cfg["sample_rate"] * cfg["duration_seconds"])
        if len(y) < target_len:
            y = np.pad(y, (0, target_len - len(y)))
        else:
            y = y[:target_len]
        
        # Generar espectrograma de Mel
        mel = librosa.feature.melspectrogram(
            y=y, sr=cfg["sample_rate"],
            n_fft=cfg["n_fft"], hop_length=cfg["hop_length"],
            n_mels=cfg["n_mels"], fmin=cfg["fmin"], fmax=cfg["fmax"]
        )
        
        # Convertir a dB
        if cfg.get("normalize_db", True):
            mel = librosa.power_to_db(mel, ref=np.max)
        
        # Normalizar a [0, 1]
        mel_min, mel_max = mel.min(), mel.max()
        if mel_max - mel_min > 0:
            mel = (mel - mel_min) / (mel_max - mel_min)
        else:
            mel = np.zeros_like(mel)
        
        # Ajustar time_steps al tamaño esperado
        expected_t = self.input_shape[1]
        if mel.shape[1] < expected_t:
            mel = np.pad(mel, ((0, 0), (0, expected_t - mel.shape[1])))
        elif mel.shape[1] > expected_t:
            mel = mel[:, :expected_t]
        
        return mel
    
    def _normalizar_cilindraje(self, cilindraje: int) -> float:
        """Normaliza el cilindraje al rango [0, 1]."""
        return (cilindraje - 125) / 75.0
    
    def predecir(self, audio_bytes: bytes, cilindraje: int) -> dict:
        """
        Ejecuta la inferencia completa.
        
        Args:
            audio_bytes: contenido del archivo de audio (wav/mp3/m4a)
            cilindraje: 125, 150 o 200
        
        Returns:
            {"clase": "normal"|"anomalia", "confianza": float, "valor_raw": float}
        """
        mel = self._audio_a_espectrograma(audio_bytes)
        
        spec_input = mel[np.newaxis, ..., np.newaxis]  # (1, 128, T, 1)
        cil_input = np.array([[self._normalizar_cilindraje(cilindraje)]], dtype=np.float32)
        
        raw = float(self.model.predict([spec_input, cil_input], verbose=0)[0][0])
        
        clase = "anomalia" if raw >= 0.5 else "normal"
        confianza = min(round(abs(raw - 0.5) * 200, 2), 100.0)
        
        return {"clase": clase, "confianza": confianza, "valor_raw": round(raw, 6)}
    
    def generar_espectrograma_png(self, audio_bytes: bytes, output_path: str) -> str:
        """Genera y guarda el espectrograma como imagen PNG."""
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        
        cfg = self.mel_config
        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=cfg["sample_rate"], duration=cfg["duration_seconds"])
        
        mel = librosa.feature.melspectrogram(
            y=y, sr=sr, n_fft=cfg["n_fft"], hop_length=cfg["hop_length"],
            n_mels=cfg["n_mels"], fmin=cfg["fmin"], fmax=cfg["fmax"]
        )
        mel_db = librosa.power_to_db(mel, ref=np.max)
        
        fig, ax = plt.subplots(1, 1, figsize=(8, 4))
        librosa.display.specshow(mel_db, sr=sr, hop_length=cfg["hop_length"],
                                  x_axis="time", y_axis="mel", ax=ax,
                                  fmin=cfg["fmin"], fmax=cfg["fmax"])
        plt.tight_layout()
        fig.savefig(output_path, dpi=100, bbox_inches="tight")
        plt.close(fig)
        return output_path
