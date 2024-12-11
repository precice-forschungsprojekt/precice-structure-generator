import sys
import os
import re

def format_precice_config(input_file, output_file=None):
    """
    Format a preCICE configuration XML file to improve readability.
    
    Args:
        input_file (str): Path to the input XML file
        output_file (str, optional): Path to the output XML file. If None, overwrites input file.
    """
    # Read the entire file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Predefined tag order for better readability
    tag_order = [
        'log', 
        'data:vector', 
        'mesh', 
        'participant', 
        'm2n:sockets', 
        'coupling-scheme:parallel-implicit'
    ]
    
    # Split the content into lines
    lines = content.split('\n')
    
    # Group lines by their tag type
    tag_groups = {}
    current_group = []
    current_tag = None
    
    # Separate XML declaration and first line
    formatted_lines = [lines[0]]
    
    # Process remaining lines
    for line in lines[1:]:
        stripped = line.strip()
        
        # Identify tag type
        if stripped.startswith('<') and not stripped.startswith('<!--') and not stripped.startswith('<?'):
            # Extract tag name (handle both opening and closing tags)
            tag_match = re.match(r'</?([^> ]+)', stripped)
            if tag_match:
                tag = tag_match.group(1).split(':')[-1]
                
                # If tag changes, add previous group with newline
                if current_tag and tag != current_tag:
                    formatted_lines.extend(current_group)
                    formatted_lines.append('')  # Add empty line between tag groups
                    current_group = []
                
                current_tag = tag
        
        # Collect lines for current group
        current_group.append(line)
    
    # Add last group
    if current_group:
        formatted_lines.extend(current_group)
    
    # Combine lines
    formatted_content = '\n'.join(formatted_lines)
    
    # Determine output file
    write_file = output_file if output_file else input_file
    
    # Write formatted content
    with open(write_file, 'w', encoding='utf-8') as f:
        f.write(formatted_content)
    
    print(f"Formatted XML saved to {write_file}")

def main():
    # Set default input and output file paths
    default_input_file = os.path.join(os.path.dirname(__file__), '_generated', 'config', 'precice-config.xml')
    default_output_file = os.path.join(os.path.dirname(__file__), '_generated', 'config', 'precice-config_better_read.xml')
    
    # Determine input file
    input_file = sys.argv[1] if len(sys.argv) > 1 else default_input_file
    
    # Determine output file
    output_file = sys.argv[2] if len(sys.argv) > 2 else default_output_file
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Validate input file
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} does not exist.")
        sys.exit(1)
    
    # Format the config
    format_precice_config(input_file, output_file)

if __name__ == '__main__':
    main()
