import argparse
import json
import re

def extract_unique_ids(json_file):
    """
    Extracts unique IDs from JSON data.

    Args:
    json_file (str): Path to the JSON file.

    Returns:
    dict: Dictionary containing unique IDs for each type of pattern.
    """
    with open(json_file, 'r') as file:
        data = json.load(file)

    unique_ids_jf_artifactory = set()
    unique_ids_jfrt = set()

    pattern_jf_artifactory = r'jf-artifactory@([\w-]+)'
    pattern_jfrt = r'jfrt@([\w-]+)'

    for token in data.get('tokens', []):
        if token is not None:
            # Extract unique IDs for pattern 'jf-artifactory@'
            subject_strings = []
            subject_strings.append(token.get("subject"))
            subject_strings.append(token.get("owner"))
            if token.get("payload") is not None:
                subject_strings.append(token["payload"].get("subject"))
                subject_strings.append(token["payload"].get("issuer"))
            for subject_string in subject_strings:
                if subject_string:
                    matches = re.findall(pattern_jf_artifactory, subject_string)
                    for match in matches:
                        unique_ids_jf_artifactory.add(match)

            # Extract unique IDs for pattern 'jfrt@'
            for subject_string in subject_strings:
                if subject_string:
                    matches = re.findall(pattern_jfrt, subject_string)
                    for match in matches:
                        unique_ids_jfrt.add(match)

    return {
        'jf_artifactory': unique_ids_jf_artifactory,
        'jfrt': unique_ids_jfrt
    }




def main():
    """
    Main function to parse command-line arguments and execute the program.
    """
    parser = argparse.ArgumentParser(description='Extract unique IDs from JSON data')
    parser.add_argument('json_file', type=str, help='Path to the JSON file')
    args = parser.parse_args()

    unique_ids = extract_unique_ids(args.json_file)
    print("Unique IDs for 'jf-artifactory@':", unique_ids['jf_artifactory'])
    print("Unique IDs for 'jfrt@':", unique_ids['jfrt'])

if __name__ == "__main__":
    main()
