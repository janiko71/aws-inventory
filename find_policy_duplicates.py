import json

def find_duplicates(policy_file_path):
    """
    Find duplicate actions in the IAM policy file.

    Args:
        policy_file_path (str): The path to the IAM policy file.

    Returns:
        list: A list of duplicate actions found in the policy file.
    """
    with open(policy_file_path, 'r') as file:
        policy = json.load(file)

    actions = policy['Statement'][0]['Action']
    action_counts = {}
    duplicates = []

    for action in actions:
        if action in action_counts:
            action_counts[action] += 1
        else:
            action_counts[action] = 1

    for action, count in action_counts.items():
        if count > 1:
            duplicates.append(action)

    return duplicates

# Path to the policy file
policy_file_path = 'inventory_policy_1.json'

# Find duplicates
duplicates = find_duplicates(policy_file_path)

# Print the duplicates
if duplicates:
    print("Duplicate actions found in the policy file:")
    for action in duplicates:
        print(action)
else:
    print("No duplicate actions found in the policy file.")