import os
import json
import yaml

# Définir le répertoire d'entrée et de sortie
input_dir = 'resources'
output_dir = 'output_policies'
os.makedirs(output_dir, exist_ok=True)

# Fonction pour extraire les permissions d'un fichier YAML
def extract_permissions(yaml_file):
    with open(yaml_file, 'r') as file:
        data = yaml.safe_load(file)
    
    permissions = set()
    
    def recursive_extract(data, resource):
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
                    
    for resource, details in data.items():
        recursive_extract(details, resource)
    
    return permissions

# Collecter les permissions de tous les fichiers YAML dans le répertoire d'entrée
all_permissions = set()
for file_name in os.listdir(input_dir):
    if file_name.endswith('.yaml'):
        file_path = os.path.join(input_dir, file_name)
        all_permissions.update(extract_permissions(file_path))

# Trier les permissions et les convertir en une liste
sorted_permissions = sorted(all_permissions)

# Fonction pour diviser les permissions en chunks de longueur maximale
def chunk_permissions(permissions, max_length):
    chunks = []
    current_chunk = []
    current_length = 0
    
    for perm in permissions:
        perm_length = len(json.dumps(perm)) + 2  # Ajouter 2 pour les guillemets et la virgule
        if current_length + perm_length > max_length:
            chunks.append(current_chunk)
            current_chunk = []
            current_length = 0
        current_chunk.append(perm)
        current_length += perm_length
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

# Diviser les permissions en chunks
max_chars = 6144
permission_chunks = chunk_permissions(sorted_permissions, max_chars)

# Sauvegarder chaque chunk dans un fichier JSON
for i, chunk in enumerate(permission_chunks):
    output_path = os.path.join(output_dir, f'permissions_{i+1}.json')
    with open(output_path, 'w') as outfile:
        json.dump({"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Action": chunk, "Resource": "*"}]}, outfile, indent=4)

print("Les fichiers de permissions ont été générés dans le répertoire 'output_policies'.")