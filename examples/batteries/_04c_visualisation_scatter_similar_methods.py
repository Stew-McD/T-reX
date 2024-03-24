import os
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from _00_main import DIR_VISUALISATION

pairs = {
    "EDIP 2003 no LT-non-renewable resources no LT-aluminium no LT": "T-reX-Demand: Aluminium-Aluminium",
    "EDIP 2003 no LT-non-renewable resources no LT-brown coal no LT": "T-reX-Demand: Coal(brown)-Coal(brown)",
    "EDIP 2003 no LT-non-renewable resources no LT-coal no LT": "T-reX-Demand: Coal(black)-Coal(black)",
    "EDIP 2003 no LT-non-renewable resources no LT-cobalt no LT": "T-reX-Demand: Cobalt-Cobalt",
    "EDIP 2003 no LT-non-renewable resources no LT-copper no LT": "T-reX-Demand: Copper-Copper",
    "EDIP 2003 no LT-non-renewable resources no LT-natural gas no LT": "T-reX-Demand: Natural gas-Natural gas",
    "EDIP 2003 no LT-non-renewable resources no LT-nickel no LT": "T-reX-Demand: Nickel-Nickel",
    "EDIP 2003 no LT-non-renewable resources no LT-oil no LT": "T-reX-Demand: Petroleum-Petroleum",
    "EDIP 2003 no LT-non-renewable resources no LT-zinc no LT": "T-reX-Demand: Zinc-Zinc",
}

# Register Libertine font
font_path = "LinLibertine_Rah.ttf"  # Update the path as needed
pdfmetrics.registerFont(TTFont("Libertine", font_path))

# Directory containing SVG files
svg_dir = DIR_VISUALISATION / "individual-methods"
print(f"Reading SVG files from directory: {svg_dir}")

# Define the layout and title
title = "T-reX --- Comparison of Similar Methods"
page_width = 0
page_height = 0
title_height = 40  # Space for title

# Calculate total page height based on pairs
for edip, T_reX in pairs.items():
    edip_file = next((f for f in os.listdir(svg_dir) if edip in f), None)
    T_reX_file = next((f for f in os.listdir(svg_dir) if T_reX in f), None)

    if edip_file and T_reX_file:
        edip_svg = svg2rlg(os.path.join(svg_dir, edip_file))
        T_reX_svg = svg2rlg(os.path.join(svg_dir, T_reX_file))

        # Update page width and height
        page_width = max(page_width, edip_svg.width + T_reX_svg.width)
        page_height += max(edip_svg.height, T_reX_svg.height)

# Add space for title
page_height += title_height
print(f"Total page size set to: {page_width}x{page_height}")

# Create a PDF file
c = canvas.Canvas(str(DIR_VISUALISATION / "scatter-similar_methods.pdf"))
c.setPageSize((page_width, page_height))

# Initialize Y-coordinate for drawing
current_y = page_height - title_height

# Add the title
c.setFont("Libertine", 16)
title_width = c.stringWidth(title, "Libertine", 16)
title_y_position = (
    current_y + (title_height - c._fontsize) / 2
)  # Center title vertically in the allocated title space
c.drawString((page_width - title_width) / 2, title_y_position, title)

# Add metadata
c.setTitle("Comparison of Similar Methods")
c.setAuthor("Stewart Charles McDowall")
print("Metadata set.")

# Loop through pairs and add SVG files to the PDF
for edip, T_reX in pairs.items():
    edip_file = next((f for f in os.listdir(svg_dir) if edip in f), None)
    T_reX_file = next((f for f in os.listdir(svg_dir) if T_reX in f), None)

    if edip_file and T_reX_file:
        # Draw the first SVG
        edip_svg = svg2rlg(os.path.join(svg_dir, edip_file))
        renderPDF.draw(edip_svg, c, 0, current_y - edip_svg.height)
        print(f"Added '{edip_file}' to the PDF.")

        # Draw the second SVG
        T_reX_svg = svg2rlg(os.path.join(svg_dir, T_reX_file))
        renderPDF.draw(T_reX_svg, c, edip_svg.width, current_y - T_reX_svg.height)
        print(f"Added '{T_reX_file}' to the PDF.")

        # Update Y-coordinate for next pair
        current_y -= max(edip_svg.height, T_reX_svg.height)

# Save the PDF
c.save()
print("PDF created: scatter-similar_methods.pdf")
