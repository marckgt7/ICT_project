import re
import os 

file_path = os.path.join('output', 'prova_Secrets1_docker.txt')

# Legge il contenuto del file
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# Divide il contenuto in blocchi basati sul pattern "Found unverified result"
blocks = re.split(r'(Found .*?Tag: latest)', content, flags=re.S)

# Mantiene i blocchi che contengono "/app/Secrets" nella sezione "File:"
filtered_blocks = [blocks[i] + blocks[i+1] for i in range(0, len(blocks)-1, 2) if '/app/Secrets' in blocks[i+1]]

# Scrive il risultato in un nuovo file
with open(file_path, 'w', encoding='utf-8') as file:
    file.write('\n\n'.join(filtered_blocks))

print("Filtro completato. Il file 'filtered_provaDocker.txt' è stato generato.")


file_path = os.path.join('output', 'prova_Secrets1_github.txt')

# Legge il contenuto del file
with open(file_path, 'r',  encoding='utf-8') as file:
    content = file.read()

# Divide il contenuto in blocchi basati sul pattern "Found unverified result"
blocks = re.split(r'(Found .*?Tag: latest)', content, flags=re.S)

# Mantiene i blocchi che contengono "/app/Secrets" nella sezione "File:"
filtered_blocks = [blocks[i] + blocks[i+1] for i in range(0, len(blocks)-1, 2) if '/app/Secrets' in blocks[i+1]]

# Scrive il risultato in un nuovo file
with open(file_path, 'w', encoding='utf-8') as file:
    file.write('\n\n'.join(filtered_blocks))

print("Filtro completato. Il file 'filtered_provaDocker.txt' è stato generato.")