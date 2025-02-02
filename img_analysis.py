import os
from vision_model import VisionModel

# Initialize vision model
vision_model = VisionModel()

def generate_image_descriptions(image_dir):
    """Generate descriptions for all images in the specified directory"""
    descriptions = {}

    for image_file in os.listdir(image_dir):
        if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(image_dir, image_file)
            description = vision_model.describe_image(image_path)
            descriptions[image_file] = description

    return descriptions

def save_descriptions_to_markdown(markdown_file, image_dir, output_file=None):
    """Append image descriptions to the Markdown file"""
    output_file = output_file or markdown_file
    descriptions = generate_image_descriptions(image_dir)

    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        content = ""

    # Append descriptions
    for image_file, description in descriptions.items():
        content += f"\n\n*Screenshot Description ({image_file}):* {description}"

    # Save updated Markdown content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)