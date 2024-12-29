# Usa un'immagine di base minimale di Python
FROM python:3.10-slim

# Imposta la directory di lavoro
WORKDIR /app

# Copia la cartella Secrets nel container
COPY Secrets1 /app/Secrets1

# Imposta i permessi corretti per la directory Secrets (opzionale)
RUN chmod -R 700 /app/Secrets1

# Esegui un comando di default
CMD ["ls", "-l", "/app/Secrets"]
