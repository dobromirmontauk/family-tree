#!/usr/bin/env python3
"""
Family Tree Generator
--------------------
This script reads family data from a CSV file and generates a DOT file
for GraphViz to visualize the family tree.

Usage:
    python generate_family_tree.py [input_csv] [output_dot] [person_name]

    Default input_csv: family_data_improved.csv
    Default output_dot: generated_family_tree.dot
    person_name: Optional. Generate only ancestors for this person
                 If not provided, generates the full family tree

Examples:
    python generate_family_tree.py                           # Full tree
    python generate_family_tree.py family.csv family.dot     # Custom files
    python generate_family_tree.py -- -- "Kajetan Montauk"   # Just ancestors
"""

import csv
import sys
import os
import re
from collections import defaultdict

# Default paths
DATA_DIR = "../data"
OUTPUT_DIR = "../output"
OUTPUT_DOT_DIR = "../output/dot"

# Default filenames
DEFAULT_INPUT_CSV = f"{DATA_DIR}/family_data_improved.csv"
DEFAULT_OUTPUT_DOT = f"{OUTPUT_DOT_DIR}/generated_family_tree.dot"

# Colors and styles
MALE_COLOR = "#BBDEFB"  # Light blue
FEMALE_COLOR = "#F8BBD0"  # Light pink
GENERATION_COLORS = [
    "lightgrey",  # Generation 1
    "#E0E0E0",    # Generation 2
    "#F5F5F5",    # Generation 3
    "#FAFAFA",    # Generation 4
    "#EEEEEE",    # Generation 5
    "#F5F5F5",    # Generation 6
    "#E0E0E0",    # Generation 7
]

