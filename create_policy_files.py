import os
import glob
import json

# Constants
POLICY_DIR = '.'  # Directory containing the policy files
OUTPUT_DIR = 'output_policies'  # Directory to save the output policy files
CHAR_LIMIT = 6144  # Character limit for each JSON file

# Ensure output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def remove_old_files(output_dir):
    """Remove old JSON files in the output directory."""
    old_files = glob.glob(os.path.join(output_dir, 'inventory_policy_part_*.json'))
    for old_file in old_files:
        os.remove(old_file)
        print(f'Removed old file: {old_file}')

def read_policy_files(policy_dir):
    """Read all inventory_policy* files and merge their actions."""
    policy_files = glob.glob(os.path.join(policy_dir, 'inventory_policy*.json'))
    all_actions = set()  # Use a set to remove duplicates

    for policy_file in policy_files:
        with open(policy_file, 'r') as f:
            policy = json.load(f)
            for statement in policy.get('Statement', []):
                all_actions.update(statement.get('Action', []))

    return list(all_actions)

def split_actions_into_policies(actions, char_limit):
    """Split actions into multiple policies based on character limit."""
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
    """Save each policy to a separate JSON file."""
    for i, policy in enumerate(policies):
        output_file = os.path.join(output_dir, f'inventory_policy_part_{i+1}.json')
        with open(output_file, 'w') as f:
            json.dump(policy, f, indent=4)
        print(f'Saved {output_file}')

def main():
    remove_old_files(OUTPUT_DIR)
    all_actions = read_policy_files(POLICY_DIR)
    policies = split_actions_into_policies(all_actions, CHAR_LIMIT)
    save_policies(policies, OUTPUT_DIR)

if __name__ == "__main__":
    main()