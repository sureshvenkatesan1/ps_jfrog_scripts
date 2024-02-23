import argparse
import json
'''
python merge_tokens.py access.backup.20240221223922.json UA-DOQ-BELLCA-combined-tokens-022124.json final_tokens.json
'''
def merge_tokens(file1, file2, output_file):
    '''Merge tokens from two JSON files.
    
    Parameters:
    file1 (str): Path to the first JSON file.
    file2 (str): Path to the second JSON file.
    output_file (str): Path to the output merged JSON file.
    '''
    # Load tokens from file1 and file2
    with open(file1, 'r') as f1:
        data1 = json.load(f1)
    with open(file2, 'r') as f2:
        data2 = json.load(f2)
    
    # Extract token IDs from file2
    existing_ids = {token['id'] for token in data2['tokens']}
    
    # Filter tokens from file1 that are not present in file2
    new_tokens = [token for token in data1['tokens'] if token['id'] not in existing_ids]
    
    # Merge data
    merged_data = {
        'version': data1['version'],
        'tokens': new_tokens + data2['tokens']
    }
    
    # Write merged data to output file
    with open(output_file, 'w') as outfile:
        json.dump(merged_data, outfile, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge tokens from two JSON files.")
    parser.add_argument("file1", help="Path to the first JSON file")
    parser.add_argument("file2", help="Path to the second JSON file")
    parser.add_argument("output_file", help="Path to the output merged JSON file")
    args = parser.parse_args()
    
    merge_tokens(args.file1, args.file2, args.output_file)