def read_family_data(csv_filename):
    """Read family data from CSV file and return as a list of dictionaries."""
    family_data = []
    
    with open(csv_filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            family_data.append(row)
    
    return family_data

def organize_by_generation(family_data):
    """Organize family data by generation."""
    generations = defaultdict(list)
    
    for person in family_data:
        gen = person.get('Generation', '')
        if gen and gen.isdigit():
            generations[int(gen)].append(person)
    
    return generations

def generate_person_node(person, person_id):
    """Generate DOT code for a person node."""
    name = person['Full Name'].strip('"')
    birth_date = person['Date of Birth'].strip('"')
    death_date = person['Date of Death'].strip('"')
    
    # Determine label text
    label_text = name
    if birth_date or death_date:
        label_text += "\\n"
        if birth_date:
            label_text += f"b. {birth_date}"
        if death_date and death_date != "":
            label_text += f", d. {death_date}" if birth_date else f"d. {death_date}"
    
    # Determine gender based on maiden name or family name
    is_female = False
    maiden_name = person.get('Maiden Name', '').strip('"')
    if maiden_name:
        is_female = True
    
    # Handle edge cases and name formats
    fill_color = FEMALE_COLOR if is_female else MALE_COLOR
    
    # Generate node
    return f'    {person_id} [label="{label_text}", shape=box, style="filled,rounded", fillcolor="{fill_color}"];'

def find_person_id(name, id_mapping):
    """Find person ID in the mapping or create a new one."""
    if name in id_mapping:
        return id_mapping[name]
    
    # Create a safe ID for the person
    safe_id = name.lower().replace(' ', '_').replace('"', '').replace('(', '').replace(')', '').replace(',', '')
    id_mapping[name] = safe_id
    return safe_id

def find_ancestors(family_data, person_name):
    """Find all ancestors of the given person."""
    # Create a dictionary of children -> parents
    child_to_parents = defaultdict(list)
    name_mapping = {}  # To handle case-insensitive matching
    
    # Fill the child_to_parents mapping
    for person in family_data:
        person_name_normalized = person['Full Name'].strip('"').lower()
        name_mapping[person_name_normalized] = person['Full Name'].strip('"')
        
        for i in range(1, 4):  # Child 1, Child 2, Child 3
            child_key = f'Child {i}'
            if child_key in person and person[child_key].strip('"'):
                child_name = person[child_key].strip('"')
                child_name_normalized = child_name.lower()
                name_mapping[child_name_normalized] = child_name
                child_to_parents[child_name_normalized].append(person['Full Name'].strip('"'))
    
    # Search for the person (case-insensitive)
    person_name_normalized = person_name.lower()
    if person_name_normalized not in name_mapping:
        close_matches = [name for name in name_mapping if person_name_normalized in name]
        if close_matches:
            print(f"Person '{person_name}' not found, but found similar names:")
            for match in close_matches:
                print(f"  - {name_mapping[match]}")
        else:
            print(f"Person '{person_name}' not found in the family data.")
        return []
    
    # Found the person, now find all ancestors
    actual_name = name_mapping[person_name_normalized]
    ancestors = set()
    
    def add_ancestors(name):
        name_normalized = name.lower()
        if name_normalized in child_to_parents:
            for parent in child_to_parents[name_normalized]:
                parent_normalized = parent.lower()
                if parent not in ancestors:
                    ancestors.add(parent)
                    add_ancestors(parent)
    
    # Start with the person's parents
    add_ancestors(actual_name)
    
    # Add the person themselves
    ancestors.add(actual_name)
    
    return list(ancestors)

def generate_dot_file(family_data, output_filename, person_name=None):
    """Generate DOT file for GraphViz.
    
    If person_name is provided, only include that person and their ancestors.
    """
    # Determine if we're generating a full tree or ancestry tree
    ancestors = None
    if person_name:
        ancestors = find_ancestors(family_data, person_name)
        if not ancestors:
            return False
    
    generations = organize_by_generation(family_data)
    
    # Create mapping of names to IDs
    id_mapping = {}
    for person in family_data:
        name = person['Full Name'].strip('"')
        find_person_id(name, id_mapping)
    
    # Track marriages and parent-child relationships
    marriages = []
    parent_child = defaultdict(list)
    
    # Find marriages and children
    for person in family_data:
        person_name = person['Full Name'].strip('"')
        
        # Skip if we're only showing ancestors and this person isn't one
        if ancestors and person_name not in ancestors:
            continue
            
        person_id = find_person_id(person_name, id_mapping)
        
        # Process spouses
        for i in range(1, 3):  # Spouse 1 and Spouse 2
            spouse_key = f'Spouse {i}'
            if spouse_key in person and person[spouse_key].strip('"'):
                spouse_name = person[spouse_key].strip('"')
                
                # Skip if we're only showing ancestors and this spouse isn't one
                if ancestors and spouse_name not in ancestors:
                    continue
                    
                spouse_id = find_person_id(spouse_name, id_mapping)
                
                # Add marriage if not already added
                marriage = tuple(sorted([person_id, spouse_id]))
                if marriage not in marriages:
                    marriages.append(marriage)
        
        # Process children
        for i in range(1, 4):  # Child 1, Child 2, Child 3
            child_key = f'Child {i}'
            if child_key in person and person[child_key].strip('"'):
                child_name = person[child_key].strip('"')
                
                # Skip if we're only showing ancestors and this child isn't one
                if ancestors and child_name not in ancestors:
                    continue
                    
                child_id = find_person_id(child_name, id_mapping)
                
                # Add parent-child relationship
                if person_id not in parent_child[child_id]:
                    parent_child[child_id].append(person_id)
    
    # Start generating the DOT file
    with open(output_filename, 'w', encoding='utf-8') as f:
        title = "Ancestry Tree" if person_name else "Family Tree"
        
        f.write('digraph FamilyTree {\n')
        f.write('    // Graph settings\n')
        f.write('    rankdir=TB;\n')
        f.write('    nodesep=0.8;\n')
        f.write('    ranksep=1.2;\n')
        f.write('    splines=ortho;\n')
        f.write('    \n')
        f.write('    // Title for the family tree\n')
        f.write('    labelloc="t";\n')
        f.write(f'    label="{title}";\n')
        f.write('    fontsize=24;\n')
        f.write('    \n')
        
        # Generate nodes by generation
        for gen_num, gen_people in sorted(generations.items()):
            gen_color = GENERATION_COLORS[(gen_num - 1) % len(GENERATION_COLORS)]
            
            # Filter people if we're only showing ancestors
            if ancestors:
                gen_people = [p for p in gen_people if p['Full Name'].strip('"') in ancestors]
                if not gen_people:
                    continue
            
            f.write(f'    // Generation {gen_num}\n')
            f.write(f'    subgraph cluster_gen{gen_num} {{\n')
            f.write(f'        label="Generation {gen_num}";\n')
            f.write(f'        style=filled;\n')
            f.write(f'        color="{gen_color}";\n')
            f.write(f'        fontsize=16;\n')
            f.write('\n')
            
            # Add person nodes for this generation
            for person in gen_people:
                person_id = find_person_id(person['Full Name'].strip('"'), id_mapping)
                f.write(f'{generate_person_node(person, person_id)}\n')
            
            f.write('    }\n\n')
        
        # Create invisible nodes for parent-child connections
        f.write('    // Invisible nodes for family connections\n')
        f.write('    node [shape=point, width=0, height=0, style=invis, label=""];\n\n')
        
        # Add marriage connections
        f.write('    // Marriage connections\n')
        f.write('    edge [dir=none, style=solid, penwidth=2.0, color="#555555"];\n')
        for person1_id, person2_id in marriages:
            f.write(f'    {person1_id} -> {person2_id};\n')
        f.write('\n')
        
        # Add parent-child connections using invisible junction nodes
        f.write('    // Parent-child connections\n')
        f.write('    edge [dir=none, style=solid, penwidth=1.2, color="#000000"];\n')
        
        junction_count = 0
        for child_id, parents in parent_child.items():
            if len(parents) >= 1:
                junction_id = f'junction_{junction_count}'
                junction_count += 1
                
                f.write(f'    {junction_id} [shape=point, width=0, height=0, style=invis, label=""];\n')
                
                # Connect parents to junction
                for parent_id in parents:
                    f.write(f'    {parent_id} -> {junction_id};\n')
                
                # Connect junction to child
                f.write(f'    {junction_id} -> {child_id};\n')
        
        f.write('}\n')
        
    return True

def get_output_filename(base_path, person_name=None):
    """Generate appropriate output filenames based on the person name."""
    directory = os.path.dirname(base_path)
    
    # Make sure output directories exist
    os.makedirs(directory, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # For ancestry trees, use a slug of the person's name
    if person_name:
        name_slug = person_name.lower().replace(' ', '_')
        dot_file = f"{directory}/ancestry_{name_slug}.dot"
        pdf_file = f"{OUTPUT_DIR}/ancestry_{name_slug}.pdf"
        png_file = f"{OUTPUT_DIR}/ancestry_{name_slug}.png"
    else:
        # For full trees, use the base path
        base_name = os.path.basename(base_path)
        name_without_ext = os.path.splitext(base_name)[0]
        dot_file = base_path
        pdf_file = f"{OUTPUT_DIR}/{name_without_ext}.pdf"
        png_file = f"{OUTPUT_DIR}/{name_without_ext}.png"
    
    return dot_file, pdf_file, png_file

def main():
    """Main function to run the script."""
    # Get filenames and person name from command-line arguments
    args = sys.argv[1:]
    input_csv = DEFAULT_INPUT_CSV
    output_dot = DEFAULT_OUTPUT_DOT
    person_name = None
    
    # Parse arguments
    if len(args) >= 1 and args[0] != '--':
        input_csv = args[0]
    if len(args) >= 2 and args[1] != '--':
        output_dot = args[1]
    if len(args) >= 3:
        person_name = args[2]
    
    # Check if input file exists
    if not os.path.isfile(input_csv):
        print(f"Error: Input file '{input_csv}' not found.")
        sys.exit(1)
    
    # Generate proper output filenames
    dot_file, pdf_file, png_file = get_output_filename(output_dot, person_name)
    
    # Read data
    print(f"Reading family data from '{input_csv}'...")
    family_data = read_family_data(input_csv)
    
    # Generate DOT file (either full tree or ancestry)
    if person_name:
        print(f"Generating ancestry tree for '{person_name}' to '{dot_file}'...")
        success = generate_dot_file(family_data, dot_file, person_name)
        if not success:
            print(f"Failed to generate ancestry tree for '{person_name}'.")
            sys.exit(1)
    else:
        print(f"Generating full family tree to '{dot_file}'...")
        generate_dot_file(family_data, dot_file)
    
    # Success message
    file_type = "ancestry tree" if person_name else "family tree"
    print(f"Done! To generate the PDF of the {file_type}, run:")
    print(f"dot -Tpdf {dot_file} -o {pdf_file}")
    print("Or to generate PNG:")
    print(f"dot -Tpng {dot_file} -o {png_file}")

if __name__ == "__main__":
    main()