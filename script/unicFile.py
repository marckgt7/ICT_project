import os

def merge_text_files(folder_path, output_file):
    try:
        # Ottiene tutti i file nella cartella
        txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]

        # Ordina i file (opzionale, se vuoi un ordine specifico)
        txt_files.sort()

        with open(output_file, 'w') as outfile:
            for txt_file in txt_files:
                file_path = os.path.join(folder_path, txt_file)
                with open(file_path, 'r') as infile:
                    lines = infile.readlines()
                    if len(lines) > 2:
                        outfile.write(''.join(lines[2:]))  # Salta le prime due righe
                        outfile.write('\n')  # Aggiunge una nuova linea tra i file

        print(f"I file sono stati uniti con successo in {output_file}.")
    except Exception as e:
        print(f"Errore: {e}")

# Esempio di utilizzo
folder_path = 'data/Secrets10'  # Sostituisci con il percorso della tua cartella
output_file = 'data/Secrets10.txt'  # Nome del file di output
merge_text_files(folder_path, output_file)
