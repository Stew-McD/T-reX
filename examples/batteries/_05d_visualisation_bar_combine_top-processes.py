import os
import xml.etree.ElementTree as ET
from tqdm import tqdm
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from _00_main import DIR_VISUALISATION

# Register Libertine font
font_path = "misc/LinLibertine_Rah.ttf"  # Change as needed
pdfmetrics.registerFont(TTFont("Libertine", font_path))

# Directory containing SVG files
svg_dir = DIR_VISUALISATION / "individual-methods_top-processes"
print(f'{"*"*50}')
print(f"Reading SVG files from directory: {svg_dir}")
print(f'{"*"*50}')

# Define the layout and title
filename = str(DIR_VISUALISATION / "combined_methods_top-processes.pdf")
title = "T-reX: Contributions to total LCIA score from top five processes"
columns = 5
figures = sorted([f for f in os.listdir(svg_dir) if f.endswith(".svg")], reverse=True)
figures_count = len(figures)
rows = figures_count // columns + (1 if figures_count % columns else 0)

if figures_count == 0:
    raise ValueError("No SVG files found in the directory.")
else:
    print(f"Found {figures_count} SVG files.")

# # Initialize variables to store the maximum dimensions
# max_width = 205
# max_height = 532

max_width = 0
max_height = 0

# Define margin size
margin = 2  # You can adjust this value

# Iterate through each SVG file to find max dimensions
progress_bar = tqdm(total=len(figures), desc="Calculating maximum dimensions")
for svg_file in figures:
    file_path = os.path.join(svg_dir, svg_file)
    svg_obj = svg2rlg(file_path)
    max_width = max(max_width, svg_obj.width)
    max_height = max(max_height, svg_obj.height)
    min_width = min(max_width, svg_obj.width)
    min_height = min(max_height, svg_obj.height)
    progress_bar.update(1)
progress_bar.close()

print(f'{"*"*50}')
print(f"Maximum width: {round(max_width,1)}, Maximum height: {round(max_height,1)}")
print(f"Minimum width: {round(min_width,1)}, Minimum height: {round(min_height,1)}")
print(f'{"*"*50}')

# Modify SVG files to add margins
progress_bar = tqdm(total=len(figures), desc="Adding margins to SVGs")
for svg_file in figures:
    file_path = os.path.join(svg_dir, svg_file)
    drawing = svg2rlg(file_path)
    c = canvas.Canvas(file_path, pagesize=(max_width, max_height))
    renderPDF.draw(drawing, c, 0, 0)

    progress_bar.update(1)
progress_bar.close()


# Calculate the size of the page
title_height = 60  # Adjust as needed
page_width = columns * (max_width + 2 * margin)
page_height = rows * (max_height + 2 * margin) + title_height
print(
    f"Creating a single-page PDF with size: {round(page_width,2)}x{round(page_height,2)} units."
)

# Create a PDF file
c = canvas.Canvas(filename, pagesize=(page_width, page_height))

# Add the title
c.setFont("Libertine", 20)
title_width = c.stringWidth(title, "Libertine", 20)
c.drawString((page_width - title_width) / 2, page_height - 35, title)

# Add metadata
c.setTitle("T-reX: Contributions from top five processes")
c.setAuthor("Stewart Charles McDowall")

print("Starting to add SVG files to the PDF...")

progress_bar = tqdm(total=figures_count, desc="Adding SVGs to PDF")
for i, file in enumerate(figures):
    x = (i % columns) * (max_width + 2 * margin)
    y = page_height - ((i // columns) + 1) * (max_height + 2 * margin) - title_height
    drawing = svg2rlg(os.path.join(svg_dir, file))
    renderPDF.draw(drawing, c, x, y)
    progress_bar.update(1)
progress_bar.close()

# Save the PDF
c.save()
print(f'{"*"*50}')
print(f"PDF created: {filename}")
print(f'{"*"*50}')
