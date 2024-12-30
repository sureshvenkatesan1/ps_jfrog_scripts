import multiprocessing
import os
import subprocess
import sys
import time
import random
import json
from datetime import datetime


# Define the worker function
def worker(repo_name, target, env, log_dir):

    jfrog_dir = f"{os.path.expanduser('~')}/{target}/.jfrog-{repo_name}-{env}"

    # Ensure the jfrog directory exists
    os.makedirs(jfrog_dir, exist_ok=True)

    # Copy the .jfrog/config/jfrog-cli.conf.v6 file
    src_config = f"{os.path.expanduser('~')}/.jfrog/jfrog-cli.conf.v6"
    dest_config = f"{jfrog_dir}/jfrog-cli.conf.v6"
    subprocess.run(["cp", src_config, dest_config])

    # Update/create the transfer.conf file
    update_threads(jfrog_dir, thread_number=600)

    # Define the command
    command = [
        "/usr/local/bin/jf", "rt", "transfer-files", "mill", target,
        "--include-repos", repo_name, "--ignore-state=false","--filestore=true"
    ]

    # Execute the command
    log_file = f"{log_dir}/jfrog_{repo_name}_{env}.out"
    #log_file = f"{os.path.expanduser('~')}/{target}/jfrog_{repo_name}_{env}_{datetime.now().strftime('%Y%m%d%H%M%S')}.out"
    start_time = time.time()  # Record the start time of the process

    # Log the total runtime
    with open(log_file, 'w') as f:
        f.write(f"\nStart time {repo_name} : {start_time}\n")

    with open(log_file, 'a') as f:
        subprocess.run(command, stdout=f, stderr=subprocess.STDOUT, env={
            "JFROG_CLI_HOME_DIR": jfrog_dir,
            "JFROG_CLI_LOG_LEVEL": "DEBUG"
        })

    end_time = time.time()  # Record the end time of the process
    total_time = end_time - start_time  # Calculate the total time

    # Log the total runtime
    with open(log_file, 'a') as f:
        f.write(f"\nTotal runtime for {repo_name}: {total_time:.2f} seconds\n")

def update_threads(folder, thread_number=10):
    transfer_dir = os.path.join(folder, "transfer")
    os.makedirs(transfer_dir, exist_ok=True)
    transfer_file = os.path.join(transfer_dir, "transfer.conf")

    transfer = {}
    if os.path.exists(transfer_file):
        with open(transfer_file, "r") as f:
            transfer = json.load(f)

    transfer["threadsNumber"] = thread_number
    with open(transfer_file, "w") as f:
        json.dump(transfer, f, indent=2)


# Function to handle tasks in batches of four
def process_in_batches(tasks, target, env,log_dir,  batch_size=4):
    for i in range(0, len(tasks), batch_size):
        batch = tasks[i:i + batch_size]
        with multiprocessing.Pool(processes=batch_size) as pool:
            pool.starmap(worker, [(repo, target, env, log_dir) for repo in batch])

# Function to read the list of repositories from a file
def read_list_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return [line.strip() for line in lines]

# Main function to set up tasks and call the batch handler
def main():
    start_time = time.time()  # Record the start time of the script
    if len(sys.argv) != 2:
        print("Usage: python script.py <env>")
        print("env: prod or test")
        sys.exit(1)

    env = sys.argv[1]


    if env == "prod":
        target = "psemea"
    elif env == "test":
        target = "psazuse"
    else:
        print(f"Invalid environment: {env}")
        sys.exit(1)

    # Create a log directory with the current date and time
    log_dir = f"logs/jfrog-sync-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(log_dir, exist_ok=True)

    file_path = 'repo_list.txt'  # Replace with your file path
    tasks = read_list_from_file(file_path)
    process_in_batches(tasks, target, env, log_dir)

    end_time = time.time()  # Record the end time of the script
    total_time = end_time - start_time  # Calculate the total time
    print(f"Total runtime of the script: {total_time:.2f} seconds")

if __name__ == "__main__":
    main()
