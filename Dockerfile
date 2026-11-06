
# Image officielle Apache Airflow
FROM apache/airflow:2.9.2-python3.11

# Définition du répertoire de travail
WORKDIR /opt/airflow

# Copie du fichier des dépendances
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie des fichiers du projet
COPY etl/ ./etl/
COPY config.ini .
COPY config.yaml .
COPY dags/ ./dags/

