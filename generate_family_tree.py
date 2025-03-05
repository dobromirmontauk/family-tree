#!/usr/bin/env python3
"""
Family Tree Generator
--------------------
This script reads family data from a CSV file and generates a DOT file
for GraphViz to visualize the family tree.

Usage:
    python generate_family_tree.py [input_csv] [output_dot]

    Default input_csv: family_data_improved.csv
    Default output_dot: generated_family_tree.dot
"""

import csv
import sys
import os
from collections import defaultdict

# Default filenames
DEFAULT_INPUT_CSV = "family_data_improved.csv"
DEFAULT_OUTPUT_DOT = "generated_family_tree.dot"

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

def generate_dot_file(family_data, output_filename):
    """Generate DOT file for GraphViz."""
    generations = organize_by_generation(family_data)
    
    # Create mapping of names to IDs
    id_mapping = {}
    for person in family_data:
        name = person['Full Name']
        find_person_id(name, id_mapping)
    
    # Track marriages and parent-child relationships
    marriages = []
    parent_child = defaultdict(list)
    
    # Find marriages and children
    for person in family_data:
        person_id = find_person_id(person['Full Name'], id_mapping)
        
        # Process spouses
        for i in range(1, 3):  # Spouse 1 and Spouse 2
            spouse_key = f'Spouse {i}'
            if spouse_key in person and person[spouse_key].strip('"'):
                spouse_name = person[spouse_key].strip('"')
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
                child_id = find_person_id(child_name, id_mapping)
                
                # Add parent-child relationship
                if person_id not in parent_child[child_id]:
                    parent_child[child_id].append(person_id)
    
    # Start generating the DOT file
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write('digraph FamilyTree {\n')
        f.write('    // Graph settings\n')
        f.write('    rankdir=TB;\n')
        f.write('    nodesep=0.8;\n')
        f.write('    ranksep=1.2;\n')
        f.write('    splines=ortho;\n')
        f.write('    \n')
        f.write('    // Title for the family tree\n')
        f.write('    labelloc="t";\n')
        f.write('    label="Family Tree";\n')
        f.write('    fontsize=24;\n')
        f.write('    \n')
        
        # Generate nodes by generation
        for gen_num, gen_people in sorted(generations.items()):
            gen_color = GENERATION_COLORS[(gen_num - 1) % len(GENERATION_COLORS)]
            
            f.write(f'    // Generation {gen_num}\n')
            f.write(f'    subgraph cluster_gen{gen_num} {{\n')
            f.write(f'        label="Generation {gen_num}";\n')
            f.write(f'        style=filled;\n')
            f.write(f'        color="{gen_color}";\n')
            f.write(f'        fontsize=16;\n')
            f.write('\n')
            
            # Add person nodes for this generation
            for person in gen_people:
                person_id = find_person_id(person['Full Name'], id_mapping)
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

def main():
    """Main function to run the script."""
    # Get filenames from command-line arguments
    input_csv = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT_CSV
    output_dot = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT_DOT
    
    # Check if input file exists
    if not os.path.isfile(input_csv):
        print(f"Error: Input file '{input_csv}' not found.")
        sys.exit(1)
    
    # Read data and generate DOT file
    print(f"Reading family data from '{input_csv}'...")
    family_data = read_family_data(input_csv)
    
    print(f"Generating DOT file '{output_dot}'...")
    generate_dot_file(family_data, output_dot)
    
    print("Done! To generate the PDF, run:")
    print(f"dot -Tpdf {output_dot} -o family_tree.pdf")
    print("Or to generate PNG:")
    print(f"dot -Tpng {output_dot} -o family_tree.png")

if __name__ == "__main__":
    main()