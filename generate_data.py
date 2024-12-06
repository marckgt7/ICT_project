import os
import random
import pandas as pd
import re
import string
import exrex  # Libreria per generare stringhe da regex

# Directory dove salvare i dati generati
output_dir = "generated_valid_secrets"
os.makedirs(output_dir, exist_ok=True)

# Funzione per sanitizzare i nomi dei file
def sanitize_filename(name):
    return re.sub(r'[\/:*?"<>|]', '_', name)

# Funzione aggiornata per estrarre il charset dalla regex
def extract_charset_from_regex(regex):
    """
    Estrae il charset dalla regex basandosi sulla parte definita tra \b...\b.
    Espande i range come `0-9` o `a-f`.
    """
    charset_match = re.search(r"\\b.*?\[([^\]]+)\].*?\\b", regex)
    if charset_match:
        raw_charset = charset_match.group(1)
        expanded_charset = ""
        i = 0
        while i < len(raw_charset):
            if i + 2 < len(raw_charset) and raw_charset[i + 1] == '-':  # Controlla se c'è un range
                start, end = raw_charset[i], raw_charset[i + 2]
                expanded_charset += ''.join(chr(c) for c in range(ord(start), ord(end) + 1))
                i += 3
            else:
                expanded_charset += raw_charset[i]
                i += 1
        return expanded_charset
    else:
        return string.ascii_letters + string.digits

# Funzione per generare un segreto valido basato sulla regex
def generate_valid_secret_from_regex(regex):
    try:
        # Utilizza exrex per generare una stringa valida
        secret = next(exrex.generate(regex))

        # Estrazione del prefisso esplicito
        prefix = ""
        use_space = False

        # Primo caso: prefisso definito tramite un gruppo `(?:...)`
        prefix_match = re.search(r"\(\?:([a-zA-Z0-9|_]+)\)", regex)
        if prefix_match:
            potential_prefixes = prefix_match.group(1).split('|')
            prefix = next((p + "_" if secret.startswith(p + "_") else p for p in potential_prefixes if secret.startswith(p)), "")
            if not prefix.endswith("_"):
                use_space = True

        # Controlla se la regex contiene il pattern (?:.|[\n\r]) per aggiungere lo spazio
        if re.search(r"(?:\.|\[\n\r\])", regex):
            use_space = True
        else :
            use_space = False

        # Estrai il charset dalla regex
        charset = extract_charset_from_regex(regex)

        # Genera la parte variabile randomica
        random_variable_part = ''.join(random.choices(charset, k=len(secret) - len(prefix)))
        
        # Combina prefisso e parte randomica con o senza spazio
        return f"{prefix} {random_variable_part}" if use_space else f"{prefix}{random_variable_part}"
    except Exception as e:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=40))

# Percorso del file caricato
excel_file_path = "Secret Regular Expression.xlsx"

# Lettura del file Excel
regex_df = pd.read_excel(excel_file_path)

# Raggruppa i detector per nome principale
grouped_detectors = {}
for _, row in regex_df.iterrows():
    full_name = row['Secret Type']
    regex = row['Regular Expression']
    
    # Identifica il nome principale (prima parola del nome completo)
    main_name = full_name.split(' ', 1)[0]  # Es. "Appcues API Key" → "Appcues"
    if main_name not in grouped_detectors:
        grouped_detectors[main_name] = []
    grouped_detectors[main_name].append((full_name, regex))

# Creazione dei file di segreti
for main_name, detectors in grouped_detectors.items():
    sanitized_main_name = sanitize_filename(main_name)
    all_secrets = []
    
    for full_name, regex in detectors:
        secrets = [generate_valid_secret_from_regex(regex) for _ in range(10)]
        all_secrets.append(f"### Secrets for {full_name} ###")
        all_secrets.extend(secrets)
        all_secrets.append("")  # Linea vuota per separare i blocchi
    
    # Scrivi tutti i segreti in un unico file
    with open(os.path.join(output_dir, f"{sanitized_main_name}_valid_secrets.txt"), "w") as file:
        file.write("\n".join(all_secrets))

print(f"Dataset generato con successo nella directory '{output_dir}'")
