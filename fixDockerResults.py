import re

# Legge il contenuto del file
with open('provaDocker.txt', 'r', encoding='utf-16') as file:
    content = file.read()

# Divide il contenuto in blocchi basati sul pattern "Found unverified result"
blocks = re.split(r'(Found unverified result .*?Tag: latest)', content, flags=re.S)

# Mantiene i blocchi che contengono "/app/Secrets" nella sezione "File:"
filtered_blocks = [blocks[i] + blocks[i+1] for i in range(0, len(blocks)-1, 2) if '/app/Secrets' in blocks[i+1]]

# Scrive il risultato in un nuovo file
with open('filtered_provaDocker.txt', 'w') as file:
    file.write('\n\n'.join(filtered_blocks))

print("Filtro completato. Il file 'filtered_provaDocker.txt' è stato generato.")


# Legge il contenuto del file
with open('provaGitHub.txt', 'r', encoding='utf-16') as file:
    content = file.read()

# Divide il contenuto in blocchi basati sul pattern "Found unverified result"
blocks = re.split(r'(Found unverified result .*?Tag: latest)', content, flags=re.S)

# Mantiene i blocchi che contengono "/app/Secrets" nella sezione "File:"
filtered_blocks = [blocks[i] + blocks[i+1] for i in range(0, len(blocks)-1, 2) if '/app/Secrets' in blocks[i+1]]

# Scrive il risultato in un nuovo file
with open('filtered_provaDocker.txt', 'w') as file:
    file.write('\n\n'.join(filtered_blocks))

print("Filtro completato. Il file 'filtered_provaDocker.txt' è stato generato.")