# Family Tree Generator

This repository contains tools to generate family tree visualizations from structured CSV data.

## Files

- `family_data_improved.csv` - CSV file containing the family data
- `generate_family_tree.py` - Python script to generate DOT files for GraphViz
- `generate_tree.sh` - Shell script for easy tree generation
- `generated_family_tree.dot` - Generated DOT file
- `generated_family_tree.pdf` - Rendered PDF of the family tree
- `generated_family_tree.png` - Rendered PNG of the family tree

## How to Use

### For a full family tree:

```
./generate_tree.sh
```

### For an ancestry tree (showing only a person's ancestors):

```
./generate_tree.sh "Person Name"
```

Example:
```
./generate_tree.sh "Kajetan Montauk"
```

This will generate:
- `ancestry_kajetan_montauk.dot`
- `ancestry_kajetan_montauk.pdf`
- `ancestry_kajetan_montauk.png`

### Manual usage:

You can also run the Python script directly:

```
# For a full tree:
python3 generate_family_tree.py

# For ancestry tree:
python3 generate_family_tree.py -- -- "Person Name"
```

And generate visualizations manually:

```
dot -Tpdf generated_family_tree.dot -o generated_family_tree.pdf
dot -Tpng generated_family_tree.dot -o generated_family_tree.png
```

## CSV Format

The CSV file has the following columns:

- `Full Name` - Complete name of the person
- `Family Name` - Current family name
- `Maiden Name` - Maiden name for women (blank for men)
- `Date of Birth` - Birth date in any format
- `Date of Death` - Death date in any format
- `Spouse 1` - Name of first spouse (if any)
- `Spouse 2` - Name of second spouse (if any)
- `Child 1` - Name of first child (if any)
- `Child 2` - Name of second child (if any)
- `Child 3` - Name of third child (if any)
- `Generation` - Generation number (starting with 1850 as generation 1)

## Requirements

- Python 3
- GraphViz (for rendering the DOT files)

## Examples

To add a new person to the family tree:

1. Add a row to the CSV file with the person's information
2. Run the generator script
3. Generate the visualization

For more detailed trees, you can modify the `generate_family_tree.py` script to customize:
- Colors
- Layout
- Grouping
- Labels