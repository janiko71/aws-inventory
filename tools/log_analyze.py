import os
import glob

# ------------------------------------------------------------------------------

# Get the most recent log file in the log directory
log_dir = 'log'
list_of_files = glob.glob(os.path.join(log_dir, 'log_*.log'))
log_file_path = max(list_of_files, key=os.path.getctime)

# ------------------------------------------------------------------------------

def analyze_log_file(log_file_path):
    """
    Analyze the log file to identify services that encountered errors.

    Args:
        log_file_path (str): The path to the log file.

    Returns:
        set: A set of unique resources, services, and error messages that encountered errors.
    """
    
    error_services = set()  # Set to store unique error services

    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            # Check if the line contains an error or exception
             
                # Extract the resource name, service name, and error message from the error line
                if "querying" in line:
                    resource_name = line.split("querying")[1].split()[0].strip()
                if "using" in line:
                    service_name = line.split("using")[1].split()[0].strip().rstrip(':')
                if (f"{service_name}:" in line):
                    error_message = line.split(f"{service_name}:")[1].strip()
                    
                    # Add the resource, service, and error message to the set
                    error_services.add((resource_name, service_name, error_message))

    return error_services

# ------------------------------------------------------------------------------

# Analyze the log file
error_services = sorted(analyze_log_file(log_file_path))

# ------------------------------------------------------------------------------

# Print the unique resources, services, and error messages that encountered errors
if error_services:
    print("Resources, services, and error messages that encountered errors:")
    for resource, service, error_message in error_services:
        print(f"{resource}:{service} - {error_message}")
else:
    print("No errors found in the log file.")

# ------------------------------------------------------------------------------