
# ============================================================
# IMPORTATION DES MODULES
# ============================================================

import psycopg2
import yaml
from pathlib import Path


'''
- Le module psycopg2 est un adaptateur PostgreSQL pour Python.
  Il permet à Python de se connecter et d'interagir avec une
  base de données PostgreSQL.

- Le module yaml permet de lire et de manipuler les fichiers
  au format YAML.

- Le module pathlib permet de manipuler les chemins d'accès
  aux fichiers de manière fiable.
'''


# ============================================================
# CHARGEMENT DU FICHIER DE CONFIGURATION YAML
# ============================================================

# Récupération du chemin absolu du dossier racine du projet.
CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.yaml"

# Ouverture du fichier config.yaml en mode lecture.
with open(CONFIG_PATH, 'r', encoding='utf-8') as file:

    # Lecture du contenu YAML et conversion en dictionnaire Python.
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

def load_data(df, create_PSQL: str, insert_PSQL: str) -> None:

    # --------------------------------------------------------
    # 1. RÉCUPÉRATION DES PARAMÈTRES DE CONNEXION
    # --------------------------------------------------------

    # Récupération des paramètres PostgreSQL depuis config.yaml.
    postgres_config = config_data['postgresql']


    # --------------------------------------------------------
    # 2. CONNEXION À LA BASE DE DONNÉES POSTGRESQL
    # --------------------------------------------------------

    conn = None
    cursor = None

    try:

        # Établissement de la connexion à PostgreSQL.
        conn = psycopg2.connect(
            host=postgres_config['host'],
            port=postgres_config['port'],
            dbname=postgres_config['database_name'],
            user=postgres_config['username'],
            password=postgres_config['password']
        )

        # Création d'un curseur pour exécuter les commandes SQL.
        cursor = conn.cursor()


        # ----------------------------------------------------
        # 3. CRÉATION DU SCHÉMA POSTGRESQL
        # ----------------------------------------------------

        # Création du schéma s'il n'existe pas encore.
        cursor.execute(config_data['schema_create_PSQL'])


        # ----------------------------------------------------
        # 4. CRÉATION DE LA TABLE
        # ----------------------------------------------------

        # Exécution de la commande SQL de création de la table.
        cursor.execute(create_PSQL)


        # ----------------------------------------------------
        # 5. INSERTION DES DONNÉES
        # ----------------------------------------------------

        # Parcours de chaque ligne du DataFrame sans récupérer l'index.
        for row in df.itertuples(index=False, name=None):

            # Insertion des valeurs dans PostgreSQL.
            cursor.execute(insert_PSQL, row)


        # ----------------------------------------------------
        # 6. VALIDATION DE LA TRANSACTION
        # ----------------------------------------------------

        # Validation de la création du schéma, de la table
        # et de l'insertion des données.
        conn.commit()

        print(
            f"{len(df)} lignes chargées avec succès "
            f"dans la table PostgreSQL."
        )


    except Exception as e:

        # Annulation de toutes les opérations en cas d'erreur.
        if conn is not None:
            conn.rollback()

        raise RuntimeError(
            f"Erreur lors du chargement des données : {e}"
        ) from e


    finally:

        # ----------------------------------------------------
        # 7. FERMETURE DES RESSOURCES
        # ----------------------------------------------------

        # Fermeture du curseur.
        if cursor is not None:
            cursor.close()

        # Fermeture de la connexion PostgreSQL.
        if conn is not None:
            conn.close()
