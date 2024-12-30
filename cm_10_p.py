import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

def analyze_detectors(results_file, additional_fn_detectors):
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
    results = defaultdict(lambda: {'TP': 0, 'FP': 0, 'FN': 0})

    # Analyze detectors
    for _, row in df.iterrows():
        detector, secrets = row['Detector'], row['SecretsFound']

        if secrets == 10:
            results[detector]['TP'] += 10  # All 10 are true positives
        elif secrets > 10:
            results[detector]['TP'] += 10  # First 10 are true positives
            results[detector]['FP'] += secrets - 10  # The rest are false positives
        elif secrets < 10:
            results[detector]['TP'] += secrets  # Found secrets are true positives
            results[detector]['FN'] += 10 - secrets  # The rest are false negatives

    # Mark missing detectors as False Negatives
    missing_detectors = [f"Detector_{i+1}" for i in range(missing_detectors_count)]
    for detector in missing_detectors:
        results[detector]['FN'] += 10  # Entirely missed detector is 10 false negatives

    # Add additional FN detectors
    for detector in additional_fn_detectors:
        results[detector]['FN'] += 10  # Entirely missed detector is 10 false negatives

    # Compute overall counts for confusion matrix
    tp = sum(r['TP'] for r in results.values())
    fp = sum(r['FP'] for r in results.values())
    fn = sum(r['FN'] for r in results.values())

    # Calculate metrics
    total_predictions = tp + fp + fn
    accuracy = tp / total_predictions if total_predictions > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    return tp, fp, fn, accuracy, precision, recall

def plot_confusion_matrix(tp, fp, fn, accuracy, precision, recall):
    # Plot matrix
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))

    confusion_matrix = np.array([[tp, fp], [fn, 0]])
    labels = ['TP', 'FP', 'FN']
    counts = [tp, fp, fn]

    ax[0].matshow(confusion_matrix, cmap='coolwarm')
    for (i, j), val in np.ndenumerate(confusion_matrix):
        ax[0].text(j, i, f'{val}', ha='center', va='center', color='white')

    ax[0].set_title('Confusion Matrix')

    ax[1].pie(counts, labels=labels, autopct='%1.1f%%', startangle=140, colors=['green', 'orange', 'red'])
    ax[1].set_title('Confusion Matrix Distribution')

    # Display metrics
    plt.figtext(0.5, 0.01, f"Accuracy: {accuracy:.2f}, Precision: {precision:.2f}, Recall: {recall:.2f}", ha="center", fontsize=10, bbox={"facecolor":"lightgrey", "alpha":0.5, "pad":5})

    plt.tight_layout()
    plt.show()

# Run analysis
results_file = 'results/prova_Secrets10_filesystem.txt'
additional_fn_detectors = []  # Replace with user input if necessary
tp, fp, fn, accuracy, precision, recall = analyze_detectors(results_file, additional_fn_detectors)
plot_confusion_matrix(tp, fp, fn, accuracy, precision, recall)
