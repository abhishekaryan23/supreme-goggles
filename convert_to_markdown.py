import os
import sys
import subprocess
from pathlib import Path

class DocumentConverter:
    def __init__(self, input_file: str, output_dir: str):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.markdown_output = None
        self.media_dir = None

    def validate_environment(self):
        """Check prerequisites"""
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        if "pandoc" not in subprocess.getoutput("which pandoc"):
            raise EnvironmentError("Pandoc not installed or not in PATH")
        
        if "pdftotext" not in subprocess.getoutput("which pdftotext"):
            raise EnvironmentError("Poppler's pdftotext not installed or not in PATH")

    def convert(self):
        """Convert file using pandoc"""
        self.validate_environment()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        base_name = self.input_file.stem
        self.markdown_output = self.output_dir / f"{base_name}.md"
        self.media_dir = self.output_dir / f"{base_name}_media"
        
        try:
            pandoc_args = [
                "pandoc",
                str(self.input_file),  # Input file
                "-o",
                str(self.markdown_output),  # Output file
                "--extract-media",
                str(self.media_dir)  # Media directory
            ]
            result = subprocess.run(pandoc_args, capture_output=True, check=True)
            return True, result.stdout.decode()
        except subprocess.CalledProcessError as e:
            return False, e.stderr.decode()
        except Exception as e:
            return False, str(e)