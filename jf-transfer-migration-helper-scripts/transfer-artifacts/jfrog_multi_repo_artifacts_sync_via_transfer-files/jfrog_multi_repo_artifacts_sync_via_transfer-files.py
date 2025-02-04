import multiprocessing
import os
import subprocess
import sys
import time
import random
import json
import argparse
import signal
from datetime import datetime
from pathlib import Path

def parse_arguments():
    parser = argparse.ArgumentParser(description='JFrog Artifactory Repository Transfer Tool')
    parser.add_argument('--source', required=True, help='Source Artifactory server ID')
    parser.add_argument('--target', required=True, help='Target Artifactory server ID')
    parser.add_argument('--ignore-state', type=bool, default=False, 
                      help='Ignore previous transfer state (default: False)')
    parser.add_argument('--filestore', type=bool, default=True,
                      help='Transfer filestore data (default: True)')
    parser.add_argument('--jf-path', default='/usr/local/bin/jf',
                      help='Path to JFrog CLI executable (default: /usr/local/bin/jf)')
    parser.add_argument('--threads', type=int, default=50,
                      help='Number of transfer threads (default: 50)')
    parser.add_argument('--timeout', type=int, default=600,
                      help='Timeout in seconds for stuck processes (default: 600)')
    parser.add_argument('--batch-size', type=int, default=4,
                      help='Number of repositories to process in parallel (default: 4)')
    return parser.parse_args()

def is_process_stuck(log_file, timeout):
    """Check if the process is stuck by monitoring log file updates"""
    if not os.path.exists(log_file):
        return False
    
    last_modified = os.path.getmtime(log_file)
    current_time = time.time()
    return (current_time - last_modified) > timeout

def run_command_with_timeout(command, log_file, env_vars, timeout):
    """Run command with timeout and restart if stuck"""
    while True:
        process = subprocess.Popen(command, stdout=open(log_file, 'a'),
                                 stderr=subprocess.STDOUT, env=env_vars)
        
        while process.poll() is None:
            time.sleep(10)
            if is_process_stuck(log_file, timeout):
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                
                banner = "=" * 80
                with open(log_file, 'a') as f:
                    f.write(f"\n{banner}\n")
                    f.write(f"Process appeared stuck. Restarting at {datetime.now()}\n")
                    f.write(f"{banner}\n")
                break
        
        if process.returncode == 0:
            break
        
        banner = "=" * 80
        with open(log_file, 'a') as f:
            f.write(f"\n{banner}\n")
            f.write(f"Process failed with return code {process.returncode} at {datetime.now()}. Retrying...\n")
            f.write(f"{banner}\n")

