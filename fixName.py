import os

# Percorsi delle cartelle
folders = ['Secrets1', 'Secrets10']

# Itera sulle cartelle
for folder in folders:
    # Controlla se la cartella esiste
    if os.path.exists(folder):
        # Itera sui file nella cartella
        for file_name in os.listdir(folder):
            # Verifica se il file contiene _valid_ e ha estensione .txt
            if '_valid_' in file_name and file_name.endswith('.txt'):
                # Crea il nuovo nome del file
                new_name = file_name.replace('_valid_', '_')
                # Percorsi completi
                old_path = os.path.join(folder, file_name)
                new_path = os.path.join(folder, new_name)
                # Rinomina il file
                os.rename(old_path, new_path)
                print(f"Rinominato: {file_name} -> {new_name}")
    else:
        print(f"Cartella {folder} non trovata.")
