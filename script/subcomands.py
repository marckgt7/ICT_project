import subprocess
from concurrent.futures import ThreadPoolExecutor
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



commands = {

    #1: Scan a repo for only verified secrets
    #"./trufflehog-3.84.1/trufflehog.exe git https://github.com/marckgt7/ProvaTruffle": "prova_Secrets1_git.txt",
    
    #2: Scan a GitHub Org for only verified secrets
    #"./trufflehog-3.84.1/trufflehog.exe github --repo=https://github.com/marckgt7/ProvaTruffle ": "prova_Secrets1_github.txt",
    
    #8: Scan individual files or directories
    #"./trufflehog-3.84.1/trufflehog.exe filesystem data/Secrets1/": "prova_Secrets1_filesystem.txt",
    #"./trufflehog-3.84.1/trufflehog.exe filesystem data/FakeSecrets1/": "prova_Secrets1_filesystem_fake.txt",


    #"./trufflehog-3.84.1/trufflehog.exe filesystem data/Secrets10/": "prova_Secrets10_filesystem.txt",
    #"./trufflehog-3.84.1/trufflehog.exe filesystem data/FakeSecrets10/": "prova_Secrets10_filesystem_fake.txt",

    "./trufflehog-3.84.1/trufflehog.exe filesystem data/Secrets1.txt": "prova_Secrets1_filesystem_unico_p.txt",
    "./trufflehog-3.84.1/trufflehog.exe filesystem data/Secrets10.txt": "prova_Secrets10_filesystem_unico_p.txt",

    #10: Scan a Docker image for verified secrets
    #"./trufflehog-3.84.1/trufflehog.exe docker --image localhost:5000/ict_project_image": "prova_Secrets1_docker.txt"
    
    #11: Scan in CI
    #"docker run --rm -it -v "+"${"+"PWD}:/pwd"+" trufflesecurity/trufflehog git file://. --since-commit main --branch feature-1 --only-verified --fail": "CI.txt",
    
    #12: Scan a Postman workspace
    #"./trufflehog-3.84.1/trufflehog.exe postman --token=PMAK-6773b476df32b80001cecf50-b2c92fe098a7cd06167ba17c43c380ebb3 --workspace-id=e2d7eb70-568c-4b1f-8500-87ddea278ca4 ": "prova_Secrets1_postman.txt",
    
    #13: Scan a Jenkins server
    #"docker run --rm -it -v "+"${"+"PWD}:/pwd"+" trufflesecurity/trufflehog jenkins --url https://jenkins.example.com --username admin --password admin": "jenkins.txt",
    
    #14: Scan an Elasticsearch server
    #"docker run --rm -it -v "+"${"+"PWD}:/pwd"+" trufflesecurity/trufflehog elasticsearch --nodes 192.168.14.3 192.168.14.4 --username truffle --password hog": "elastic.txt",
    
    #15: Scan a GitHub Repository for Cross Fork Object References and Deleted Commits
    #"docker run --rm -it -v "+"${"+"PWD}:/pwd"+" trufflesecurity/trufflehog github-experimental --repo https://github.com/<USER>/<REPO>.git --object-discovery": "cfordc.txt",
    
    #16: Scan Hugging Face
    #"docker run --rm -it -v "+"${"+"PWD}:/pwd"+" trufflesecurity/trufflehog huggingface --model <model_id> --include-discussions --include-prs": "hugging.txt"

}

# Funzione per eseguire un comando e salvare l'output
def run_command(command, output_file):
    try:
        # Esegui il comando PowerShell
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,  # Usa 'text=True' per trattare l'output come stringa
            encoding='utf-8',  # Forza la codifica UTF-8
            check=True
        )
        print("Sto facendo", command)
        # Salva il risultato nel file
        with open(output_file, "a", encoding='utf-8') as file:  # Usa UTF-8 anche per il file
            file.write(f"--- Output del comando '{command}' ---\n")
            file.write(result.stdout + "\n")
    except subprocess.CalledProcessError as e:
        # Salva eventuali errori nel file
        with open(output_file, "a", encoding='utf-8') as file:
            file.write(f"--- Errore nell'esecuzione di '{command}' ---\n")
            file.write(e.stderr + "\n")
            print("Ho fallito", command)


# Esegui i comandi contemporaneamente
results_dir = "./TruffleOutput"
os.makedirs(results_dir, exist_ok=True)
#delete_files_in_folder(os.path.join(results_dir))

with ThreadPoolExecutor() as executor:
    for command, output_file in commands.items():
        output_file = os.path.join(results_dir, output_file)
        executor.submit(run_command, command, output_file)