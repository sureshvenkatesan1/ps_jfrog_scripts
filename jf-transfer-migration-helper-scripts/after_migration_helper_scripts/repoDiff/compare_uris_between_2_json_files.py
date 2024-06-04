import json
import argparse
# python compare_uris_between_2_json_files.py /tmp/source.log  /tmp/target.log
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def extract_uris(json_data):
    uris = set()
    if 'uri' in json_data:
        uris.add(json_data['uri'])
    if 'files' in json_data:
        for file in json_data['files']:
            if 'uri' in file:
                uris.add(file['uri'])
    return uris

def compare_uris(file1_uris, file2_uris):
    return file1_uris - file2_uris

def main():
    parser = argparse.ArgumentParser(description="Compare URIs in two JSON files.")
    parser.add_argument('file1', type=str, help="Path to the first JSON file.")
    parser.add_argument('file2', type=str, help="Path to the second JSON file.")

    args = parser.parse_args()

    # Load JSON files
    json_data1 = load_json(args.file1)
    json_data2 = load_json(args.file2)

    # Extract URIs
    uris_file1 = extract_uris(json_data1)
    uris_file2 = extract_uris(json_data2)

    # Print counts of URIs
    print(f"Count of URIs in {args.file1}: {len(uris_file1)}")
    print(f"Count of URIs in {args.file2}: {len(uris_file2)}")

    # Compare URIs
    unique_uris = compare_uris(uris_file1, uris_file2)

    if unique_uris:
        print("URIs in file1 but not in file2:")
        for uri in unique_uris:
            print(uri)
    else:
        print("All URIs in file1 are also in file2.")

if __name__ == "__main__":
    main()
