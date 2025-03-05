# Family Tree Generator

This repository contains tools to generate family tree visualizations from structured CSV data.

## Project Structure

```
family-tree/
├── data/                # Input data files
│   ├── *.mermaid        # Original Mermaid graph files
│   ├── all.csv          # Original CSV data
│   └── family_data_improved.csv  # Structured CSV data
│
├── src/                 # Source code
│   ├── generate_family_tree.py   # Python generator script
│   └── generate_tree.sh          # Shell script for easy generation
│
├── output/              # Generated files
│   ├── *.pdf            # PDF visualizations
│   ├── *.png            # PNG visualizations
│   └── dot/             # Generated DOT files
│
└── images/              # Original image files
```

## How to Use

### For a full family tree:

```
cd src
./generate_tree.sh
```

### For an ancestry tree (showing only a person's ancestors):

```
cd src
./generate_tree.sh "Person Name"
```

Example:
```
cd src
./generate_tree.sh "Kajetan Montauk"
```

This will generate:
- `output/dot/ancestry_kajetan_montauk.dot`
- `output/ancestry_kajetan_montauk.pdf`
- `output/ancestry_kajetan_montauk.png`

### Manual usage:

You can also run the Python script directly:

```
cd src

# For a full tree:
python3 generate_family_tree.py

# For ancestry tree:
python3 generate_family_tree.py -- -- "Person Name"
```

And generate visualizations manually:

```
dot -Tpdf ../output/dot/generated_family_tree.dot -o ../output/generated_family_tree.pdf
dot -Tpng ../output/dot/generated_family_tree.dot -o ../output/generated_family_tree.png
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