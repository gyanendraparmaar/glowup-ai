"""Storage MCP Server — local filesystem storage for the demo."""

import os
import zipfile
from io import BytesIO
from config import config


class StorageMCP:
    """MCP-style tool server for file storage.

    For the demo, this just saves to the local filesystem.
    In production, this would use Google Cloud Storage with signed URLs.
    """

    def __init__(self):
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    async def save(
        self,
        data: bytes,
        filename: str,
        subdir: str = "",
    ) -> str:
        """Save bytes to local filesystem. Returns the file path."""
        if subdir:
            dir_path = os.path.join(config.OUTPUT_DIR, subdir)
            os.makedirs(dir_path, exist_ok=True)
            path = os.path.join(dir_path, filename)
        else:
            path = os.path.join(config.OUTPUT_DIR, filename)

        with open(path, "wb") as f:
            f.write(data)
        return path

    async def load(self, path: str) -> bytes:
        """Load file from filesystem."""
        with open(path, "rb") as f:
            return f.read()

    async def create_zip(
        self, file_paths: list[str], output_name: str
    ) -> str:
        """Create a ZIP of multiple files. Returns path to ZIP file."""
        zip_path = os.path.join(config.OUTPUT_DIR, output_name)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in file_paths:
                zf.write(path, os.path.basename(path))
        return zip_path
