"""import pandas as pd

# Leggi il file Excel
file_path = "Secret Regular Expression short.xlsx"  # Sostituisci con il percorso del tuo file
df = pd.read_excel(file_path)

# Verifica che la colonna 'Secret Type' esista
if 'Secret Type' not in df.columns:
    raise ValueError("La colonna 'Secret Type' non è presente nel file Excel.")

# Funzione per rimuovere "API" non come prima parola
def clean_secret_type(value):
    words = str(value).split()  # Divide la stringa in parole
    if len(words) > 0 and words[0].lower() == "key":  # Mantiene "API" se è la prima parola
        return value
    # Rimuove tutte le occorrenze di "API" non come prima parola
    cleaned_words = [word for word in words if word.lower() != "key"]
    return " ".join(cleaned_words)  # Ricostruisce la stringa senza "API"

# Applica la funzione per modificare la colonna
df['Secret Type'] = df['Secret Type'].apply(clean_secret_type)

# Salva il risultato in un nuovo file Excel
output_path = "Secret Regular Expression short.xlsx"  # Sostituisci con il percorso desiderato
df.to_excel(output_path, index=False)

print(f"File modificato salvato in: {output_path}")



import pandas as pd
from difflib import SequenceMatcher

# Funzione per calcolare la similarità
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Leggi i due file Excel
file_1 = "output_file.xlsx"  # File contenente la colonna 'Detector'
file_2 = "Secret Regular Expression short.xlsx"  # File contenente la colonna 'Secret Type'

# Carica i file in DataFrame
df1 = pd.read_excel(file_1)  # Assicurati che 'Detector' esista
df2 = pd.read_excel(file_2)  # Assicurati che 'Secret Type' esista

# Verifica che le colonne esistano
if 'Detector' not in df1.columns:
    raise ValueError("La colonna 'Detector' non è presente nel primo file.")
if 'Secret Type' not in df2.columns:
    raise ValueError("La colonna 'Secret Type' non è presente nel secondo file.")

# Estrarre le colonne di interesse
detector_list = df1['Detector'].dropna().astype(str).tolist()
secret_type_list = df2['Secret Type'].dropna().astype(str).tolist()

# Trova le somiglianze e conta
similar_count = 0
for detector in detector_list:
    for secret in secret_type_list:
        if similar(detector, secret) >= 0.85:  # Similarità >= 80%
            similar_count += 1

# Risultato
print(f"Numero di elementi simili trovati: {similar_count}")
"""

import pandas as pd

# Leggi il file Excel
file_path = "regex.xlsx"
df = pd.read_excel(file_path)

# Rimuovi i duplicati
# Il metodo `drop_duplicates()` rimuove le righe duplicate
# L'opzione `keep='first'` conserva la prima occorrenza
cleaned_df = df.drop_duplicates()

# Salva il file senza duplicati
output_file_path = "regex_no_duplicates.xlsx"
cleaned_df.to_excel(output_file_path, index=False)

print(f"File salvato senza duplicati in: {output_file_path}")
