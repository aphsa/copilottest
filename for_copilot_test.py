#!/usr/bin/python3
import glob
import socket
import subprocess
import csv
import os


def run_command(command):
    """
    Runs a shell command and returns its output as a list of lines.
    """
    try:
        # In Python 3.6, run() returns a CompletedProcess instance
        completed_process = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        # Return the stdout output split into lines
        return completed_process.stdout.splitlines()

    except Exception as e:
        print(f"Error running command: {e}")
        return []


def write_to_csv(file_name, lst):
    with open(file_name, "w") as f:
        writer = csv.writer(f)
        writer.writerows(lst)


def upload_to_s3(file):
    """
    Uploads the diff file to S3 bucket.
    """
    s3_bucket = "s3://infrastructure/dbcache/"
    aws_cmd_prefix = "/usr/local/bin/aws --region us-east-1 s3 cp "
    cmd = aws_cmd_prefix + file + " " + s3_bucket
    print("Uploading %s to %s" % (file, s3_bucket))
    for line in run_command(cmd):
        print(line)


def extract_directories_from_file(filename):
    altfolder = None
    existing = None

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("Alt="):
                altfolder = line.split("=")[1]
            elif line.startswith("Exist="):
                existing = line.split("=")[1]

    return altfolder, existing


def main():
    # Get server's hostname
    server_name = socket.gethostname()
    result_file = "/var/tmp/" + os.uname()[1] + "_journal.csv"

    # Glob for files
    db_files = glob.glob("/sys/*/db.cf")
    cache_files = glob.glob("/sys/*/cache.cf")

    # Combine both lists
    all_files = db_files + cache_files

    # List to store the information
    results = []

    for file in all_files:
        alt_dir, exist = extract_directories_from_file(file)

        results.append([server_name, file, alt_dir, exist])

    if results:
        print("writing to csv %", result_file)
        write_to_csv(result_file, results)
        upload_to_s3(result_file)


if __name__ == "__main__":
    main()
