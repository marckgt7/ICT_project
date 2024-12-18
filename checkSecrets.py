import re
import pandas as pd
from tabulate import tabulate

conta = 0

# Funzione per contare i detector unici e quanti segreti hanno rilevato
def count_unique_detectors_and_secrets(file_path):
    global conta
    try:
        # Prova ad aprire il file con codifica UTF-16
        with open(file_path, 'r', encoding='utf-16') as file:
            content = file.read()

        # Usa una regex per trovare tutte le occorrenze del tipo di detector e raw result
        detector_pattern = r"Detector Type:\s*(\w+)"
        raw_result_pattern = r"Raw result:\s*([\w\W]+?)\n"
        file_result_pattern = r"File:\s*generated_valid_secrets\\(\w+)_valid_secrets\.txt"


        # Trova tutti i detector e i relativi segreti
        detectors = re.findall(detector_pattern, content)
        raw_results = re.findall(raw_result_pattern, content)

        file_result = re.findall(file_result_pattern,content)

        # Crea una lista di tuple con detector e segreti
        detector_secrets = []

        for i, result in enumerate(raw_results):
            detector = detectors[i]

            # Uniforma il formato del nome del detector (es. minuscole)
            detector_normalized = detector.strip().lower()

            # Aggiungi una tupla (detector, segreto) alla lista
            detector_secrets.append((detector_normalized, result, file_result[i]))


            conta += 1

        # Crea un DataFrame dai dati raccolti
        df = pd.DataFrame(detector_secrets, columns=['Detector', 'Secret','file'])

        # Rimuovi i duplicati
        df_unique = df.drop_duplicates(subset=['Detector', 'Secret','file'])
        

        # Calcola il numero di segreti per ogni detector
        detector_counts = df_unique.groupby('Detector').size().to_dict()

        return len(df_unique['Detector'].unique()), detector_counts, df_unique

    except UnicodeDecodeError:
        print("Errore di codifica del file. Prova a usare un'altra codifica.")
        return 0, {}, pd.DataFrame()

# Percorso del file di input
file_path = 'prova.txt'
excel_file_path = "Secret Regular Expression MYNE.xlsx"  # Percorso del file Excel

# Esegui il conteggio dei detector e dei segreti
unique_detector_count, detector_secrets, df_unique = count_unique_detectors_and_secrets(file_path)
print(f"unique_detector_count: {unique_detector_count}")
print(f"detector_secrets: {len(detector_secrets)}")
print(f"df_unique : {df_unique.drop_duplicates(subset=['Detector'])}")
output_file = "output_file.xlsx"
df_dc = df_unique.drop_duplicates(subset=['Detector'])

# Salva il DataFrame in Excel
df_dc.to_excel(output_file, index=False)  # index=False evita di salvare l'indice del DataFrame

# Leggi il file Excel per ottenere l'elenco dei detector attesi
try:
    regex_df = pd.read_excel(excel_file_path)

    # Rimuovi i duplicati nella colonna 'Secret Type' (prendendo solo la prima parola e rendendola minuscola)
    regex_df['Detector'] = regex_df['Secret Type'].apply(lambda x: x.split()[0].strip().lower())
    regex_df_unique = regex_df.drop_duplicates(subset=['Detector'])
    print(regex_df)

    expected_detectors = regex_df_unique['Detector'].unique()  # Prendi solo i detector unici
    print(f"expected_detectors: {len(expected_detectors)}")
except Exception as e:
    print(f"Errore durante la lettura del file Excel: {e}")
    expected_detectors = []

# Trova i detector mancanti
detectors_found = set(detector_secrets.keys())  # Detectors trovati nel file prova.txt (formato uniformato)
print(f"Detector found: {len(detectors_found)}")
temp = list(detectors_found)
df = pd.DataFrame(temp, columns=["Detectors"])
df.to_excel("detectors_totali.xlsx", index=False)  # index=False evita di salvare l'indice del DataFrame

try:
    file_det = pd.read_excel("output_file.xlsx")

    # Rimuovi i duplicati nella colonna 'Secret Type' (prendendo solo la prima parola e rendendola minuscola)
    pippo = file_det.drop_duplicates(subset=['file'])
    pippo = pippo.copy()
    pippo['file'] = pippo['file'].apply(lambda x: x.strip().lower())

    pippo = pippo['file']

except Exception as e:
    print(f"Errore durante la lettura del file Excel: {e}")
    expected_detectors = []

#print(f"questo è pippo: {set(pippo)}")
print(f"totali: {len(set(expected_detectors))}")
print(f"trovati: {len(set(pippo))}")

detectors_missing = set(expected_detectors) - set(pippo)  # Detector presenti in Excel ma non trovati


temp1 = list(detectors_missing)
temp1.sort()
#print(f"detectors_missing: {temp1}")

temp1 = pd.DataFrame(temp1)

temp1.to_excel("detectors_missing.xlsx", index=False)


missing_count = len(detectors_missing)  # Contatore dei detector mancanti
print(f"missing: {missing_count}")
extra_detectors = set(pippo) - set(expected_detectors)
my_list = list(extra_detectors)
my_list.sort()
print(f"Extra detectors not expected: {my_list}")


unione = set(pippo).union(detectors_missing)
numero_elementi = len(unione)
print("Numero di elementi:", numero_elementi)



# Salva la lista dei detector trovati (found) e dei detector mancanti (missing)
with open('found.txt', 'w') as found_file:
    found_file.write(f"Numero di detector trovati: {len(detectors_found)}\n")
    for detector in sorted(detectors_found):
        found_file.write(f"{detector}\n")

with open('missing.txt', 'w') as missing_file:
    missing_file.write(f"Numero di detector mancanti: {missing_count}\n")
    for detector in sorted(detectors_missing):
        missing_file.write(f"{detector}\n")

# Salva il contenuto del DataFrame in un file CSV
# Estrai la colonna 'Detector' e rimuovi i duplicati
df_unique_detectors = df_unique['Detector'].drop_duplicates()

# Salva solo i detector unici in un file CSV
df_unique_detectors.to_csv('detectors_found.csv', index=False, header=True)  # Salva senza l'indice e con l'intestazione

# Prepariamo i dati per la tabella
table_data = []
detector_mismatch = []  # Lista per i detector che non hanno 10 segreti

for detector, count in detector_secrets.items():
    table_data.append([detector, count])

    # Se il numero di segreti non è 10, aggiungi il detector alla lista di mismatch
    if count != 10:
        detector_mismatch.append((detector, count))

# Prepara l'output
output = []

# Tabella dei detector
output.append("Tabella dei detector e segreti rilevati:")
output.append(tabulate(table_data, headers=['Detector', 'Numero segreti rilevati'], tablefmt='grid'))

# Totale dei detector
output.append(f"\nTotale detector trovati: {unique_detector_count}")

# Segnala i detector che non hanno 10 segreti
if detector_mismatch:
    output.append("\nDetector con numero di segreti diverso da 10:")
    for detector, count in detector_mismatch:
        output.append(f"- {detector}: {count} segreti")
else:
    output.append("\nTutti i detector hanno esattamente 10 segreti.")

# Segnala i detector mancanti
output.append(f"\nNumero totale di detector mancanti: {missing_count}")
if detectors_missing:
    output.append("Elenco dei detector mancanti:")
    for detector in sorted(detectors_missing):
        output.append(f"- {detector}")
else:
    output.append("Tutti i detector del file Excel sono presenti nel file prova.")

# Salva l'output su un file
with open('results.txt', 'w') as results_file:
    results_file.write("\n".join(output))

print("L'output è stato salvato nel file 'results.txt'.")
print(conta)
