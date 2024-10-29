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
        set: A set of unique resources and services that encountered errors.
    """
    
    error_services = set()  # Set to store unique error services

    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            # Check if the line contains an error or exception
            if "Error" in line or "Exception" in line:
                print(f"Found error line: {line.strip()}")  # Debugging line
                
                # Extract the resource name and service name from the error message
                if "querying" in line:
                    resource_name = line.split("querying")[1].split()[0].strip()
                if "using" in line:
                    service_name = line.split("using")[1].split()[0].strip()
                    print(f"Extracted resource name: {resource_name}, service name: {service_name}")  # Debugging line
                    
                    # Add the resource and service to the set
                    error_services.add(f"{resource_name}:{service_name}")

    return error_services

# ------------------------------------------------------------------------------

# Analyze the log file
error_services = sorted(analyze_log_file(log_file_path))

# ------------------------------------------------------------------------------

# Print the unique resources and services that encountered errors
if error_services:
    print("Resources and services that encountered errors:")
    for service in error_services:
        print(service)
else:
    print("No errors found in the log file.")

# ------------------------------------------------------------------------------