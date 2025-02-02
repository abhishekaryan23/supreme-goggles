import gradio as gr
from convert_to_markdown import DocumentConverter
from pathlib import Path
import os

def convert_document(input_file, output_dir):
    # Set default output directory
    if not output_dir.strip():
        default_output = Path.cwd() / "converted_documents"
        output_dir = str(default_output)
        default_output.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        converter = DocumentConverter(input_file.name, output_dir)
        success, message = converter.convert()
        
        if success:
            # Read the generated Markdown file
            with open(converter.markdown_output, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            output_str = f"Success! Converted file saved to:\nMarkdown: {converter.markdown_output}\nMedia: {converter.media_dir}"
            return markdown_content, output_str
        else:
            return "", f"Conversion failed: {message}"
    except Exception as e:
        return "", f"Error occurred during conversion: {str(e)}"

iface = gr.Interface(
    fn=convert_document,
    inputs=[
        gr.File(label="Upload document to convert"),
        gr.Textbox(
            label="Output directory (leave blank for default)",
            placeholder="Default: converted_documents folder in current directory"
        )
    ],
    outputs=[
        gr.Markdown(label="Converted Markdown Preview"),
        gr.Textbox(label="Status")
    ],
    title="Markdown Document Converter",
    description="Converts documents (PDF, DOCX, etc.) to Markdown format with images included in a media folder."
)

if __name__ == "__main__":
    iface.launch()