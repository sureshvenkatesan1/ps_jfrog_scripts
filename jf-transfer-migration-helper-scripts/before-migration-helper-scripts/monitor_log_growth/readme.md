

# Log File Growth Monitor Script

## Description

This Bash script monitors the growth of log files within a specified directory for a custom-defined period of time. It allows you to check whether the log files have increased in size during the specified time frame.
Purpose :  to determine if your script that writes to the log file has completed, as the log file did not grow.


## Usage

To use the script, follow these instructions:

1. Ensure you have Bash installed on your system.

2. Make the script executable (if not already):

   ```bash
   chmod +x monitor_log_growth.sh
   ```

3. Run the script with the following command:

   ```bash
   ./monitor_log_growth.sh <log_directory> <log_file_pattern> <sleep_duration_seconds>
   ```

   - `<log_directory>`: The directory containing the log files you want to monitor for growth.
   - `<log_file_pattern>`: The pattern to match log files within the directory. Use single quotes around the pattern to prevent shell expansion.
   - `<sleep_duration_seconds>`: The duration in seconds for which the script will monitor log file growth.

4. The script will display whether each log file has grown in size during the specified monitoring period.

## Example

```bash
./monitor_log_growth.sh /path/to/your/log/directory 'upload-session*.log' 60
```

In this example, the script will monitor the specified log files for growth over a 60-second period.

## Notes

- Ensure that the provided `<log_directory>` exists before running the script.
- If no log files are found matching the specified pattern in the given directory, the script will report that no files were found.
- The script uses the `stat` command to determine file sizes, so it should work on Unix-like systems.

