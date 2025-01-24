# processing/base_processor.py
import numpy as np
import cv2
from PyQt5.QtCore import QThread, pyqtSignal

class FourierBase:
    def __init__(self):
        pass

    def compute_fft(self, image):
        """Compute the FFT and shift it."""
        fft = np.fft.fft2(image)
        return np.fft.fftshift(fft)

    def extract_components(self, fft_shift):
        """Extract magnitude, phase, real, and imaginary components."""
        return {
            "Magnitude": np.abs(fft_shift),
            "Phase": np.angle(fft_shift),
            "Real": np.real(fft_shift),
            "Imaginary": np.imag(fft_shift)
        }

    def reconstruct_fft(self, component_type, component_data):
        """Reconstruct the complex FT based on the selected component type."""
        if component_type in ["FT Magnitude", "FT Phase"]:
            return component_data["Magnitude"] * np.exp(1j * component_data["Phase"])
        elif component_type in ["FT Real", "FT Imaginary"]:
            return component_data["Real"] + 1j * component_data["Imaginary"]
        else:
            raise ValueError(f"Unknown component type: {component_type}")

    def inverse_fft(self, mixed_ft):
        """Apply inverse FFT to get the result."""
        return np.fft.ifft2(np.fft.ifftshift(mixed_ft)).real