import json
from sklearn.model_selection import train_test_split

input_file = "validation.json"
val_file = "val.json"
test_file = "test.json"

# Load data from input file
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Split data into training and test sets
train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)

# Write training data to file
with open(val_file, "w", encoding="utf-8") as f:
    json.dump(train_data, f, indent=4, ensure_ascii=False)

# Write test data to file
with open(test_file, "w", encoding="utf-8") as f:
    json.dump(test_data, f, indent=4, ensure_ascii=False)
