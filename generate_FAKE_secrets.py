import pandas as pd
import re
import os
import random
import string
from openpyxl import Workbook, load_workbook


def sanitize_filename(name):
    return re.sub(r'[\\/:*?"<>|]', '_', name)


def generate_random_string(charset, length):
    global perfect, imperfect
    # Espandi il charset se contiene intervalli
    charset_length = random.randint(5, 20)  # Lunghezza del charset casuale
    all_characters = "FACCIO RUMOREèàùrumore" + string.digits + string.punctuation
    charset = ''.join(random.choices(all_characters, k=charset_length))
    
    # Se length è un intervallo, scegli una lunghezza casuale nell'intervallo
    if ',' in length:
        min_len, max_len = length.split(',')
        min_len = int(min_len) if min_len else None
        max_len = int(max_len) if max_len else None
        
        if min_len is not None and max_len is not None:
            actual_length = random.randint(min_len, max_len) + max_len
        elif min_len is not None:
            actual_length = min_len
        elif max_len is not None:
            actual_length = max_len  

    elif length == 'None' or length == '\\':
        # Lunghezza casuale se è 'None'
        actual_length = random.randint(1, 100)  # Puoi cambiare l'intervallo
    else:
        # Lunghezza fissa
        actual_length = int(length) 
    
    #print(actual_length)
    return ''.join(random.choices(charset, k=actual_length ))

# Funzione per analizzare una singola regex e ottenere informazioni dettagliate
def generate_secret(regex):
    global perfect, imperfect

    if regex == "EMAIL A PIACERE":
       return "rompiamo@tutto.IT"

    # Trova il pre fisso
    match = re.search(r"\(\?:([a-zA-Z0-9|_.-]+)\)", regex) 
    if match:
        prefisso = match.group(1).split('|')
    else:
        match = re.search(r"\\b\(?([a-zA-Z0-9_.\\-]+)\\?", regex) or \
                re.search(r"\(\?:([a-zA-Z0-9]+)\)", regex) or \
                re.search(r'https://[^[]+', re.sub(r'\\', '', regex))
        if match:
            if match.lastindex is not None and match.lastindex >= 1: 
                prefisso = match.group(1) 
                prefisso = prefisso.replace("\\", "")
            else: 
                prefisso = match.group(0)  # HTTP 
        else:
            prefisso = ""
    

    # Matching per suffissi tipo ".aha.io", ".jfrog.io" non chiusi tra [] o {}
    suffix_match = re.findall(r'(\.[a-zA-Z0-9]+|@[a-zA-Z0-9]+|tt\b|[ \r\n]{1}|-X)', regex)

    # Pattern per trovare i separatori (es. \. o \-)
    separator_pattern = r'\\(-4|[.=_|@\-])'  # Cattura -4 come entità e tutti gli altri separatori

    # Estrarre i separatori
    all_separators = []
    matches = re.findall(separator_pattern, regex)
    all_separators.extend(matches)

    # Se suffix_match ha qualcosa, rimuove gli ultimi n elementi da all_separators
    if suffix_match:
        n = len(suffix_match)
        all_separators = all_separators[:-n] if n <= len(all_separators) else []


    # Trova tutte le coppie tra parentesi quadre e graffe
    matches = re.findall(r"\[([^\]]+)\]|\{([^\}]+)\}", regex)

    if matches:
        # Usa una lista per associare la lunghezza successiva a quelli vuoti
        coppie = [
            (x, y if y else (matches[i + 1][1] if i + 1 < len(matches) else 'None'))
            for i, (x, y) in enumerate(matches)
            if x or (y or (i + 1 < len(matches) and matches[i + 1][1]))  # Rimuovi le coppie dove il primo valore è vuoto
        ]

        # Rimuovi le coppie con il primo valore vuoto ('') o con il secondo valore vuoto o solo spazi
        coppie = [pair for pair in coppie if pair[0] != '' and pair[1].strip() != '']

    else:
        return None

    #charsets contiene tutti i possibili charset e le lunghezze di questi (opzionale)
    # Verifica se prefisso è una lista
    if isinstance(prefisso, list):  
        secret = ''.join(random.choice(prefisso))  # Sceglie un elemento casuale dalla lista
    else:
        secret = prefisso  # Usa direttamente prefisso se è una stringa

    charsets = []
    # Stampa le coppie risultanti
    if(not coppie):
        return None
    else:
        for coppia in coppie:
            charsets.append(coppia)
        for i, charset in enumerate(charsets):
            random_variable_part = generate_random_string(charset[0], charset[1])

            if(all_separators and len(all_separators)  == len(charsets) ):
                secret +=  all_separators[0]  # Usa l'elemento in testa
                all_separators.pop(0)  # Rimuovi l'elemento appena usato
            secret += random_variable_part
            if i < len(charsets) - 1:
                if all_separators:
                    secret +=  all_separators[0]  # Usa l'elemento in testa
                    all_separators.pop(0)  # Rimuovi l'elemento appena usato
                else:
                    secret += '-'
        
        if(suffix_match):
            for suffix in suffix_match:
                secret += suffix
        
        return secret

   
excel_file_path = "Secret Regular Expression FILTERED.xlsx"
regex_df = pd.read_excel(excel_file_path, engine="openpyxl")

# Directory dove salvare i dati generati
output_dir = "FakeSecrets10"
os.makedirs(output_dir, exist_ok=True)

grouped_detectors = {}
for _, row in regex_df.iterrows():
    full_name = row['Secret Type']
    regex = row['Regular Expression']
    
    main_name = full_name.split(' ', 1)[0]
    if main_name not in grouped_detectors:
        grouped_detectors[main_name] = []
    grouped_detectors[main_name].append((full_name, regex))

for main_name, detectors in grouped_detectors.items():
    sanitized_main_name = sanitize_filename(main_name)
    all_secrets = []

    secret_types = [detector[0].split()[-1] for detector in detectors]
    generated_secrets = {secret_type: [] for secret_type in secret_types}

    for full_name, regex in detectors:
        secret_type = full_name.split()[-1]
        try:
            # Tentativo di generare 10 segreti per ogni tipo
            generated_secrets[secret_type] = [generate_secret(regex) for _ in range(10)]
        except Exception as e:
            # Se si verifica un errore, stampa un messaggio di errore e passa al prossimo detector
            print(f"Errore durante la generazione dei segreti per {full_name}: {e}")
            continue
    
    # Aggiungi i secret types e una riga di separazione
    all_secrets.append(" | ".join(secret_types))
    all_secrets.append("-" * len(" | ".join(secret_types)))

    # Aggiungi i segreti generati, evitando i valori None
    for i in range(10):
        row = [generated_secrets[secret_type][i] for secret_type in secret_types]
        # Rimuovi i valori None dalla riga
        row = [secret for secret in row if secret is not None]
        
        # Aggiungi la riga solo se non è vuota
        if row:
            all_secrets.append(" FACCIO RUMORE ".join(row))

    # Scrivi i segreti nel file
    with open(os.path.join(output_dir, f"{sanitized_main_name}_secrets.txt"), "w") as file:
        file.write("\n".join(all_secrets))

print(f"Dataset generato con successo nella directory '{output_dir}'")
