import argparse
import random
from datasets import DatasetDict, Dataset
import pickle

parser = argparse.ArgumentParser()
parser.add_argument('train_file', help='path to the training file')
parser.add_argument('val_test_file', help='path to the validation and test file')
args = parser.parse_args()

train_pairs = []
with open(args.train_file, 'r', encoding='utf-8') as f:
    for line in f:
        ept, lgp = line.strip().split('\t')
        train_pairs.append({'ept': ept, 'lgp': lgp}) #ept = european portuguese ; lgp = lingua gestual portuguesa

val_pairs = []
test_pairs = []
with open(args.val_test_file, 'r', encoding='utf-8') as f:
    pairs = [line.strip().split('\t') for line in f]
    random.shuffle(pairs)
    split_index = int(len(pairs) * 0.8)
    val_pairs = [{'ept': ept, 'lgp': lgp} for ept, lgp in pairs[:split_index]]
    test_pairs = [{'ept': ept, 'lgp': lgp} for ept, lgp in pairs[split_index:]]

train_dataset = Dataset.from_dict({'translation': train_pairs})
val_dataset = Dataset.from_dict({'translation': val_pairs})
test_dataset = Dataset.from_dict({'translation': test_pairs})

dataset_dict = DatasetDict({
    'train': train_dataset,
    'validation': val_dataset,
    'test': test_dataset
})


output_file = 'dataset_pre_processed_elan.pkl'

with open(output_file, 'wb') as f:
    pickle.dump(dataset_dict, f)
