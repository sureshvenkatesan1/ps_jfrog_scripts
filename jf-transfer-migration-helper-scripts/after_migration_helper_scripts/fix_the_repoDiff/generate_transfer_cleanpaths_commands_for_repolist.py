import argparse

def generate_commands(repo_list):
    repos = repo_list.split(';')
    for repo in repos:
        command = f"python3 /home/sureshv/comparison_report/transfer_cleanpaths_delta_from_repoDiff.py \\\n" \
                  f"/home/sureshv/comparison_report/output/{repo}/cleanpaths.txt \\\n" \
                  f"source-server {repo} target-server {repo}\n\n"
        print(command)

def main():
    parser = argparse.ArgumentParser(description="Generate commands for transferring clean paths.")
    parser.add_argument('repo_list', help="A semicolon-separated list of repositories")

    args = parser.parse_args()
    generate_commands(args.repo_list)

if __name__ == "__main__":
    main()
