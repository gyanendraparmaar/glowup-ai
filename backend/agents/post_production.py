"""Post-Production Agent — applies realism post-processing to generated images."""

import random
from io import BytesIO
from PIL import Image, ImageEnhance, ImageFilter
from mcp_servers.storage import StorageMCP

# Try to import piexif for EXIF injection; optional
try:
    import piexif
    HAS_PIEXIF = True
except ImportError:
    HAS_PIEXIF = False


class PostProductionAgent:
    """Agent that applies final post-processing to make the generated image
    indistinguishable from a real phone photo.

    Applies:
        1. Subtle lens vignette
        2. Sensor noise
        3. Micro color shift
        4. Slight lens softness
        5. JPEG compression at realistic quality
        6. iPhone EXIF metadata injection

    MCP servers used:
        - Storage MCP (save final image)
    """

    def __init__(self):
        self.storage = StorageMCP()

    async def process_and_save(
        self,
        image_bytes: bytes,
        output_path: str,
    ) -> str:
        """Apply all post-processing and save the result.

        Args:
            image_bytes: Raw generated image bytes
            output_path: Where to save the final JPEG

        Returns:
            Path to the saved file
        """
        final_bytes = self._make_it_look_real(image_bytes)

        # Save via Storage MCP
        import os
        filename = os.path.basename(output_path)
        subdir = os.path.dirname(output_path).replace("outputs/", "").replace("outputs\\", "")
        path = await self.storage.save(final_bytes, filename, subdir)
        return path

    def _make_it_look_real(self, image_bytes: bytes) -> bytes:
        """Apply all realism post-processing layers."""
        img = Image.open(BytesIO(image_bytes)).convert("RGB")

        # 1. Subtle lens vignette
        img = self._apply_vignette(img, strength=0.15)

        # 2. Sensor noise
        img = self._apply_sensor_noise(img, intensity=3)

        # 3. Micro color shift (real cameras aren't perfectly neutral)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(random.uniform(0.97, 1.03))

        # 4. Slight warmth shift
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(random.uniform(1.0, 1.02))

        # 5. Slight lens softness (real lenses aren't razor-sharp)
        img = img.filter(ImageFilter.GaussianBlur(radius=0.3))

        # 6. Save as realistic JPEG quality
        buffer = BytesIO()
        quality = random.randint(87, 93)
        img.save(buffer, format="JPEG", quality=quality)

        # 7. Inject iPhone EXIF metadata
        if HAS_PIEXIF:
            jpeg_bytes = self._inject_exif(buffer.getvalue())
        else:
            jpeg_bytes = buffer.getvalue()

        return jpeg_bytes

    def _apply_vignette(self, img: Image.Image, strength: float = 0.15) -> Image.Image:
        """Apply a subtle lens vignette (darkening at edges)."""
        import numpy as np

        w, h = img.size
        # Create distance-from-center mask
        Y, X = np.ogrid[:h, :w]
        cx, cy = w / 2, h / 2
        dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
        max_dist = np.sqrt(cx ** 2 + cy ** 2)
        dist = dist / max_dist

        # Vignette falloff
        vignette = 1 - (dist ** 2) * strength

        # Apply to image
        img_array = np.array(img).astype(float)
        for c in range(3):
            img_array[:, :, c] *= vignette
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)

        return Image.fromarray(img_array)

    def _apply_sensor_noise(self, img: Image.Image, intensity: int = 3) -> Image.Image:
        """Add subtle sensor noise like a real camera sensor."""
        import numpy as np

        img_array = np.array(img).astype(float)
        noise = np.random.normal(0, intensity, img_array.shape)
        img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        return Image.fromarray(img_array)

    def _inject_exif(self, jpeg_bytes: bytes) -> bytes:
        """Inject realistic iPhone EXIF metadata."""
        if not HAS_PIEXIF:
            return jpeg_bytes

        # Simulate iPhone 15 Pro Max EXIF
        exif_dict = {
            "0th": {
                piexif.ImageIFD.Make: b"Apple",
                piexif.ImageIFD.Model: b"iPhone 15 Pro Max",
                piexif.ImageIFD.Software: b"17.4.1",
                piexif.ImageIFD.Orientation: 1,
            },
            "Exif": {
                piexif.ExifIFD.FNumber: (178, 100),  # f/1.78
                piexif.ExifIFD.ExposureTime: (1, random.choice([60, 100, 125, 200])),
                piexif.ExifIFD.ISOSpeedRatings: random.choice([50, 64, 80, 100, 125]),
                piexif.ExifIFD.FocalLength: (6900, 1000),  # 6.9mm
                piexif.ExifIFD.FocalLengthIn35mmFilm: 24,
                piexif.ExifIFD.LensModel: b"iPhone 15 Pro Max back camera 6.9mm f/1.78",
                piexif.ExifIFD.ColorSpace: 1,  # sRGB
            },
        }

        exif_bytes = piexif.dump(exif_dict)
        return piexif.insert(exif_bytes, jpeg_bytes)
