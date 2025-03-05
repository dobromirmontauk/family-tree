#!/bin/bash
# Script to regenerate the family tree from CSV data
# Optional: Provide a person's name to generate only their ancestry tree

# Change to the directory where the script is located
cd "$(dirname "$0")"

# Project directories
DATA_DIR="../data"
OUTPUT_DIR="../output"
OUTPUT_DOT_DIR="../output/dot"

# Default filenames
INPUT_CSV="${DATA_DIR}/family_data_improved.csv"
OUTPUT_DOT="${OUTPUT_DOT_DIR}/generated_family_tree.dot"
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
fi

# Ensure output directories exist
mkdir -p "${OUTPUT_DIR}"
mkdir -p "${OUTPUT_DOT_DIR}"

# Generate the DOT file and extract output filenames
if [ -n "$PERSON_NAME" ]; then
    echo "Generating ancestry tree for '$PERSON_NAME'..."
    result=$(python3 generate_family_tree.py "$INPUT_CSV" "$OUTPUT_DOT" "$PERSON_NAME" 2>&1)
else
    echo "Generating full family tree..."
    result=$(python3 generate_family_tree.py 2>&1)
fi

# Check if the Python script executed successfully
if [ $? -ne 0 ]; then
    echo "Error: Failed to generate DOT file."
    echo "$result"
    exit 1
fi

# Extract the DOT, PDF, and PNG filenames from the output
DOT_FILE=$(echo "$result" | grep -o "dot -Tpdf [^ ]* -o" | sed 's/dot -Tpdf \(.*\) -o/\1/')
PDF_FILE=$(echo "$result" | grep -o "\-o [^ ]*\.pdf" | sed 's/-o //')
PNG_FILE=$(echo "$result" | grep -o "\-o [^ ]*\.png" | sed 's/-o //')

# Verify we have filenames
if [ -z "$DOT_FILE" ] || [ -z "$PDF_FILE" ] || [ -z "$PNG_FILE" ]; then
    echo "Error: Could not determine output filenames."
    echo "$result"
    exit 1
fi

# Check if the DOT file was generated
if [ ! -f "$DOT_FILE" ]; then
    echo "Error: DOT file was not generated."
    exit 1
fi

# Generate the PDF
echo "Generating PDF..."
dot -Tpdf "$DOT_FILE" -o "$PDF_FILE"

# Generate the PNG
echo "Generating PNG..."
dot -Tpng "$DOT_FILE" -o "$PNG_FILE"

# Check if the files were generated successfully
if [ -f "$PDF_FILE" ] && [ -f "$PNG_FILE" ]; then
    echo "Success! Generated files:"
    echo "  - $PDF_FILE"
    echo "  - $PNG_FILE"
else
    echo "Error: Some files were not generated correctly."
    exit 1
fi

echo "Done!"