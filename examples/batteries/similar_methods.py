import os
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

pairs = {
    "EDIP 2003 no LT-non-renewable resources no LT-aluminium no LT": "WasteAndMaterialFootprint-Demand: Aluminium-Aluminium",
    "EDIP 2003 no LT-non-renewable resources no LT-brown coal no LT": "WasteAndMaterialFootprint-Demand: Coal(brown)-Coal(brown)",
    "EDIP 2003 no LT-non-renewable resources no LT-coal no LT": "WasteAndMaterialFootprint-Demand: Coal(black)-Coal(black)",
    "EDIP 2003 no LT-non-renewable resources no LT-cobalt no LT": "WasteAndMaterialFootprint-Demand: Cobalt-Cobalt",
    "EDIP 2003 no LT-non-renewable resources no LT-copper no LT": "WasteAndMaterialFootprint-Demand: Copper-Copper",
    "EDIP 2003 no LT-non-renewable resources no LT-natural gas no LT": "WasteAndMaterialFootprint-Demand: Natural gas-Natural gas",
    "EDIP 2003 no LT-non-renewable resources no LT-nickel no LT": "WasteAndMaterialFootprint-Demand: Nickel-Nickel",
    "EDIP 2003 no LT-non-renewable resources no LT-oil no LT": "WasteAndMaterialFootprint-Demand: Petroleum-Petroleum",
    "EDIP 2003 no LT-non-renewable resources no LT-zinc no LT": "WasteAndMaterialFootprint-Demand: Zinc-Zinc",
}

# Register Libertine font
font_path = "LinLibertine_Rah.ttf"  # Update the path as needed
pdfmetrics.registerFont(TTFont("Libertine", font_path))

# Directory containing SVG files
svg_dir = "visualisation/individual-methods"
print(f"Reading SVG files from directory: {svg_dir}")

# Define the layout and title
title = "WasteAndMaterialFootprint --- Comparison of Similar Methods"
page_width = 0
page_height = 0
title_height = 40  # Space for title

# Calculate total page height based on pairs
for edip, wmf in pairs.items():
    edip_file = next((f for f in os.listdir(svg_dir) if edip in f), None)
    wmf_file = next((f for f in os.listdir(svg_dir) if wmf in f), None)

    if edip_file and wmf_file:
        edip_svg = svg2rlg(os.path.join(svg_dir, edip_file))
        wmf_svg = svg2rlg(os.path.join(svg_dir, wmf_file))

        # Update page width and height
        page_width = max(page_width, edip_svg.width + wmf_svg.width)
        page_height += max(edip_svg.height, wmf_svg.height)

# Add space for title
page_height += title_height
print(f"Total page size set to: {page_width}x{page_height}")

# Create a PDF file
c = canvas.Canvas("similar_methods.pdf")
c.setPageSize((page_width, page_height))

# Initialize Y-coordinate for drawing
current_y = page_height - title_height

# Add the title
c.setFont("Libertine", 16)
title_width = c.stringWidth(title, "Libertine", 16)
title_y_position = current_y + (title_height - c._fontsize) / 2  # Center title vertically in the allocated title space
c.drawString((page_width - title_width) / 2, title_y_position, title)

# Add metadata
c.setTitle("Comparison of Similar Methods")
c.setAuthor("Stewart Charles McDowall")
print("Metadata set.")

# Loop through pairs and add SVG files to the PDF
for edip, wmf in pairs.items():
    edip_file = next((f for f in os.listdir(svg_dir) if edip in f), None)
    wmf_file = next((f for f in os.listdir(svg_dir) if wmf in f), None)

    if edip_file and wmf_file:
        # Draw the first SVG
        edip_svg = svg2rlg(os.path.join(svg_dir, edip_file))
        renderPDF.draw(edip_svg, c, 0, current_y - edip_svg.height)
        print(f"Added '{edip_file}' to the PDF.")

        # Draw the second SVG
        wmf_svg = svg2rlg(os.path.join(svg_dir, wmf_file))
        renderPDF.draw(wmf_svg, c, edip_svg.width, current_y - wmf_svg.height)
        print(f"Added '{wmf_file}' to the PDF.")

        # Update Y-coordinate for next pair
        current_y -= max(edip_svg.height, wmf_svg.height)

# Save the PDF
c.save()
print("PDF created: similar_methods.pdf")
