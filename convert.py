import json
import yaml
import glob
import os

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def convert_to_yaml(policy_json, extra_service_json, service_name, output_yaml_path):
    yaml_data = {
        service_name: {
            'boto_resource_name': service_name,
            'region_type': 'local',  # Assuming 'local' for all, adjust if needed
            'list_function': {
                'permissions': [action.split(':')[1] for action in policy_json['Statement'][0]['Action']],
                'item_key': extra_service_json.get(service_name, {}).get('item_key', ''),
                'item_search_id': extra_service_json.get(service_name, {}).get('item_search_id', ''),
                'details': {
                    key: {
                        'detail_function': value['detail_function'],
                        'detail_param': value['detail_param'],
                        'result_key': value['result_key'],
                        'detail_permission': value['required_permission']
                    } for key, value in extra_service_json.get(service_name, {}).items() if isinstance(value, dict)
                }
            }
        }
    }
    
    with open(output_yaml_path, 'w') as yaml_file:
        yaml.dump(yaml_data, yaml_file, default_flow_style=False)

def main():
    policy_files = glob.glob('policies/inventory_policy_local_*.json')
    extra_service_file = 'policies/extra_service_calls.json'
    extra_service_data = load_json(extra_service_file)
    
    for policy_file in policy_files:
        service_name = os.path.basename(policy_file).replace('inventory_policy_local_', '').replace('.json', '')
        output_yaml_file = f'policies/inventory_{service_name}.yaml'
        
        policy_data = load_json(policy_file)
        
        convert_to_yaml(policy_data, extra_service_data, service_name, output_yaml_file)
        
        print(f'Converted {policy_file} and {extra_service_file} to {output_yaml_file}')

if __name__ == "__main__":
    main()