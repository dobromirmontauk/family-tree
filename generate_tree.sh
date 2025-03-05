#!/bin/bash
# Simple script to regenerate the family tree from CSV data

# Change to the directory where the script is located
cd "$(dirname "$0")"

# Generate the DOT file
echo "Generating DOT file from CSV data..."
python3 generate_family_tree.py

# Check if the DOT file was generated successfully
if [ ! -f "./generated_family_tree.dot" ]; then
    echo "Error: DOT file was not generated."
    exit 1
fi

# Generate the PDF
echo "Generating PDF..."
dot -Tpdf generated_family_tree.dot -o generated_family_tree.pdf

# Generate the PNG
echo "Generating PNG..."
dot -Tpng generated_family_tree.dot -o generated_family_tree.png

# Check if the files were generated successfully
if [ -f "./generated_family_tree.pdf" ] && [ -f "./generated_family_tree.png" ]; then
    echo "Success! Generated files:"
    echo "  - $(pwd)/generated_family_tree.pdf"
    echo "  - $(pwd)/generated_family_tree.png"
else
    echo "Error: Some files were not generated correctly."
    exit 1
fi

echo "Done!"