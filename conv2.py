import os
import yaml

def update_yaml_structure(file_path):
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)

    for resource, resource_data in data.items():
        if 'inventory_nodes' in resource_data:
            new_inventory_nodes = {}
            for node_name, node_data in resource_data['inventory_nodes'].items():
                if 'function' in node_data:
                    function_name = node_data.pop('function')
                    node_data['item_key'] = node_name
                    new_inventory_nodes[function_name] = node_data
                else:
                    new_inventory_nodes[node_name] = node_data
            resource_data['inventory_nodes'] = new_inventory_nodes

    with open(file_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

# Répertoire contenant les fichiers YAML à modifier
paused_resources_dir = 'paused_resources'

# Parcourir tous les fichiers YAML dans le répertoire
for filename in os.listdir(paused_resources_dir):
    if filename.endswith('.yaml'):
        file_path = os.path.join(paused_resources_dir, filename)
        update_yaml_structure(file_path)

print("Mise à jour terminée.")