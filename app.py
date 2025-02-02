import os
import re
import base64
from pathlib import Path
import gradio as gr
from convert_to_markdown import DocumentConverter

def get_mime_type(extension):
    """Map file extensions to MIME types."""
    mime_types = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'tiff': 'image/tiff',
        'bmp': 'image/bmp',
    }
    return mime_types.get(extension.lower(), 'application/octet-stream')

def embed_images(markdown_content, media_dir):
    """Embed images in Markdown as base64 data URIs."""
    if not media_dir or not Path(media_dir).exists():
        return markdown_content
    
    # Match image references in Markdown
    image_refs = re.findall(r'!\[.*?\]\((.*?)\)', markdown_content)
    for image_ref in image_refs:
        image_path = Path(media_dir) / image_ref
        if image_path.exists():
            with open(image_path, 'rb') as img_file:
                base64_img = base64.b64encode(img_file.read()).decode('utf-8')
                ext = image_path.suffix.lstrip('.').lower()
                mime = get_mime_type(ext)
                # Replace image path with base64 data URI
                markdown_content = markdown_content.replace(f'({image_ref})', 
                    f'(data:{mime};base64,{base64_img})')
    return markdown_content

def convert_document(input_file, output_dir):
    if not output_dir.strip():
        output_dir = str(Path.cwd() / "converted_documents")
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    else:
        output_dir = str(Path(output_dir).expanduser().resolve())
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        converter = DocumentConverter(input_file.name, output_dir)
        success, _ = converter.convert()
        if success and converter.markdown_output.exists():
            with open(converter.markdown_output, 'r', encoding='utf-8') as f:
                markdown = embed_images(f.read(), converter.media_dir)
                return markdown, f"Success!\nMarkdown: {converter.markdown_output}"
        return "", "Conversion failed: Output not generated"
    except Exception as e:
        return "", f"Error: {str(e)}"

iface = gr.Interface(
    fn=convert_document,
    inputs=[
        gr.File(label="Upload document"),
        gr.Textbox(label="Output directory (optional)")
    ],
    outputs=[
        gr.Markdown(label="Preview"),
        gr.Textbox(label="Status")
    ],
    title="Document to Markdown Converter",
    description="Converts documents to Markdown with embedded images.",
    allow_flagging="never"
)

if __name__ == "__main__":
    iface.launch()