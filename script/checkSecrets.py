import re
import pandas as pd
from tabulate import tabulate
import os

# Funzione per cancellare i file in una cartella
def delete_files_in_folder(folder_path):
    # Verifica se la cartella esiste
    if os.path.exists(folder_path):
        # Cicla attraverso i file nella cartella
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            # Controlla se è un file e lo cancella
            if os.path.isfile(file_path):
                os.remove(file_path)
    else:
        print(f"La cartella {folder_path} non esiste.")

# Funzione per contare i detector unici e quanti segreti hanno rilevato
def count_unique_detectors_and_secrets(file_path):
    global conta
    try:
        # Prova ad aprire il file con codifica UTF-16
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Divide il contenuto in blocchi basati sul pattern "Found unverified result"
        blocks = re.split(r'(Found .*?\n\n)', content, flags=re.S)
        blocks = [block for block in blocks if block and "Found" in block]
        secrets = []
        for block in blocks:
            detector_match = re.search(r'Detector Type: (\w+)', block)
            raw_result_match = re.search(r'Raw result: ([^\n]+)', block)
            file_match = re.search(r'File: .*[/\\](\w+)_secrets\.txt', block)

            if detector_match and raw_result_match and file_match:
                detector_type = detector_match.group(1)
                raw_result = raw_result_match.group(1)
                file_name = file_match.group(1)
                
                detector_normalized = detector_type.strip().lower()
                file_name_normalized = file_name.strip().lower()
                secrets.append((detector_normalized, file_name_normalized, raw_result))
            else:
                print(detector_match)
                print(raw_result_match)
                print(file_match)
        df = pd.DataFrame(secrets, columns=['Detector', 'File', 'Secret'])
        df_unique = df.drop_duplicates(subset=['File', 'Secret'])
        return df_unique

    except UnicodeDecodeError:
        print("Errore di codifica del file. Prova a usare un'altra codifica.")
        return 0, {}, pd.DataFrame()

# Percorso del file di input
file_path_array = [ './output/prova_Secrets1_docker.txt',
                    './output/prova_Secrets1_filesystem.txt',
                    './output/prova_Secrets1_git.txt',
                    './output/prova_Secrets1_github.txt',
                    './output/prova_Secrets10_filesystem.txt',
                    './output/prova_Secrets1_filesystem_fake.txt',
                    './output/prova_Secrets10_filesystem_fake.txt'
                    ]
excel_file_path = "./Secret Regular Expression FILTERED.xlsx"  # Percorso del file Excel
results_dir = "./results"
os.makedirs(results_dir, exist_ok=True)
delete_files_in_folder(os.path.join(results_dir))

for file_path in file_path_array:
    # Esegui il conteggio dei detector e dei segreti
    detectors_found = count_unique_detectors_and_secrets(file_path)
    # Questo file contiene tutti i detector rilevati da trufflehog
    output_file = "detectors_found.xlsx"
    detectors_found.to_excel(output_file, index=False)  # index=False evita di salvare l'indice del DataFrame
    # Leggi il file Excel per ottenere l'elenco dei detector attesi
    try:
        regex_df = pd.read_excel(excel_file_path)

        # Rimuovi i duplicati nella colonna 'Secret Type' (prendendo solo la prima parola e rendendola minuscola)
        regex_df['Detector'] = regex_df['Secret Type'].apply(lambda x: x.split()[0].strip().lower())
        regex_df = regex_df.drop(columns=['Secret Type', 'Source', 'Pattern_ID', 'Regular Expression', 'Unnamed: 4'], axis=1)
        expected_detectors = regex_df.drop_duplicates(subset=['Detector'])
    except Exception as e:
        print(f"Errore durante la lettura del file Excel: {e}")
        expected_detectors = []

    # Prepariamo i dati per la tabella
    table_data = []
    detector_mismatch = []  # Lista per i detector che non hanno 10 segreti

    # Raggruppa e conta i detector trovati
    detectors_found_group = detectors_found.groupby('File').size().reset_index(name='Count')
    for index, row in detectors_found_group.iterrows():
        table_data.append([row['File'], row['Count']])

        if("Secrets10" in file_path):
            # Se il numero di segreti non è 10, aggiungi il detector alla lista di mismatch
            if row['Count'] != 10:
                detector_mismatch.append((row['File'], row['Count']))
        else:
            if row['Count'] != 1:
                detector_mismatch.append((row['File'], row['Count']))

    # Prepara l'output
    output = []

    expected_detectors.columns = ['File']
    # Tabella dei detector
    output.append("Tabella dei detector e segreti rilevati:")
    output.append(tabulate(table_data, headers=['File', 'Numero segreti rilevati'], tablefmt='grid'))

    # Totale dei detector
    output.append(f"Detector trovati: {len(detectors_found['Detector'].unique())}")
    output.append(f"Detector Expected: {len(expected_detectors)}")

    # Falsi negativi
    detectors_missing = expected_detectors.merge(detectors_found, on='File', how='left')
    detectors_missing = detectors_missing.drop_duplicates(subset=['File', 'Secret']) # QUELLI CHE HANNO PIU DI UN SEGRETO
    detectors_missing.to_excel("detector_missing.xlsx", index=False)  # index=False evita di salvare l'indice del DataFrame
    output.append(f"Detector mancanti: {detectors_missing['Secret'].isna().sum()}")
    
    # Veri Positivi
    output.append(f"Veri Positivi: {detectors_missing.drop_duplicates(subset=['File'])['Secret'].notna().sum()}")

    # Falsi positivi
    extra_detectors = expected_detectors.merge(detectors_found, on='File', how='right')
    extra_detectors.to_excel("extra_detectors.xlsx", index=False)  # index=False evita di salvare l'indice del DataFrame
    output.append(f"Detector extra: {extra_detectors['Secret'].isna().sum()}")

    # Veri Negativi = = DETECTOR_TRUFFLEHOG - EXPECTED_DETECTOR
    #print(f"Detector NON Trovati: {detectors_missing['Secret'].notna().sum()}")

    # Segnala i detector che non hanno 10 segreti
    falsi_positivi = 0
    if detector_mismatch:
        output.append(f"\nDetector con numero di segreti diverso da 10: {len(detectors_found['Detector'].unique()) + len(detector_mismatch) - len(detectors_found['Detector'].unique())}")

        for detector, count in detector_mismatch:
            output.append(f"- {detector}: {count} segreti")
            falsi_positivi += count
            
    else:
        output.append("\nTutti i detector hanno esattamente 10 segreti.")

    output.append(f"\nFalsi Positivi: {falsi_positivi - len(detector_mismatch)}")
    output.append("\n")
    # Segnala i detector mancanti
    detectors_nan = detectors_missing[detectors_missing['Secret'].isna()]['File'].tolist()
    if detectors_nan:
        output.append("Elenco dei detector missing:")
        for detector in sorted(detectors_nan):
            output.append(f"- {detector}")
    else:
        output.append("Tutti i detector hanno un Secret presente.")

    # Salva l'output su un file
    with open(os.path.join(results_dir, file_path.replace('output/', '')), 'w') as results_file:
        results_file.write("\n".join(output))

    print("L'output è stato salvato nel file", results_file.name)
