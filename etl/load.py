
# ============================================================
# IMPORTATION DES MODULES
# ============================================================

import psycopg2
import configparser
import yaml
from pathlib import Path


'''
- Le module psycopg2 est un adaptateur PostgreSQL pour Python.
  Il permet à Python de se connecter et d'interagir avec une
  base de données PostgreSQL.

- Le module configparser permet de manipuler les fichiers de
  configuration au format INI. Il facilite la séparation des
  paramètres de configuration du code Python.

- Le module yaml permet de lire et de manipuler les fichiers
  au format YAML (YAML Ain't Markup Language). Il permet de
  convertir les données YAML en structures Python.
  
- Le module pathlib permet de manipuler les chemins d'accès
  aux fichiers de manière fiable, quel que soit le répertoire
  depuis lequel le programme est exécuté.
'''


# ============================================================
# CHARGEMENT DU FICHIER DE CONFIGURATION YAML
# ============================================================

# Récupération du chemin absolu du dossier racine du projet.
# __file__ représente le chemin du fichier load.py.
# parents[1] remonte de etl/ vers le dossier racine du projet.
CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.yaml"

# Ouverture du fichier config.yaml en mode lecture.
with open(CONFIG_PATH, 'r', encoding='utf-8') as file:

    # Lecture du contenu YAML et conversion en dictionnaire Python.
    # safe_load() permet de charger les données YAML de manière sécurisée.
    config_data = yaml.safe_load(file)


'''
Cette fonction permet de charger les données d'un DataFrame
Pandas dans une base de données PostgreSQL.

Paramètres :
    df : DataFrame contenant les données à charger.
    create_PSQL : commande SQL permettant de créer la table.
    insert_PSQL : commande SQL permettant d'insérer les données.

Retour :
    None : la fonction ne retourne pas de valeur.
'''


# ============================================================
# FONCTION DE CHARGEMENT DES DONNÉES (LOAD)
# ============================================================

def load_data(df: object, create_PSQL: str, insert_PSQL: str) -> None:

    # --------------------------------------------------------
    # 1. LECTURE DU FICHIER DE CONFIGURATION INI
    # --------------------------------------------------------

    # Création d'un objet ConfigParser pour lire le fichier INI.
    config = configparser.ConfigParser()

    # Définition du chemin absolu du fichier config.ini.
    CONFIG_INI_PATH = Path(__file__).resolve().parents[1] / "config.ini"

    # Lecture des paramètres de connexion PostgreSQL.
    config.read(CONFIG_INI_PATH, encoding='utf-8')


    # --------------------------------------------------------
    # 2. CONNEXION À LA BASE DE DONNÉES POSTGRESQL
    # --------------------------------------------------------

    # psycopg2.connect() établit une connexion à PostgreSQL
    # à partir des paramètres contenus dans config.ini.
    conn = psycopg2.connect(
        host=config['POSTGRESQL']['host'],
        port=config['POSTGRESQL']['port'],
        dbname=config['POSTGRESQL']['database'],
        user=config['POSTGRESQL']['user'],
        password=config['POSTGRESQL']['password']
    )

    # --------------------------------------------------------
    # 3. CRÉATION DU CURSEUR ET DE LA TABLE
    # --------------------------------------------------------

    # Création d'un curseur pour exécuter les commandes SQL.
    cursor = conn.cursor()

    # Exécution de la commande SQL de création de la table.
    cursor.execute(create_PSQL)

    # Validation de la transaction de création de la table.
    conn.commit()


    # --------------------------------------------------------
    # 4. INSERTION DES DONNÉES
    # --------------------------------------------------------

    # Parcours de chaque ligne du DataFrame sans récupérer l'index.
    for row in df.itertuples(index=False):

        # Insertion des valeurs de la ligne dans PostgreSQL.
        cursor.execute(insert_PSQL, row)


    # --------------------------------------------------------
    # 5. VALIDATION ET FERMETURE DES RESSOURCES
    # --------------------------------------------------------

    # Validation de toutes les opérations d'insertion.
    conn.commit()

    # Fermeture du curseur.
    cursor.close()

    # Fermeture de la connexion à PostgreSQL.
    conn.close()
