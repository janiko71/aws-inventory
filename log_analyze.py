def analyze_log_file(log_file_path):
    """
    Analyze the log file to identify services that encountered errors.

    Args:
        log_file_path (str): The path to the log file.

    Returns:
        set: A set of unique services that encountered errors.
    """
    error_services = set()

    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            if "Error" in line or "Exception" in line:
                print(f"Found error line: {line.strip()}")  # Debugging line
                # Extract the service name from the error message
                if "using" in line:
                    service_name = line.split("using")[1].split()[0].strip()
                    print(f"Extracted service name: {service_name}")  # Debugging line
                    error_services.add(service_name)

    return error_services

# Path to the log file
log_file_path = 'log/log_20241027_192917.log'

# Analyze the log file
error_services = analyze_log_file(log_file_path)

# Print the unique services that encountered errors
if error_services:
    print("Services that encountered errors:")
    for service in error_services:
        print(service)
else:
    print("No errors found in the log file.")