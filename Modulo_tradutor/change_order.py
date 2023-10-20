# Replace these file paths with the actual paths to your input and output files
input_file_path = 'new_training_file.txt'
output_file_path = 'changed_file.txt'

# Open the input and output files
with open(input_file_path, 'r') as input_file, open(output_file_path, 'w') as output_file:
    # Loop through each line in the input file
    for line in input_file:
        # Split the line by the tab character
        parts = line.strip().split('\t')
        # Reverse the parts and join them back together with a tab character
        reversed_line = '\t'.join(reversed(parts))
        # Write out the reversed line to the output file
        output_file.write(reversed_line + '\n')
