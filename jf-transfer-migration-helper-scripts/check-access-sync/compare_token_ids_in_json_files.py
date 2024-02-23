import argparse
import json

def compare_token_ids(file1, file2):
    '''Compare token IDs between two JSON files.
    
    Parameters:
    file1 (str): Path to the first JSON file.
    file2 (str): Path to the second JSON file.
    
    Returns:
    bool: True if the token IDs are the same, False otherwise.
    '''
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)
    
    # Extract token IDs from both files
    token_ids_1 = {token['id'] for token in data1['tokens']}
    token_ids_2 = {token['id'] for token in data2['tokens']}
    
    # Compare sets of token IDs
    return token_ids_1 == token_ids_2

def main():
    '''Main function to compare token IDs between two JSON files.'''
    parser = argparse.ArgumentParser(description="Compare token IDs between two JSON files.")
    parser.add_argument("file1", help="Path to the first JSON file")
    parser.add_argument("file2", help="Path to the second JSON file")
    args = parser.parse_args()
    
    if compare_token_ids(args.file1, args.file2):
        print("Both JSON files have the same token IDs.")
    else:
        print("JSON files have different token IDs.")

if __name__ == "__main__":
    main()
