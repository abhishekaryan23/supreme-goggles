import os
import sys
import subprocess
import shutil
from pathlib import Path
import pymupdf

class DocumentConverter:
    def __init__(self, input_file: str, output_dir: str):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.markdown_output = None
        self.media_dir = None

    def validate_environment(self):
        """Validate prerequisites based on input file type."""
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        if self.input_file.suffix.lower() == ".pdf":
            try:
                import pymupdf
            except ImportError:
                raise EnvironmentError("PyMuPDF not installed. Install with 'pip install pymupdf'")
        else:
            if "pandoc" not in shutil.which("pandoc"):
                raise EnvironmentError("Pandoc not installed or not in PATH")

    def convert(self):
        """Convert document to Markdown and extract media."""
        self.validate_environment()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        base_name = self.input_file.stem
        self.markdown_output = self.output_dir / f"{base_name}.md"
        self.media_dir = self.output_dir / f"{base_name}_media"
        self.media_dir.mkdir(parents=True, exist_ok=True)

        try:
            if self.input_file.suffix.lower() == ".pdf":
                doc = pymupdf.open(str(self.input_file))
                markdown_content = ""
                
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    markdown_content += text + "\n\n"
                    
                    # Extract images from the page
                    img_list = page.get_images()
                    for img in img_list:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        ext = base_image["ext"]
                        
                        # Save image to media directory
                        image_filename = f"page{page_num}_xref{xref}.{ext}"
                        image_path = self.media_dir / image_filename
                        with open(image_path, 'wb') as img_file:
                            img_file.write(image_bytes)
                        
                        # Add image reference to Markdown
                        markdown_content += f"![Image from page {page_num}]({image_filename})\n\n"
                
                # Write Markdown content to file
                with open(self.markdown_output, "w", encoding="utf-8") as f:
                    f.write(markdown_content)
                
                doc.close()
                if not self.markdown_output.exists():
                    raise FileNotFoundError("Markdown output not generated")
            else:
                subprocess.run([
                    "pandoc",
                    str(self.input_file),
                    "-o",
                    str(self.markdown_output),
                    "--extract-media",
                    str(self.media_dir)
                ], check=True)
            return True, "Conversion successful"
        except subprocess.CalledProcessError as e:
            return False, f"Pandoc failed: {e.stderr.decode()}"
        except Exception as e:
            return False, str(e)

def main(input_file, output_dir):
    try:
        converter = DocumentConverter(input_file, output_dir)
        success, message = converter.convert()
        if success:
            print(f"Markdown: {converter.markdown_output}\nMedia: {converter.media_dir}")
        else:
            print(f"Error: {message}")
    except Exception as e:
        print(f"Critical error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_to_markdown.py <input_file> <output_directory>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])