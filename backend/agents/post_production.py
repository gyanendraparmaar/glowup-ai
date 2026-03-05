from __future__ import annotations
"""Post-Production Agent — applies realism post-processing to generated images."""

import logging
import random
from io import BytesIO
from PIL import Image, ImageEnhance, ImageFilter
from mcp_servers.storage import StorageMCP
from config import config

# Try to import piexif for EXIF injection; optional
try:
    import piexif
    HAS_PIEXIF = True
except ImportError:
    HAS_PIEXIF = False

logger = logging.getLogger("glowup.post_production")


class PostProductionAgent:
    """Agent that applies final post-processing to make the generated image
    indistinguishable from a real phone photo.

    Applies:
        1. Subtle lens vignette
        2. Sensor noise
        3. Micro color shift
        4. Slight lens softness
        5. JPEG compression at realistic quality
        6. EXIF metadata (stripped by default for privacy)

    MCP servers used:
        - Storage MCP (save final image)
    """

    def __init__(self):
        self.storage = StorageMCP()

    async def process_and_save(
        self,
        image_bytes: bytes,
        output_path: str,
        original_path: str | None = None,
    ) -> str:
        """Apply all post-processing and save the result.

        Args:
            image_bytes: Raw generated image bytes
            output_path: Where to save the final JPEG
            original_path: Optional path to original photo (to preserve EXIF)

        Returns:
            Path to the saved file
        """
        final_bytes = self._make_it_look_real(image_bytes, original_path)

        # Save via Storage MCP
        import os
        filename = os.path.basename(output_path)
        subdir = os.path.dirname(output_path).replace("outputs/", "").replace("outputs\\", "")
        path = await self.storage.save(final_bytes, filename, subdir)
        logger.info("post_production.saved path=%s size_kb=%d", path, len(final_bytes) // 1024)
        return path

    def _make_it_look_real(self, image_bytes: bytes, original_path: str | None = None) -> bytes:
        """Apply all realism post-processing layers."""
        img = Image.open(BytesIO(image_bytes)).convert("RGB")

        # 1. Subtle lens vignette
        img = self._apply_vignette(img, strength=config.VIGNETTE_STRENGTH)

        # 2. Sensor noise
        img = self._apply_sensor_noise(img, intensity=config.SENSOR_NOISE_INTENSITY)

        # 3. Micro color shift (real cameras aren't perfectly neutral)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(random.uniform(config.COLOR_SHIFT_MIN, config.COLOR_SHIFT_MAX))

        # 4. Slight warmth shift
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(random.uniform(config.WARMTH_SHIFT_MIN, config.WARMTH_SHIFT_MAX))

        # 5. Slight lens softness (real lenses aren't razor-sharp)
        img = img.filter(ImageFilter.GaussianBlur(radius=config.LENS_BLUR_RADIUS))

        # 6. Save as realistic JPEG quality
        buffer = BytesIO()
        quality = random.randint(config.JPEG_QUALITY_MIN, config.JPEG_QUALITY_MAX)
        img.save(buffer, format="JPEG", quality=quality)

        # 7. Handle EXIF metadata
        jpeg_bytes = buffer.getvalue()
        if HAS_PIEXIF and original_path:
            jpeg_bytes = self._copy_exif_from_original(jpeg_bytes, original_path)

        return jpeg_bytes

    def _apply_vignette(self, img: Image.Image, strength: float = 0.15) -> Image.Image:
        """Apply a subtle lens vignette (darkening at edges)."""
        import numpy as np

        w, h = img.size
        Y, X = np.ogrid[:h, :w]
        cx, cy = w / 2, h / 2
        dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
        max_dist = np.sqrt(cx ** 2 + cy ** 2)
        dist = dist / max_dist

        vignette = 1 - (dist ** 2) * strength

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

    def _copy_exif_from_original(self, jpeg_bytes: bytes, original_path: str) -> bytes:
        """Copy EXIF from the original photo if available, otherwise strip EXIF."""
        if not HAS_PIEXIF:
            return jpeg_bytes

        try:
            original_exif = piexif.load(original_path)
            # Only copy basic camera info, strip GPS/location data for privacy
            if "GPS" in original_exif:
                original_exif["GPS"] = {}
            exif_bytes = piexif.dump(original_exif)
            return piexif.insert(exif_bytes, jpeg_bytes)
        except Exception:
            # If original has no EXIF or it fails, return without EXIF (privacy-safe default)
            logger.debug("No EXIF to copy from original, returning clean JPEG")
            return jpeg_bytes
