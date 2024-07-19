import requests
import datetime
import argparse
import json

def main(source_jpd_url, jpd_token, days_left, filename, include_subject):
    headers = {
        'user-agent': "vscode-restclient",
        'authorization': f"Bearer {jpd_token}"
    }

    data = requests.get(f"{source_jpd_url}/access/api/v1/tokens", headers=headers).json()
    # print(json.dumps(data, indent=4))

    with open(filename, 'w') as token_expiry_list:
        for i in data['tokens']:
            token_id = i['token_id']
            subject = i['subject'].split('/')[-1] if include_subject else None  # Extracting the last part of the subject if required
            print("\nChecking for Token ID ==> ", token_id)

            response = requests.get(f"{source_jpd_url}/access/api/v1/tokens/{token_id}", headers=headers).json()

            try:
                if response['expiry']:
                    time_left = datetime.datetime.fromtimestamp(response['expiry']) - datetime.datetime.now()
                    print("Expiry Days = ", time_left)
                    if time_left.days < days_left:
                        print(f"The expiry date is less than {days_left} days")
                        if include_subject:
                            token_expiry_list.write(f"{token_id}\t{subject}\n")  # Writing in tab-separated format
                        else:
                            token_expiry_list.write(f"{token_id}\n")
            except KeyError:
                print("No Expiry Date Set for token ==> ", token_id)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check Access Token Expiry')
    parser.add_argument('--source-jpd-url', type=str, required=True, help='Source JPD URL')
    parser.add_argument('--jpd-token', type=str, required=True, help='JPD Token')
    parser.add_argument('--days-left', type=int, required=True, help='Number of days left for token expiry')
    parser.add_argument('--filename', type=str, default='token_less_days.txt', help='Output filename')
    parser.add_argument('--include-subject', action='store_true', help='Include the last part of the subject in the output')

    args = parser.parse_args()
    main(args.source_jpd_url, args.jpd_token, args.days_left, args.filename, args.include_subject)
