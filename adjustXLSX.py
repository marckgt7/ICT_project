import pandas as pd
import re
import os
from openpyxl import load_workbook

# Funzione per sanitizzare i nomi dei file
def sanitize_filename(name):
    return re.sub(r'[\\/:*?"<>|]', '_', name)

# Funzione per trovare la variabile dopo "keyPat" e il suo contenuto
def find_variable_after_keypat(file_content):    
    keypat_match = re.search(r'keyPat\s*=.*?\n(\s*(\w+)\s*=\s*(.*?))\n', file_content, re.DOTALL)
    if keypat_match:
        variable_name = keypat_match.group(2).strip()
        variable_content = keypat_match.group(3).strip()

        if "regexp.MustCompile" in variable_content:
            return variable_name, variable_content

    return None, None

# Percorso del file Excel
excel_file_path = "Secret Regular Expression.xlsx"
regex_df = pd.read_excel(excel_file_path, engine="openpyxl")

# Percorso dei detector
detectors_path = 'trufflehog-3.84.1/pkg/detectors/'

# Modifica dei file detector e aggiorna il DataFrame
new_rows = []

for root, dirs, files in os.walk(detectors_path):
    for file in files:
        # Ottieni il nome della cartella corrente
        folder_name = os.path.basename(root)

        # Controlla se il file ha estensione .go e il nome della cartella
        if file.endswith(".go") and file.startswith(folder_name.lower()) and folder_name.startswith(file[:-3]):
            file_path = os.path.join(root, file)

            #print(file)
            with open(file_path, 'r') as f:
                file_content = f.read()

            # Trova la variabile dopo "keyPat"
            variable_name, variable_content = find_variable_after_keypat(file_content)
            if not variable_name:
                continue

            # Rimuove le ultime tre lettere "PAT" da variable_name
            variable_name = variable_name[:-3] if variable_name.endswith("PAT") else variable_name

            #print(variable_name, variable_content)

            # Trova l'ultimo indice della categoria nel DataFrame
            # Trova l'ultimo indice della categoria nel DataFrame
            detector_prefix = folder_name.capitalize()  # Prefix per il detector
            matching_indices = regex_df[regex_df['Secret Type'].str.startswith(detector_prefix)].index

            if len(matching_indices) == 0:
                
                words_to_remove = ["io", "api", "apikey", "key", "workflow", 
                                   "devopspersonalaccesstoken", "functionkey", "searchadminkey", 
                                   "searchquerykey", "projectkey", "consumerkey", "personaltoken", "anyplace",
                                   "serviceaccount", "channelkey"]
                cleaned_name = re.sub(rf"({'|'.join(words_to_remove)})$", "", folder_name, flags=re.IGNORECASE)
                 # Genera il prefisso del detector

                detector_prefix = cleaned_name.capitalize()  # Capitalizza il nome pulito
                if(cleaned_name == "myfreshworks"):
                    matching_indices = regex_df[
                        regex_df['Secret Type'].str.lower().str.startswith("freshworks")
                    ].index
                else:
                    matching_indices = regex_df[
                        regex_df['Secret Type'].str.lower().str.startswith(detector_prefix.lower())
                    ].index
                    
                if len(matching_indices) == 0:
                    print(f"Nessuna corrispondenza trovata per {detector_prefix}. Salto il file {file}.")
                    continue
                #print(f"Nessuna corrispondenza trovata per {detector_prefix}. Salto il file {file}.")
                #continue
            
            last_index = matching_indices[-1]

            # Crea una nuova riga
            new_row = pd.DataFrame({
                'Secret Type': [folder_name.capitalize() + ' ' + variable_name.upper()],
                'Regular Expression': [variable_content]
            })

            # Dividi il DataFrame in due parti e inserisci la nuova riga
            upper_half = regex_df.iloc[:last_index + 1]
            lower_half = regex_df.iloc[last_index + 1:]
            regex_df = pd.concat([upper_half, new_row, lower_half], ignore_index=True)

# Salva il file Excel modificato con il suffisso "_prova"
modified_excel_file_path = excel_file_path.replace('.xlsx', '_prova.xlsx')
regex_df.to_excel(modified_excel_file_path, index=False, engine="openpyxl")

print(f"File Excel modificato salvato come: {modified_excel_file_path}")
