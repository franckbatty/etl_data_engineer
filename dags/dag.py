# Import Modules
import yaml
# Le Module datetime est utilisés pour gérer les dates et les durées.
from datetime import (
    datetime,
    timedelta
)
# Importation de la fonction d'extration des données crées : extract_data 
from etl.extract import extract_data
from etl.transform import (
    transform_customers,
    transform_orders
)
from etl.load import load_data

'''Cette ligne importe la classe DAG (Directed Acyclic Graph) d'Apache Airflow.
qui vous permet de définir et de gérer des pipelines de données.'''

from airflow import DAG 
 
''' Cette ligne importe la classe PythonOperator d'Apache Airflow.
PythonOperator est utilisé pour définir des tâches qui exécutent des fonctions Python.'''

from airflow.operators.python import PythonOperator
 
# Ouverture du fichier YAML

with open('/opt/airflow/config.yaml', 'r') as file:
    config_data = yaml.safe_load(file)
# yaml.safe_load(file) : Cette fonction du module yaml lit le contenu du fichier ouvert et le convertit
# en une structure de données Python, telle qu'un dictionnaire.

## -----------------------Define the DAG
# Arguments par défaut à passer à chaque tâche : default_args
default_args = {
    'owner': 'Mon pipeline airflow', # Le nom de la personne qui developpe le Dag
    'depends_on_past': False,  # Indique si l'instance de la tâche dépend de l'instance de la tâche précédente.
    'start_date': datetime(2026, 11, 6), # Date de debut du Dag
    'retry_delay': timedelta(minutes=5), # Intervalle de temps après echelle après avoir lancé le Dag
    'catchup': False, # Indique si les exécutions manquées de DAG doivent être rattrapées.
}
# Initialisation du Dag 
dag = DAG('etl_dmv', 
        default_args=default_args, 
        schedule_interval=timedelta(days=1) # Le DAG est programmé pour s'exécuter une fois par jour
        ) 
# "etl_dmv" ; Nom du Dag
# schedule_interval : Définit la fréquence d'exécution du DAG.

# Definissons les TASKS
 
# Tasks d'Extraction de la données 

task_extract_customers = PythonOperator(
    task_id='extract_customers', # Identifiant unique de la tâche (extract de ."Nom de la tache"..)
    # python_callable prend une fonction Python en argument 
    python_callable=extract_data, # La fonction Python à exécuter la tâche.
# op_kwargs : Un dictionnaire d'arguments à passer à cette fonction.
    op_kwargs={'filepath': config_data['customers_filepath'],
               'select_cols': config_data['customers_columns_list'],
               'rename_cols': config_data['customers_columns_rename_dict']},
    dag=dag
) 
task_extract_orders = PythonOperator(
    task_id='extract_orders', # Identifiant unique de la tâche.
    python_callable=extract_data, # La fonction Python à exécuter la tâche.
    # op_kwargs : Un dictionnaire d'arguments à passer à cette fonction.
    op_kwargs={'filepath': config_data['orders_filepath'], 
               'select_cols': config_data['orders_columns_list'],  
               'rename_cols': config_data['orders_columns_rename_dict']},
    dag=dag
) 
'''
Les paramètres de op_kwargs sont des arguments de mot-clé que nous pouvons passer à la fonction Python 
définie dans python_callable.
Ils permettent de personnaliser le comportement de la tâche en fonction des besoins spécifiques.
'''

###############  Tasks de Transformer la données  

# Cette commande utilise le mécanisme XCom (Cross-Communication) d'Airflow pour récupérer les données
#  stockées par la tâche extract_customers.
task_transform_customers = PythonOperator(
    task_id='transform_customers',
    python_callable=transform_customers,
    op_kwargs={'customers_df': "{{ task_instance.xcom_pull(task_ids='extract_customers') }}"},
    dag=dag
)  

task_transform_orders = PythonOperator(
    task_id='transform_orders',
    python_callable=transform_orders,
    op_kwargs={'orders_df': "{{ task_instance.xcom_pull(task_ids='extract_orders') }}"},
    dag=dag
)

######################### Tasks de Chargement des données 

# Ce code crée un Task (tâche) de chargement des données dans 
# un DAG (Directed Acyclic Graph) d'Apache Airflow.
task_load_customers = PythonOperator(
    task_id='load_customers',
    python_callable=load_data,
    op_kwargs={'df': "{{ task_instance.xcom_pull(task_ids='transform_customers') }}",
               'create_PSQL': config_data['customers_create_PSQL'],
               'insert_PSQL': config_data['customers_insert_PSQL']},
    dag=dag
) 
''' 
    - Dans ce contexte de op_kwargs, Les données transformées par la tâche transform_customers 
    sont récupérées et utilisées dans cette tâche load_customers.

    - create_PSQL, Ce paramètre utilise la valeur customers_create_PSQL du dictionnaire config_data. 
    Il s'agit probablement d'une commande ou d'une instruction SQL pour créer des tables 
    ou d'autres objets dans PostgreSQL.

    - insert_PSQL, Ce paramètre utilise la valeur customers_insert_PSQL du dictionnaire config_data.
    Il s'agit probablement d'une commande ou d'une instruction SQL pour insérer des 
    données dans les tables de PostgreSQL.
    
    - customers_insert_PSQL : Cette commande SQL est utilisée pour insérer des valeurs dans la table customers
'''

task_load_orders = PythonOperator(
    task_id='load_orders',
    python_callable=load_data,
    op_kwargs={'df': "{{ task_instance.xcom_pull(task_ids='transform_orders') }}",
               'create_PSQL': config_data['orders_create_PSQL'],
               'insert_PSQL': config_data['orders_insert_PSQL']},
    dag=dag
)


# Lecture des Task. C'est à dire nous allons d'abord commencer avec ce format : ETL,
# task_extract_customers et on passe à
# task_transform_customers. Ansi de suite.
# Define the task dependencies
task_extract_customers >> task_transform_customers >> task_load_customers
task_extract_orders >> task_transform_orders >> task_load_orders 