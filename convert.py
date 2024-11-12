import json
import yaml
import os
from utils import transform_function_name

# Lire le fichier service_structure.json
with open('service_structure.json', 'r') as f:
    service_structure = json.load(f)

def convert_json_to_yaml(policy_data):
    """
    Convertit le contenu JSON en YAML.
    """
    global service_structure

    yaml_content = {}
    scope = policy_data.get('scope', 'local')
    for statement in policy_data.get('Statement', []):
        actions = statement.get('Action', [])

        for action in actions:
            resource_name, permission = action.split(':')
            if resource_name not in yaml_content:
                yaml_content[resource_name] = []
                yaml_content[resource_name].append({'region_type': scope})
                yaml_content[resource_name].append({'boto_resource_name': resource_name})
                
                # Ajouter l'élément 'category' correspondant à la catégorie présente dans service_structure
                category = service_structure.get(resource_name, {})
                yaml_content[resource_name].append({'category': category})

                # Ajouter le niveau 'inventory_nodes' pour chaque ressource
                if 'inventory_nodes' not in yaml_content[resource_name]:
                    yaml_content[resource_name].append({'inventory_nodes': []})
            
            # Ajouter l'élément 'list_function' sous 'inventory_nodes'
            list_function = transform_function_name(permission)
            yaml_content[resource_name][-1]['inventory_nodes'].append({list_function: []})

            current_node = yaml_content[resource_name][-1]['inventory_nodes'][-1][list_function]

            # Préparer les éléments suivants
            current_node.append({'permissions': permission})
            current_node.append({'item_key': ""})
            current_node.append({'item_search_id': ""})
            current_node.append({'detail_param': ""})
            current_node.append({'result_key': ""})

    return yaml.dump(yaml_content, default_flow_style=False, allow_unicode=True)

# Répertoires d'entrée et de sortie
input_dir = 'policies'
output_dir = 'resources_converted'

# Créer le répertoire de sortie s'il n'existe pas
os.makedirs(output_dir, exist_ok=True)

# Parcourir les fichiers inventory_policy....json dans le répertoire d'entrée
for filename in os.listdir(input_dir):
    if filename.startswith('inventory_policy') and filename.endswith('.json'):
        print(f"Traitement du fichier : {filename}")
        
        # Lire le fichier inventory_policy....json
        with open(os.path.join(input_dir, filename), 'r') as f:
            policy_data = json.load(f)
        
        # Convertir le contenu JSON en YAML
        if 'global' in filename:
            policy_data['scope'] = 'global'
        elif 'local' in filename:
            policy_data['scope'] = 'local'
        
        yaml_data = convert_json_to_yaml(policy_data)
        
        # Renommer le fichier en sortie
        new_filename = filename.replace('inventory_policy', 'inventory')
        
        # Sauvegarder le contenu YAML dans un nouveau fichier avec une extension .yaml dans le répertoire de sortie
        yaml_filename = os.path.join(output_dir, new_filename.replace('.json', '.yaml'))
        with open(yaml_filename, 'w', encoding='UTF8') as f:
            f.write("# Fichier YAML généré à partir de JSON\n")
            f.write("# Structure of the file\n")
            f.write("# ---\n")
            f.write("# Category is a nom to group resource in the final inventory. Ex: 'Compute' for 'ec2', 'Storage' for 'efs', 'fsx', 'glacier', etc.\n")
            f.write("# boto_resource_name is the name of the boto3 resource to use to interact with the service. Generally, it is the name of the service in the AWS SDK, but sometime it may differ.\n")
            f.write("# region_type is the type of region where the service is available. It can be 'local' or 'global'.\n")
            f.write("#\n")
            f.write("# inventory_nodes is a list of functions to call to get the inventory of the service. Most of the time, you will have only one function to call, but you can have more if needed.\n")
            f.write("# Each function is a dictionary with the following keys:\n")
            f.write("# - item_key: the key in the response where the list of items is stored.\n")
            f.write("# - item_search_id: the key in the item to use as an identifier for the detailed inventory functions.\n")
            f.write("# - permissions: the list of permissions needed to call the function.\n")
            f.write("# - detail_param: the parameter to use to call the detailed inventory functions.\n")
            f.write("# - result_key: the key in the response where the detailed inventory is stored.\n")
            f.write(yaml_data)

print("Conversion terminée.")