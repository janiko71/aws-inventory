"""
This script extracts permissions from YAML files in a specified directory.

Functions:
    extract_permissions(file_path):
        Extracts permissions from a given YAML file.
            file_path (str): The path to the YAML file.
            set: A set of permissions extracted from the file.
    write_permissions_to_files(permissions, output_dir):
        Writes the set of permissions to multiple output files if the size exceeds 6144 characters.
            permissions (set): The set of permissions to write.
            output_dir (str): The directory to save the output files.
Usage:
    1. Set the `input_dir` variable to the path of the directory containing the YAML files.
    2. Set the `output_dir` variable to the path of the directory for output files.
    3. Run the script to collect and print permissions from all YAML files in the specified directory.
    4. The script also prints the total execution time.
Example:
    input_dir = 'path/to/input/dir'
    output_dir = 'path/to/output/dir'
    # Run the script to collect permissions
    python create_policy_files.py
    # Output
    {'resource1:permission1', 'resource2:permission2', ...}
"""
import os
import yaml
import json
import time

def extract_permissions(file_path):
    """
    Extrait les permissions d'un fichier YAML donné.

    Args:
        file_path (str): Le chemin du fichier YAML.

    Returns:
        set: Un ensemble de permissions extraites du fichier.
    """
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    
    permissions = set()

    def recursive_extract(data, resource):
        """
        Extrait récursivement les permissions des données YAML.

        Args:
            data (dict or list): Les données YAML.
            resource (str): Le nom de la ressource actuelle.
        """
        if isinstance(data, dict):
            for key, value in data.items():
                if key == 'permissions':
                    if isinstance(value, str):
                        perms = [perm.strip() for perm in value.split(',')]
                        permissions.update(f"{resource}:{perm}" for perm in perms)
                    elif isinstance(value, list):
                        permissions.update(f"{resource}:{perm}" for perm in value)
                else:
                    recursive_extract(value, resource)
        elif isinstance(data, list):
            for item in data:
                recursive_extract(item, resource)
    
    # Parcourt chaque ressource dans les données YAML
    for resource, details in data.items():
        recursive_extract(details, resource)
    
    return permissions

def write_permissions_to_files(permissions, output_dir):
    """
    Écrit les permissions dans des fichiers de sortie en respectant la limite de 6144 caractères.

    Args:
        permissions (set): Un ensemble de permissions à écrire.
        output_dir (str): Le répertoire pour enregistrer les fichiers de sortie.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Trier les permissions par ordre alphabétique et supprimer les doublons
    sorted_permissions = sorted(permissions)

    file_index = 1
    current_file_content = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [],
                "Resource": "*"
            }
        ]
    }
    current_file_size = len(json.dumps(current_file_content))
    max_size = 6144

    for perm in sorted_permissions:
        action = perm
        action_json = json.dumps(action) + "\n"
        if current_file_size + len(action_json) > max_size:
            with open(os.path.join(output_dir, f"permissions_output_{file_index}.json"), 'w') as file:
                json.dump(current_file_content, file, indent=4)
            file_index += 1
            current_file_content = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [action],
                        "Resource": "*"
                    }
                ]
            }
            current_file_size = len(json.dumps(current_file_content))
        else:
            current_file_content["Statement"][0]["Action"].append(action)
            current_file_size += len(action_json)
    
    if current_file_content["Statement"][0]["Action"]:
        with open(os.path.join(output_dir, f"permissions_output_{file_index}.json"), 'w') as file:
            json.dump(current_file_content, file, indent=4)

# Démarrer le chronomètre
start_time = time.time()

# Collecter les permissions de tous les fichiers YAML dans le répertoire d'entrée
input_dir = 'resources'  # Remplacer par le chemin réel du répertoire d'entrée
output_dir = 'output_policies'  # Remplacer par le chemin réel du répertoire de sortie
all_permissions = set()
for file_name in os.listdir(input_dir):
    if file_name.endswith('.yaml'):
        file_path = os.path.join(input_dir, file_name)
        all_permissions.update(extract_permissions(file_path))

# Écrire les permissions dans des fichiers de sortie
write_permissions_to_files(all_permissions, output_dir)

# Afficher le temps d'exécution total
end_time = time.time()
print(f"Temps d'exécution total: {end_time - start_time:.2f} secondes")