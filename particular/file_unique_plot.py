import os
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np

# Ensure the 'plot' folder exists
plot_folder = './plot'
os.makedirs(plot_folder, exist_ok=True)

def analyze_and_plot(file_name):
    # Read the file
    with open(file_name, 'r',encoding="Utf-8") as file:
        lines = file.readlines()

    # Extract Detector Types
    detector_types = [line.split(': ')[1].strip() for line in lines if line.startswith('Detector Type')]
    detector_counts = Counter(detector_types)
    expected_secrets = 6650 if "10" in file_name else 665
    print(detector_types)
    # Count unique detectors
    unique_detectors = len(detector_counts)
    print(unique_detectors)
    # Initialize metrics
    if file_name.endswith('_p.txt'):
        tp = unique_detectors
        fn = expected_secrets - unique_detectors
        fp = sum(count - 1 for count in detector_counts.values())
        tn = 0
    elif file_name.endswith('_n.txt'):
        fp = sum(detector_counts.values())
        tn = expected_secrets - unique_detectors
        tp = 0
        fn = 0
    else:
        raise ValueError("File name must end with '_p.txt' or '_n.txt'")

    # Calculate metrics
    accuracy = (tp + tn) / 665 if 665 > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    fscore = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    # Plot the confusion matrix
    plot_confusion_matrix(tp, fp, fn, tn, accuracy, precision, recall, fscore, file_name)

def plot_confusion_matrix(tp, fp, fn, tn, accuracy, precision, recall, fscore, file_name):
    # Plot matrix
    fig, ax = plt.subplots(1, 2, figsize=(5, 3))

    # Confusion matrix setup
    confusion_matrix = [[tp, fp], [fn, tn]]
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
    
    # Pie chart
    colors_pie = [
            cmap(0.3),  # Greenish (near the start of the colormap)
            cmap(0.1),   # Blueish (midway through the colormap)
            cmap(0.2)   # Orange-ish (towards the end of the colormap)
    ]
    counts = [tp, fp, fn, tn]
    filtered_counts = [value for value in counts if value > 0]
    counts = filtered_counts
    labels_pie = ['True Positives', 'False Positives', 'False Negatives', 'True Negatives']
    filtered_counts_with_labels = [(label, value) for label, value in zip(labels_pie, counts) if value > 0]
# Separare labels e counts filtrati
    filtered_labels, filtered_counts = zip(*filtered_counts_with_labels) if filtered_counts_with_labels else ([], [])
    labels_pie = filtered_labels


    _, texts, autotexts = ax[1].pie(counts, labels=labels_pie, autopct='%1.1f%%', 
                                         startangle=200, colors=colors_pie, 
                                         wedgeprops={'linewidth': 0.3, 'edgecolor': 'white'},
                                         pctdistance=0.6,
                                         textprops={'color': 'black'})

    # Customize pie chart text appearance
    for text in texts + autotexts:
        text.set_fontsize(6)
    
    ax[1].set_title('Confusion Matrix Distribution', fontsize=8)

    # Save the plot
    output_path = os.path.join(plot_folder, os.path.basename(file_name).replace('.txt', '.png'))
    # Display metrics in a cleaner format
    plt.figtext(0.5, 0.005, f"Accuracy: {accuracy:.3f} | Precision: {precision:.3f} | Recall: {recall:.3f} | F1-score: {fscore:.3f}",
                ha="center", fontsize=7, bbox={"facecolor":"#ECEFF1", "alpha":0.7, "pad":4})
    plt.tight_layout(pad=0.9)
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved plot to {output_path}")

# Analyze specific files
analyze_and_plot(r'TruffleOutput\prova_Secrets10_filesystem_unico_p.txt')
analyze_and_plot(r'TruffleOutput\prova_Secrets1_filesystem_unico_p.txt')


