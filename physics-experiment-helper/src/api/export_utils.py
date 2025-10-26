"""Utilities for exporting experiments to PDF and ZIP formats."""

import zipfile
import io
from pathlib import Path
from typing import Dict, List
import markdown
from io import BytesIO
import requests
import os


def create_zip_archive(files: Dict[str, str], images: List[str] = None, session_id: str = "experiment") -> BytesIO:
    """Create a ZIP archive containing all experiment files.

    Args:
        files: Dictionary of filename to content
        images: List of image URLs
        session_id: Session identifier for naming

    Returns:
        BytesIO object containing the ZIP archive
    """
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add all markdown files
        for filename, content in files.items():
            zip_file.writestr(filename, content)

        # Download and add images if available
        if images:
            images_list = "# Experiment Images\n\n"
            images_folder = "images/"
            
            for idx, img_url in enumerate(images, 1):
                try:
                    # Download image
                    response = requests.get(img_url, timeout=30)
                    response.raise_for_status()
                    
                    # Create image filename
                    img_filename = f"image_{idx:03d}.jpg"
                    img_path = images_folder + img_filename
                    
                    # Add image to ZIP
                    zip_file.writestr(img_path, response.content)
                    
                    # Add to images list
                    images_list += f"{idx}. {img_filename} (from {img_url})\n"
                    
                except Exception as e:
                    # If download fails, just add the URL to the list
                    images_list += f"{idx}. {img_url} (download failed: {str(e)})\n"
            
            zip_file.writestr("experiment_images.txt", images_list)

        # Add README
        readme_content = f"""# Physics Experiment - Session {session_id}

This archive contains your complete physics experiment guide.

## Files Included:
"""
        for filename in files.keys():
            readme_content += f"- {filename}\n"

        if images:
            readme_content += f"\n## Images: {len(images)} found\n"
            readme_content += "Images are stored in the 'images/' folder and listed in experiment_images.txt\n"

        readme_content += """
## How to Use:
1. Open each markdown (.md) file in a text editor or markdown viewer
2. Follow the methodology step-by-step
3. Use the data templates to record your measurements
4. Complete your report using the report template
5. View images in the 'images/' folder

Good luck with your experiment!
"""
        zip_file.writestr("README.txt", readme_content)

    zip_buffer.seek(0)
    return zip_buffer


def markdown_to_html(markdown_content: str, include_images: bool = True) -> str:
    """Convert markdown content to HTML.

    Args:
        markdown_content: Markdown text
        include_images: Whether to process image tags

    Returns:
        HTML string
    """
    html_content = markdown.markdown(
        markdown_content,
        extensions=['extra', 'codehilite', 'tables', 'fenced_code']
    )

    # Wrap in basic HTML structure
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Physics Experiment</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
                color: #333;
            }}
            h1 {{
                color: #2563eb;
                border-bottom: 3px solid #2563eb;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #3b82f6;
                margin-top: 30px;
            }}
            h3 {{
                color: #60a5fa;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #2563eb;
                color: white;
            }}
            code {{
                background-color: #f3f4f6;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }}
            pre {{
                background-color: #f3f4f6;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }}
            blockquote {{
                border-left: 4px solid #2563eb;
                padding-left: 20px;
                margin-left: 0;
                font-style: italic;
                color: #666;
            }}
            img {{
                max-width: 100%;
                height: auto;
                margin: 20px 0;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .warning {{
                background-color: #fef3c7;
                border-left: 4px solid #f59e0b;
                padding: 15px;
                margin: 20px 0;
            }}
            @media print {{
                body {{
                    max-width: 100%;
                }}
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    return full_html


def create_complete_html_report(files: Dict[str, str], images: List[str] = None, session_id: str = "experiment") -> str:
    """Create a single HTML document from all experiment files.

    Args:
        files: Dictionary of filename to markdown content
        images: List of image URLs to include
        session_id: Session identifier

    Returns:
        Complete HTML document
    """
    # Combine all files into one document
    combined_markdown = f"# Physics Experiment Report - Session {session_id}\n\n"

    # Define file order
    file_order = [
        "experiment_synopsis.md",
        "theory_and_background.md",
        "methodology.md",
        "data_template.md",
        "analysis_and_conclusion.md",
        "report_template.md",
        "references_and_resources.md"
    ]

    # Add images section if available
    if images:
        combined_markdown += "## Experiment Images\n\n"
        for idx, img_url in enumerate(images, 1):
            combined_markdown += f"![Experiment Image {idx}]({img_url})\n\n"
            combined_markdown += f"*Image {idx}: [View full size]({img_url})*\n\n"
        combined_markdown += "---\n\n"

    # Add files in order
    for filename in file_order:
        if filename in files:
            combined_markdown += f"\n\n---\n\n# {filename.replace('_', ' ').replace('.md', '').title()}\n\n"
            combined_markdown += files[filename]
            combined_markdown += "\n\n"

    # Add any remaining files not in the order
    for filename, content in files.items():
        if filename not in file_order:
            combined_markdown += f"\n\n---\n\n# {filename.replace('_', ' ').replace('.md', '').title()}\n\n"
            combined_markdown += content
            combined_markdown += "\n\n"

    # Convert to HTML
    html_report = markdown_to_html(combined_markdown)

    return html_report
