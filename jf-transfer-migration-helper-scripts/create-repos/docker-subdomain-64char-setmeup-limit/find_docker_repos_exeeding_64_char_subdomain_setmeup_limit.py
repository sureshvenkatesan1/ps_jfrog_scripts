import json
import argparse

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def filter_repositories(customer_name, repos):
    result = []
    for repo in repos:
        full_name = f"{customer_name}-{repo}"
        # print(f"Repository: {full_name}, Length: {len(full_name)}")
        if len(full_name) > 64:
            result.append((repo, len(full_name)))
    return result

def main():
    parser = argparse.ArgumentParser(description="Filter Docker repositories by length for AWS Route 53")
    parser.add_argument("json_file", help="Path to the JSON file with repository names")
    parser.add_argument("customer_name", help="Customer name to prepend to repository names")

    args = parser.parse_args()

    repos = load_json(args.json_file)
    filtered_repos = filter_repositories(args.customer_name, repos)
    print("AWS Route 53 restricts the length of the top-level domain to 64 characters. This means that the combined length of the server name and repository name (<servername-reponame>) cannot exceed 64 characters.")
    print("Here are the repos that have this limit:")
    for repo, length in filtered_repos:
        print(f"Repository: {repo} , Subdomain: {args.customer_name}-{repo}, Length: {length}")

if __name__ == "__main__":
    main()
