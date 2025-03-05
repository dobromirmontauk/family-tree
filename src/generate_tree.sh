#!/bin/bash
# Script to regenerate the family tree from CSV data
# Optional: Provide a person's name to generate only their ancestry tree

# Change to the directory where the script is located
cd "$(dirname "$0")"

# Default filenames
INPUT_CSV="family_data_improved.csv"
OUTPUT_DOT="generated_family_tree.dot"
PDF_OUTPUT="generated_family_tree.pdf"
PNG_OUTPUT="generated_family_tree.png"
PERSON_NAME=""

# Process command line arguments
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    echo "Usage: $0 [person_name]"
    echo ""
    echo "  person_name    Optional: Generate ancestry tree for this person"
    echo "                 If not provided, generates the full family tree"
    echo ""
    echo "Example: $0 \"Kajetan Montauk\""
    exit 0
fi

# If a name is provided, use it to generate an ancestry tree
if [ -n "$1" ]; then
    PERSON_NAME="$1"
    # Create output filenames for the ancestry tree
    NAME_SLUG=$(echo "$PERSON_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '_')
    OUTPUT_DOT="ancestry_${NAME_SLUG}.dot"
    PDF_OUTPUT="ancestry_${NAME_SLUG}.pdf"
    PNG_OUTPUT="ancestry_${NAME_SLUG}.png"
fi

# Generate the DOT file
if [ -n "$PERSON_NAME" ]; then
    echo "Generating ancestry tree for '$PERSON_NAME'..."
    python3 generate_family_tree.py "$INPUT_CSV" "$OUTPUT_DOT" "$PERSON_NAME"
else
    echo "Generating full family tree..."
    python3 generate_family_tree.py
fi

# Check if the DOT file was generated successfully
if [ ! -f "./$OUTPUT_DOT" ]; then
    echo "Error: DOT file was not generated."
    exit 1
fi

# Generate the PDF
echo "Generating PDF..."
dot -Tpdf "$OUTPUT_DOT" -o "$PDF_OUTPUT"

# Generate the PNG
echo "Generating PNG..."
dot -Tpng "$OUTPUT_DOT" -o "$PNG_OUTPUT"

# Check if the files were generated successfully
if [ -f "./$PDF_OUTPUT" ] && [ -f "./$PNG_OUTPUT" ]; then
    echo "Success! Generated files:"
    echo "  - $(pwd)/$PDF_OUTPUT"
    echo "  - $(pwd)/$PNG_OUTPUT"
else
    echo "Error: Some files were not generated correctly."
    exit 1
fi

echo "Done!"