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

# Cancella i file prima di eseguire i comandi
delete_files_in_folder(r"C:\Users\carlo\OneDrive\Desktop\MAGISTRALE\ICT\results")

commands = {

    #1: Scan a repo for only verified secrets
    "docker run --rm -it -v "+"${"+"PWD}:/pwd"+" trufflesecurity/trufflehog git https://github.com/trufflesecurity/test_keys --only-verified": "repo.txt",
    
    #2: Scan a GitHub Org for only verified secrets
    "docker run --rm -it -v "+"${"+"PWD}:/pwd"+" trufflesecurity/trufflehog github --org=trufflesecurity --only-verified": "git_org.txt",
    
    #4: Scan a GitHub Repo + its Issues and Pull Requests
    "docker run --rm -it -v "+"${"+"PWD}:/pwd"+" trufflesecurity/trufflehog github --repo https://github.com/trufflesecurity/test_keys --issue-comments --pr-comments": "repo_issues_prs.txt",
    
    #5: Scan an S3 bucket for verified keys
    "docker run --rm -it -v "+"${"+"PWD}:/pwd"+" trufflesecurity/trufflehog s3 --bucket=<bucket name> --only-verified": "s3.txt",
    
    #6: Scan S3 buckets using IAM Roles
    "docker run --rm -it -v "+"${"+"PWD}:/pwd"+" trufflesecurity/trufflehog s3 --role-arn=<iam role arn>": "s3_iam_roles.txt",
    
    #7: Scan a Github Repo using SSH authentication in docker
    "docker run --rm -it -v "+"${"+"PWD}:/pwd"+" -v $HOME/.ssh:/root/.ssh:ro trufflesecurity/trufflehog:latest git ssh://github.com/trufflesecurity/test_keys": "repo_ssh.txt",
    
    #8: Scan individual files or directories
    "docker run --rm -it -v "+"${"+"PWD}:/pwd"+" trufflesecurity/trufflehog filesystem path/to/file1.txt path/to/file2.txt path/to/dir": "files.txt",
    
    #9: Scan GCS buckets for verified secrets
    "docker run --rm -it -v "+"${"+"PWD}:/pwd"+" trufflesecurity/trufflehog gcs --project-id=<project-ID> --cloud-environment --only-verified": "gcs.txt",
    
    #10: Scan a Docker image for verified secrets
    "docker run --rm -it -v "+"${"+"PWD}:/pwd"+" trufflesecurity/trufflehog docker --image trufflesecurity/secrets --only-verified": "docker_image.txt",
    
    #11: Scan in CI
    "docker run --rm -it -v "+"${"+"PWD}:/pwd"+" trufflesecurity/trufflehog git file://. --since-commit main --branch feature-1 --only-verified --fail": "CI.txt",
    
    #12: Scan a Postman workspace
    "docker run --rm -it -v "+"${"+"PWD}:/pwd"+" trufflesecurity/trufflehog postman --token=<postman api token> --workspace-id=<workspace id>": "postman.txt",
    
    #13: Scan a Jenkins server
    "docker run --rm -it -v "+"${"+"PWD}:/pwd"+" trufflesecurity/trufflehog jenkins --url https://jenkins.example.com --username admin --password admin": "jenkins.txt",
    
    #14: Scan an Elasticsearch server
    "docker run --rm -it -v "+"${"+"PWD}:/pwd"+" trufflesecurity/trufflehog elasticsearch --nodes 192.168.14.3 192.168.14.4 --username truffle --password hog": "elastic.txt",
    
    #15: Scan a GitHub Repository for Cross Fork Object References and Deleted Commits
    "docker run --rm -it -v "+"${"+"PWD}:/pwd"+" trufflesecurity/trufflehog github-experimental --repo https://github.com/<USER>/<REPO>.git --object-discovery": "cfordc.txt",
    
    #16: Scan Hugging Face
    "docker run --rm -it -v "+"${"+"PWD}:/pwd"+" trufflesecurity/trufflehog huggingface --model <model_id> --include-discussions --include-prs": "hugging.txt"

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
        # Salva il risultato nel file
        with open(output_file, "a", encoding='utf-8') as file:  # Usa UTF-8 anche per il file
            file.write(f"--- Output del comando '{command}' ---\n")
            file.write(result.stdout + "\n")
    except subprocess.CalledProcessError as e:
        # Salva eventuali errori nel file
        with open(output_file, "a", encoding='utf-8') as file:
            file.write(f"--- Errore nell'esecuzione di '{command}' ---\n")
            file.write(e.stderr + "\n")

# Esegui i comandi contemporaneamente
with ThreadPoolExecutor() as executor:
    for command, output_file in commands.items():
        output_file = os.path.join("results", output_file)
        executor.submit(run_command, command, output_file)