import os
from tqdm import tqdm
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# Register Libertine font
font_path = "LinLibertine_Rah.ttf"  # Change as needed
pdfmetrics.registerFont(TTFont("Libertine", font_path))

from _00_main import DIR_VISUALISATION
# Directory containing SVG files
svg_dir = DIR_VISUALISATION / "individual-methods"
print(f'{"*"*50}')
print(f"Reading SVG files from directory: {svg_dir}")
print(f'{"*"*50}')

# Define the layout and title
title = "T-reX --- Scatter plots of individual methods"
columns = 3
figures = [f for f in os.listdir(svg_dir) if f.endswith(".svg")]
figures = sorted(figures, reverse=True)
figures_count = len(figures)
rows = figures_count // columns + (1 if figures_count % columns else 0)

if figures_count == 0:
    raise ValueError("No SVG files found in the directory.")
else:
    print(f"Found {figures_count} SVG files.")

# Get the size of the first SVG to determine the size for all
first_svg = svg2rlg(os.path.join(svg_dir, figures[0]))
img_width = first_svg.width
img_height = first_svg.height
print(f"Each SVG size: {round(img_width, 2)}x{round(img_height, 2)} units.")

# Calculate the size of the page
title_height = 50  # Adjust as needed
page_width = columns * img_width
page_height = rows * img_height + title_height
print(
    f"Creating a single-page PDF with size: {round(page_width,2)}x{round(page_height,2)} units."
)

# Create a PDF file
c = canvas.Canvas(
    str(DIR_VISUALISATION / "scatter-combined_methods.pdf"),
    pagesize=(page_width, page_height),
)

# Add the title
c.setFont("Libertine", 16)  # Set Libertine font and size for the title
title_width = c.stringWidth(title, "Libertine", 16)
c.drawString(
    (page_width - title_width) / 2, page_height - 35, title
)  # Center the title

# Add metadata
c.setTitle("T-reX: Scatter Plots of Individual Methods")  # PDF Title
c.setAuthor("Stewart Charles McDowall")  # Author's name


print("Starting to add SVG files to the PDF...")


count_figures = len(figures)
progress_bar = tqdm(total=count_figures, desc="Processing figures")

for file in figures:
    i = figures.index(file)
    x = (i % columns) * img_width
    y = page_height - ((i // columns) + 1) * img_height - title_height
    drawing = svg2rlg(os.path.join(svg_dir, file))
    renderPDF.draw(drawing, c, x, y)
    progress_bar.update(1)

progress_bar.close()

# Save the PDF
c.save()
print(f'{"*"*50}')
print("PDF created: combined_methods.pdf")
print(f'{"*"*50}')
