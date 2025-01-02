import os
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

# Ensure the 'plot' folder exists
plot_folder = './plot'
os.makedirs(plot_folder, exist_ok=True)

def analyze_and_plot(file_name):
    # Read the file
    with open(file_name, 'r',encoding="Utf-16") as file:
        lines = file.readlines()

    # Extract Detector Types
    detector_types = [line.split(': ')[1].strip() for line in lines if line.startswith('Detector Type')]
    detector_counts = Counter(detector_types)

    # Count unique detectors
    unique_detectors = len(detector_counts)
    print(unique_detectors)
    # Initialize metrics
    if file_name.endswith('_p.txt'):
        tp = unique_detectors
        fn = 665 - unique_detectors
        fp = sum(count - 1 for count in detector_counts.values())
        tn = 0
    elif file_name.endswith('_n.txt'):
        fp = sum(detector_counts.values())
        tn = 665 - unique_detectors
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

    # Heatmap
    ax[0].imshow(confusion_matrix, cmap='Blues', alpha=0.9)
    for i in range(2):
        for j in range(2):
            ax[0].text(j, i, f"{labels[i][j]}: {confusion_matrix[i][j]}", ha='center', va='center', color='black')

    ax[0].set_xticks([0, 1])
    ax[0].set_xticklabels(['Positive', 'Negative'])
    ax[0].set_yticks([0, 1])
    ax[0].set_yticklabels(['Detected', 'Missed'])
    ax[0].set_title('Confusion Matrix')

    # Pie chart
    values = [tp, fp, fn, tn]
    labels_pie = ['TP', 'FP', 'FN', 'TN']
    ax[1].pie(values, labels=labels_pie, autopct='%1.1f%%', startangle=90, colors=['green', 'red', 'orange', 'blue'])
    ax[1].set_title('Distribution')

    # Save the plot
    output_path = os.path.join(plot_folder, os.path.basename(file_name).replace('.txt', '.png'))
    plt.figtext(0.5, 0.01, f"Accuracy: {accuracy:.2f} | Precision: {precision:.2f} | Recall: {recall:.2f} | F1-score: {fscore:.2f}", ha="center")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved plot to {output_path}")

# Analyze specific files
analyze_and_plot('particular/prova10_p.txt')
analyze_and_plot('particular/prova10_n.txt')
