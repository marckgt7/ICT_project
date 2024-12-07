import os
import random
import pandas as pd
import re
import string
import exrex  # Libreria per generare stringhe da regex

# Directory dove salvare i dati generati
output_dir = "generated_valid_secrets"
os.makedirs(output_dir, exist_ok=True)

def sanitize_filename(name):
    return re.sub(r'[\/:*?"<>|]', '_', name)

def extract_length_from_regex(regex):
    """
    Estrae la lunghezza totale del segreto, supportando regex complesse.
    """
    length_matches = re.findall(r"(?:\[.*?\]|[a-zA-Z0-9\\\/\+=\-_\(\):])\{(\d+),?(\d+)?\}", regex)
    if length_matches:
        min_length_total = 0
        max_length_total = 0
        for min_len, max_len in length_matches:
            min_len = int(min_len)
            max_len = int(max_len) if max_len else min_len
            min_length_total += min_len
            max_length_total += max_len
        if min_length_total == max_length_total:
            return min_length_total  # Lunghezza fissa
        return (min_length_total, max_length_total)  # Lunghezza minima e massima
    return None

def extract_charset_from_regex(regex):
    charset_match = re.search(r"\\b.*?\[([^\]]+)\].*?\\b", regex)
    if charset_match:
        raw_charset = charset_match.group(1)
        expanded_charset = ""
        i = 0
        while i < len(raw_charset):
            if i + 2 < len(raw_charset) and raw_charset[i + 1] == '-':
                start, end = raw_charset[i], raw_charset[i + 2]
                expanded_charset += ''.join(chr(c) for c in range(ord(start), ord(end) + 1))
                i += 3
            else:
                expanded_charset += raw_charset[i]
                i += 1
        return expanded_charset
    else:
        return string.ascii_letters + string.digits

def handle_complex_regex(regex):
    """
    Trasforma regex complesse con flag globali o multilinea in una forma compatibile.
    """
    # Rimuove i flag globali o multilinea che non sono supportati direttamente da `exrex`
    sanitized_regex = re.sub(r"(?<=/)[gmi]+", "", regex)  # Rimuove flag come 'g', 'm', 'i'
    if sanitized_regex.startswith("/"):
        sanitized_regex = sanitized_regex.strip("/")
    return sanitized_regex

def generate_valid_secret_from_regex(regex):
    try:
        regex = handle_complex_regex(regex)  # Gestisce regex complesse
        length_info = extract_length_from_regex(regex)
        
        if isinstance(length_info, tuple):
            min_length, max_length = length_info
            secret_length = random.randint(min_length, max_length)
        elif isinstance(length_info, int):
            secret_length = length_info
        else:
            secret_length = 40  # Valore di default

        secret = next(exrex.generate(regex))

        prefix = ""
        use_space = False

        prefix_match = re.search(r"\(\?:([a-zA-Z0-9|_]+)\)", regex)
        if prefix_match:
            potential_prefixes = prefix_match.group(1).split('|')
            prefix = next((p + "_" if secret.startswith(p + "_") else p for p in potential_prefixes if secret.startswith(p)), "")

        if re.search(r"(?:\.|\[\n\r\])", regex):
            use_space = True

        charset = extract_charset_from_regex(regex)

        if secret_length:
            random_variable_part = ''.join(random.choices(charset, k=secret_length))
        else:
            random_variable_part = ''.join(random.choices(charset, k=len(secret) - len(prefix)))

        return f"{prefix} {random_variable_part}" if use_space else f"{prefix}{random_variable_part}"
    except Exception as e:
        print(f"Errore con la regex {regex}: {e}")
        return ''.join(random.choices(string.ascii_letters + string.digits, k=40))

excel_file_path = "Secret Regular Expression.xlsx"
regex_df = pd.read_excel(excel_file_path)

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
        generated_secrets[secret_type] = [generate_valid_secret_from_regex(regex) for _ in range(10)]

    all_secrets.append(" | ".join(secret_types))
    all_secrets.append("-" * len(" | ".join(secret_types)))

    for i in range(10):
        row = [generated_secrets[secret_type][i] for secret_type in secret_types]
        all_secrets.append(" | ".join(row))

    with open(os.path.join(output_dir, f"{sanitized_main_name}_valid_secrets.txt"), "w") as file:
        file.write("\n".join(all_secrets))

print(f"Dataset generato con successo nella directory '{output_dir}'")
