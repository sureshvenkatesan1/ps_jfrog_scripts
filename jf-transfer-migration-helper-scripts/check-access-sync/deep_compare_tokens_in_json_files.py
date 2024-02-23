import argparse
import json

def compare_tokens(file1: str, file2: str) -> dict:
    '''Compare tokens between two JSON files.
    
    This function compares the tokens between two JSON files. It reads the
    contents of both files, compares each token individually, and returns a
    report detailing the differences between tokens with the same ID, ignoring
    the 'projectKey' attribute if it is missing in one file and exists but
    is null in the other file.
    
    Parameters:
        file1 (str): Path to the first JSON file.
        file2 (str): Path to the second JSON file.
    
    Returns:
        dict: A dictionary containing token IDs as keys and their differences
              as values.
    '''
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)
    
    differences = {}
    
    # Group tokens by ID
    tokens1 = {token['id']: token for token in data1['tokens']}
    tokens2 = {token['id']: token for token in data2['tokens']}
    
    # Compare tokens with the same ID
    for id in set(tokens1.keys()) & set(tokens2.keys()):
        # Check if 'projectKey' exists and is null in one file but missing in the other
        if 'projectKey' in tokens1[id] and tokens1[id]['projectKey'] is None and 'projectKey' not in tokens2[id]:
            del tokens1[id]['projectKey']
        if 'projectKey' in tokens2[id] and tokens2[id]['projectKey'] is None and 'projectKey' not in tokens1[id]:
            del tokens2[id]['projectKey']
        
        if tokens1[id] != tokens2[id]:
            differences[id] = {'file1': tokens1[id], 'file2': tokens2[id]}
    
    return differences

def main():
    '''Main function to compare tokens between two JSON files.'''
    parser = argparse.ArgumentParser(description="Compare tokens between two JSON files.")
    parser.add_argument("file1", type=str, help="Path to the first JSON file")
    parser.add_argument("file2", type=str, help="Path to the second JSON file")
    args = parser.parse_args()
    
    differences = compare_tokens(args.file1, args.file2)
    
    if differences:
        print("Differences found between tokens with the same ID:")
        for id, diff in differences.items():
            print(f"Token ID: {id}")
            print("Difference in file 1:")
            print(json.dumps(diff['file1'], indent=4))
            print("Difference in file 2:")
            print(json.dumps(diff['file2'], indent=4))
            print()
        print(f"Total count of tokens with differences: {len(differences)}")
    else:
        print("No differences found between tokens with the same ID.")

if __name__ == "__main__":
    main()
