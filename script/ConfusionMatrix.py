import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# Ensure the 'plot' folder exists
plot_folder = './plot'
os.makedirs(plot_folder, exist_ok=True)

# Function to analyze detectors based on the extracted numero
def analyze_detectors(results_file, numero, additional_fn_detectors):
    # Read the results file and preprocess
    data = []
    missing_detectors_count = 0
    with open(results_file, 'r') as file:
        lines = file.readlines()
        missing_section = False
        for line in lines:
            if "Elenco dei detector missing:" in line:
                missing_section = True
                continue
            if missing_section:
                missing_detectors_count += 1
            if "|" in line and not line.strip().startswith("+"):
                parts = line.split("|")
                detector = parts[1].strip()
                try:
                    secrets_found = int(parts[2].strip())
                    data.append((detector, secrets_found))
                except ValueError:
                    continue

    # Convert to DataFrame
    df = pd.DataFrame(data, columns=['Detector', 'SecretsFound'])

    # Initialize results
    results = defaultdict(lambda: {'TP': 0, 'FP': 0, 'FN': 0,'TN':0})

    # Analyze detectors based on 'numero' (different logic for fake files)
    if 'fake' in results_file:
        for _, row in df.iterrows():
            detector, secrets = row['Detector'], row['SecretsFound']

            if secrets == numero:
                results[detector]['FP'] += numero  # All secrets are true negatives
            elif secrets > numero:
                results[detector]['FP'] += secrets  # All are false positives
            elif secrets < numero:
                results[detector]['FP'] += secrets  # Found secrets are false positives
                results[detector]['FN'] += numero - secrets  # The rest are false negatives
                        # Mark missing detectors as False Negatives
        missing_detectors = [f"Detector_{i+1}" for i in range(missing_detectors_count)]
        for detector in missing_detectors:
            results[detector]['TN'] += numero  # Entirely missed detector is 10 false negatives
    else:
        # Regular logic for non-fake files
        for _, row in df.iterrows():
            detector, secrets = row['Detector'], row['SecretsFound']

            if secrets == numero:
                results[detector]['TP'] += numero  # All secrets are true positives
            elif secrets > numero:
                results[detector]['TP'] += numero  # First 'numero' are true positives
                results[detector]['FP'] += secrets - numero  # Rest are false positives
            elif secrets < numero:
                results[detector]['TP'] += secrets  # Found secrets are true positives
                results[detector]['FN'] += numero - secrets  # Rest are false negatives

        # Mark missing detectors as False Negatives
        missing_detectors = [f"Detector_{i+1}" for i in range(missing_detectors_count)]
        for detector in missing_detectors:
            results[detector]['FN'] += numero  # Entirely missed detector is 10 false negatives

    # Add additional FN detectors
    for detector in additional_fn_detectors:
        results[detector]['FN'] += numero  # Entirely missed detector is 10 false negatives

    # Compute overall counts for confusion matrix
    tp = sum(r['TP'] for r in results.values())
    fp = sum(r['FP'] for r in results.values())
    fn = sum(r['FN'] for r in results.values())
    tn = sum(r['TN'] for r in results.values())


    # Calculate metrics
    total_predictions = tp + fp + fn + tn
    accuracy = (tp+tn) / total_predictions if total_predictions > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    fscore = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return tp, fp, fn,tn, accuracy, precision, recall, fscore

def save_confusion_matrix(tp, fp, fn,tn, accuracy, precision, recall, fscore, output_path):
    # Plot matrix
    fig, ax = plt.subplots(1, 2, figsize=(5, 3))

    # Confusion matrix setup
    confusion_matrix = np.array([[tp, fp], [fn, tn]])
    labels = [['TP', 'FP'], ['FN', 'TN']]

    # Custom colormap for smoother pastel look
    cmap = plt.get_cmap('ocean_r')

    # Confusion matrix heatmap with lighter borders
    ax[0].imshow(confusion_matrix, cmap=cmap, alpha=0.9)
    for (i, j), value in np.ndenumerate(confusion_matrix):
        ax[0].text(j, i, f"{labels[i][j]}\n{value}", ha='center', va='center', 
                   color='black', fontsize=6)

    ax[0].set_xticks(range(2))
    ax[0].set_xticklabels(['Positive', 'Negative'], fontsize=6)
    ax[0].set_yticks(range(2))
    ax[0].set_yticklabels(['Detected', 'Missed'], fontsize=6)
    ax[0].set_title('Confusion Matrix', fontsize=8)
    ax[0].grid(False)
    ax[0].tick_params(axis='both', length=0)

    # Adjusting the border (spines) thickness
    for spine in ax[0].spines.values():
        spine.set_linewidth(0.3)  # Set a thinner border (you can adjust the value)

    # Metrics pie chart
    counts = [tp, fp, fn,tn]
    labels_pie = ['True Positives', 'False Positives', 'False Negatives','True Negatives']
    colors_pie = [
            cmap(0.3),  # Greenish (near the start of the colormap)
            cmap(0.1),   # Blueish (midway through the colormap)
            cmap(0.2)   # Orange-ish (towards the end of the colormap)
    ]
    wedges, texts, autotexts = ax[1].pie(counts, labels=labels_pie, autopct='%1.1f%%', 
                                         startangle=200, colors=colors_pie, 
                                         wedgeprops={'linewidth': 0.3, 'edgecolor': 'white'},
                                         pctdistance=0.6,
                                         textprops={'color': 'black'})

    # Customize pie chart text appearance
    for text in texts + autotexts:
        text.set_fontsize(6)

    ax[1].set_title('Confusion Matrix Distribution', fontsize=8)

    # Display metrics in a cleaner format
    plt.figtext(0.5, 0.005, f"Accuracy: {accuracy:.2f} | Precision: {precision:.2f} | Recall: {recall:.2f} | F1-score: {fscore:.2f}",
                ha="center", fontsize=7, bbox={"facecolor":"#ECEFF1", "alpha":0.7, "pad":4})

    plt.tight_layout(pad=0.9)
    plt.savefig(output_path, dpi=150)
    plt.close()



# Process all files in the results folder
results_folder = './checkSecretsResults'
additional_fn_detectors = []  # Replace with user input if necessary

# Loop through files in the 'results' folder
for file_name in os.listdir(results_folder):
    if file_name.endswith('.txt'):
        # Extract the numero from the filename (e.g., 'Secrets10')
        if 'Secrets' in file_name:
            numero_str = file_name.split('Secrets')[1].split('_')[0]
            numero = int(numero_str)

            # File path
            file_path = os.path.join(results_folder, file_name)

            # Analyze detectors for the current file
            tp, fp, fn,tn, accuracy, precision, recall, fscore = analyze_detectors(file_path, numero, additional_fn_detectors)

            # Generate plot path
            output_file_name = file_name.replace('prova', 'plot').replace('.txt', '.png')
            output_path = os.path.join(plot_folder, output_file_name)

            # Save the confusion matrix for the current file
            print(f"Saving plot for {file_name} to {output_path}")
            save_confusion_matrix(tp, fp, fn,tn, accuracy, precision, recall, fscore, output_path)
