# Importation des modules
import psycopg2  
import configparser
import yaml
'''
     - Le Module psycopg2 est un adaptateur PostgreSQL pour le langage de programmation Python. 
     Il permet à Python de se connecter et d'interagir avec des bases de données PostgreSQL.

    - Le Module configparser est un module en Python utilisé pour manipuler des fichiers de configuration
    au format INI. Il Facilite la gestion des paramètres de configuration d'une applications.
    Il Permet de séparer les configurations du code, ce qui facilite la gestion et la maintenance.

    - Le Module yaml est un module en Python utilisé pour travailler avec des fichiers au format 
    YAML (YAML Ain't Markup Language).
    Il Permet de représenter des structures de données complexes de manière simple.
'''

# Cette ligne ouvre le fichier config.yaml en mode lecture ('r').
with open('../../config.yaml', 'r') as file:
# Cette ligne charge le contenu du fichier YAML dans une variable Python nommée config_data.
    config_data = yaml.safe_load(file) # La fonction safe_load () du module yaml lit le contenu 
                                       # du fichier et le convertit en une structure de données Python
                                       # (par exemple, un dictionnaire).

''' Cette fonction nous permet de charger des données dans une base de données PostgreSQL en utilisant un 
    DataFrame pandas, des commandes SQL, et des configurations stockées dans un fichier config.ini.

    create_PSQL: str : La commande SQL pour créer la table.

    insert_PSQL: str : La commande SQL pour insérer les données.

    -> object : Spécifie que la fonction retourne un objet.
'''
def load_data(df: object, create_PSQL: str, insert_PSQL: str) -> object:
    # Cette commande nous permet Crée un objet ConfigParser pour lire les fichiers de configuration.
    config = configparser.ConfigParser()  
    config.read('config.ini') # Permet de lire le fichier config.ini et charge les configurations.
# Connexion à la base de données PostgreSQL
    # psycopg2.connect : Établit une connexion à la base de données PostgreSQL en utilisant 
    # les paramètres de configuration lus depuis config.ini.
    conn = psycopg2.connect(
        host=config['POSTGRESQL']['host'],
        port=config['POSTGRESQL']['port'],
        dbname=config['POSTGRESQL']['database'],
        user=config['POSTGRESQL']['user'],
        password=config['POSTGRESQL']['password']
    )
# Création d'un curseur et exécution de la commande CREATE TABLE
    cursor = conn.cursor() # Crée un curseur pour exécuter les commandes SQL.
    cursor.execute(create_PSQL) # Exécute la commande SQL pour créer la table.
    conn.commit() # Valide (commit) la transaction de création de la table.

# Insertion des données dans la table
    for row in df.itertuples(index=False): # Itère sur chaque ligne du DataFrame sans inclure les index.
        cursor.execute(insert_PSQL, row) # Exécute la commande d'insertion SQL pour chaque ligne du DataFrame,
                                         # en passant les valeurs des colonnes comme arguments.

# Validation et fermeture des connexions.
    conn.commit() # Valide (commit) toutes les transactions d'insertion.
    cursor.close() # Ferme le curseur.
    conn.close()   # Ferme la connexion à la base de données. 
  