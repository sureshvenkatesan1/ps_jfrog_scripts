import argparse
import json
import os

def extract_version_and_tokens(json_file):
    # Load JSON data from file
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Create a new dictionary with only "version" and "tokens"
    extracted_data = {"version": data.get("version", ""), "tokens": data.get("tokens", [])}

    # Create modified filename
    base_filename, extension = os.path.splitext(json_file)
    modified_filename = f"{base_filename}_modified{extension}"

    # Save extracted data to file
    with open(modified_filename, 'w') as f:
        json.dump(extracted_data, f, indent=2)

    print(f"Extracted data saved to {modified_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract version and tokens from JSON file")
    parser.add_argument("json_file", help="Path to JSON file")
    args = parser.parse_args()

    extract_version_and_tokens(args.json_file)