# Define the worker function
def worker(repo_name, args, log_dir, main_log_file):
    start_time = datetime.now()
    
    with open(main_log_file, 'a') as f:
        f.write(f"\n[{start_time}] Starting transfer for repository: {repo_name}\n")
    
    jfrog_dir = f"{os.path.expanduser('~')}/{args.target}/.jfrog-{repo_name}"

    # Ensure the jfrog directory exists
    os.makedirs(jfrog_dir, exist_ok=True)

    # Copy the .jfrog/config/jfrog-cli.conf.v6 file
    src_config = f"{os.path.expanduser('~')}/.jfrog/jfrog-cli.conf.v6"
    dest_config = f"{jfrog_dir}/jfrog-cli.conf.v6"
    subprocess.run(["cp", src_config, dest_config])

    # Update/create the transfer.conf file
    update_threads(jfrog_dir, args.threads)

    # Define the command
    command = [
        args.jf_path, "rt", "transfer-files", args.source, args.target,
        "--include-repos", repo_name,
        "--ignore-state="+str(args.ignore_state).lower(),
        "--filestore="+str(args.filestore).lower()
    ]

    # Log the command being executed
    command_str = ' '.join(command)
    with open(main_log_file, 'a') as f:
        f.write(f"\n[{datetime.now()}] Executing command for {repo_name}:\n{command_str}\n")
    print(f"\nExecuting command for {repo_name}:\n{command_str}")

    # Execute the command
    log_file = f"{log_dir}/jfrog_{repo_name}.out"
    
    # Log the start time in human-readable format
    with open(log_file, 'w') as f:
        f.write(f"\nStart time {repo_name}: {start_time}\n")

    env_vars = {
        "JFROG_CLI_HOME_DIR": jfrog_dir,
        "JFROG_CLI_LOG_LEVEL": "DEBUG"
    }

    restart_count = 0
    def log_restart():
        nonlocal restart_count
        restart_count += 1
        banner = "=" * 80
        current_time = datetime.now()
        with open(main_log_file, 'a') as f:
            f.write(f"\n{banner}\n")
            f.write(f"[{current_time}] Repository {repo_name} transfer restarted (attempt {restart_count})\n")
            f.write(f"Executing command:\n{command_str}\n")
            f.write(f"{banner}\n")
        with open(log_file, 'a') as f:
            f.write(f"\n{banner}\n")
            f.write(f"[{current_time}] Transfer restart attempt {restart_count}\n")
            f.write(f"Executing command:\n{command_str}\n")
            f.write(f"{banner}\n")

    run_command_with_timeout(command, log_file, env_vars, args.timeout)

    end_time = time.time()  # Record the end time of the process
    total_time = end_time - start_time  # Calculate the total time

    # Log the total runtime
    with open(log_file, 'a') as f:
        f.write(f"\nTotal runtime for {repo_name}: {total_time:.2f} seconds\n")

    end_time = time.time()
    total_time = end_time - start_time
    
    with open(main_log_file, 'a') as f:
        f.write(f"[{datetime.now()}] Completed transfer for repository: {repo_name}\n")
        f.write(f"Total time for {repo_name}: {total_time:.2f} seconds\n")
        if restart_count > 0:
            f.write(f"Number of restarts for {repo_name}: {restart_count}\n")
        f.write("-" * 80 + "\n")

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
def process_in_batches(tasks, args, log_dir, main_log_file):
    for i in range(0, len(tasks), args.batch_size):
        batch = tasks[i:i + args.batch_size]
        with open(main_log_file, 'a') as f:
            f.write(f"\n[{datetime.now()}] Processing batch {i//args.batch_size + 1} of {(len(tasks) + args.batch_size - 1)//args.batch_size}\n")
            f.write(f"Repositories in this batch: {', '.join(batch)}\n")
        
        with multiprocessing.Pool(processes=args.batch_size) as pool:
            pool.starmap(worker, [(repo, args, log_dir, main_log_file) for repo in batch])

# Function to read the list of repositories from a file
def read_list_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return [line.strip() for line in lines]

# Main function to set up tasks and call the batch handler
def main():
    start_time = time.time()
    args = parse_arguments()

    # Create main log file in script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_log_file = os.path.join(script_dir, f"transfer_main_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    with open(main_log_file, 'w') as f:
        f.write(f"JFrog Transfer Process Started at {datetime.now()}\n")
        f.write(f"Source: {args.source}, Target: {args.target}\n")
        f.write("-" * 80 + "\n")

    log_dir = f"logs/jfrog-sync-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(log_dir, exist_ok=True)

    file_path = 'repo_list.txt'
    tasks = read_list_from_file(file_path)
    
    with open(main_log_file, 'a') as f:
        f.write(f"\nFound {len(tasks)} repositories to process\n")
        f.write(f"Processing in batches of {args.batch_size}\n")
        f.write("-" * 80 + "\n")

    process_in_batches(tasks, args, log_dir, main_log_file)

    end_time = time.time()
    total_time = end_time - start_time
    
    with open(main_log_file, 'a') as f:
        f.write(f"\nAll transfers completed at {datetime.now()}\n")
        f.write(f"Total runtime: {total_time:.2f} seconds\n")
    
    print(f"Total runtime of the script: {total_time:.2f} seconds")
    print(f"See detailed log at: {main_log_file}")

if __name__ == "__main__":
    main()
