import os
import glob
import json

# Constants
POLICY_DIR = 'policies'  # Directory containing the policy files
OUTPUT_DIR = 'output_policies'  # Directory to save the output policy files
CHAR_LIMIT = 6144  # Character limit for each JSON file
EXTRA_SERVICE_CALLS_FILE = os.path.join(POLICY_DIR, 'extra_service_calls.json')  # File containing extra service calls

# Ensure output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def remove_old_files(output_dir):
    """
    Remove old JSON files in the output directory.

    Args:
        output_dir (str): The directory where old files are located.
    """
    old_files = glob.glob(os.path.join(output_dir, 'inventory_policy_part_*.json'))
    for old_file in old_files:
        os.remove(old_file)
        print(f'Removed old file: {old_file}')

def read_policy_files(policy_dir):
    """
    Read all inventory_policy* files and merge their actions.

    Args:
        policy_dir (str): The directory containing the policy files.

    Returns:
        list: A list of all unique actions from the policy files.
    """
    policy_files = glob.glob(os.path.join(policy_dir, 'inventory_policy*.json'))
    all_actions = set()  # Use a set to remove duplicates

    for policy_file in policy_files:
        with open(policy_file, 'r') as f:
            policy = json.load(f)
            for statement in policy.get('Statement', []):
                all_actions.update(statement.get('Action', []))

    return list(all_actions)

def read_extra_permissions(extra_service_calls_file):
    """
    Read extra permissions from the extra_service_calls.json file.

    Args:
        extra_service_calls_file (str): The path to the extra_service_calls.json file.

    Returns:
        list: A list of extra permissions required by the services.
    """
    with open(extra_service_calls_file, 'r') as f:
        extra_service_calls = json.load(f)
    
    extra_permissions = set()
    for service, config in extra_service_calls.items():
        if 'required_permission' in config:
            extra_permissions.add(config['required_permission'])
        else:
            for sub_key, sub_config in config.items():
                if isinstance(sub_config, dict) and 'required_permission' in sub_config:
                    extra_permissions.add(sub_config['required_permission'])
    
    return list(extra_permissions)

def split_actions_into_policies(actions, char_limit):
    """
    Split actions into multiple policies based on character limit.

    Args:
        actions (list): A list of actions to be included in the policies.
        char_limit (int): The character limit for each JSON policy file.

    Returns:
        list: A list of policies, each within the character limit.
    """
    policies = []
    current_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [],
                "Resource": "*"
            }
        ]
    }
    current_length = len(json.dumps(current_policy))

    for action in actions:
        action_length = len(json.dumps(action)) + 2  # Adding 2 for the comma and quotes
        if current_length + action_length > char_limit:
            policies.append(current_policy)
            current_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [],
                        "Resource": "*"
                    }
                ]
            }
            current_length = len(json.dumps(current_policy))

        current_policy["Statement"][0]["Action"].append(action)
        current_length += action_length

    if current_policy["Statement"][0]["Action"]:
        policies.append(current_policy)

    return policies

def save_policies(policies, output_dir):
    """
    Save each policy to a separate JSON file.

    Args:
        policies (list): A list of policies to be saved.
        output_dir (str): The directory where the policy files will be saved.
    """
    for i, policy in enumerate(policies):
        output_file = os.path.join(output_dir, f'inventory_policy_part_{i+1}.json')
        with open(output_file, 'w') as f:
            json.dump(policy, f, indent=4)
        print(f'Saved {output_file}')

def main():
    """
    Main function to read policy files, merge actions, read extra permissions,
    split actions into policies, and save the policies to JSON files.
    """
    # Remove old policy files
    remove_old_files(OUTPUT_DIR)
    
    # Read actions from policy files
    all_actions = read_policy_files(POLICY_DIR)
    
    # Read extra permissions from extra_service_calls.json
    extra_permissions = read_extra_permissions(EXTRA_SERVICE_CALLS_FILE)
    
    # Combine all actions and extra permissions
    all_actions.extend(extra_permissions)
    
    # Sort actions alphabetically
    all_actions = sorted(all_actions)
    
    # Split actions into multiple policies based on character limit
    policies = split_actions_into_policies(all_actions, CHAR_LIMIT)
    
    # Save the policies to JSON files
    save_policies(policies, OUTPUT_DIR)

if __name__ == "__main__":
    main()