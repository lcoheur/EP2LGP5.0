import random

# Read the original file
with open('pairs_pt_lgp.txt', 'r') as original_file:
    lines = original_file.readlines()

# Randomly choose 500 lines
random_lines = random.sample(lines, 500)

# Write the randomly chosen lines to a new file
with open('pairs_pt_lgp_test.txt', 'w') as new_file:
    new_file.writelines(random_lines)

# Remove the randomly chosen lines from the original file
remaining_lines = [line for line in lines if line not in random_lines]
with open('pairs_pt_lgp.txt', 'w') as original_file:
    original_file.writelines(remaining_lines)
