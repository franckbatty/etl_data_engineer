
# ============================================================
# IMPORTATION DES MODULES
# ============================================================

import yaml

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

# Importation des fonctions ETL
from etl.extract import extract_data

from etl.transform import (
    transform_customers,
    transform_orders
)

from etl.load import load_data


# ============================================================
# LECTURE DU FICHIER DE CONFIGURATION YAML
# ============================================================

with open('/opt/airflow/config.yaml', 'r') as file:
    config_data = yaml.safe_load(file)


# ============================================================
# CONFIGURATION DU DAG
# ============================================================

default_args = {
    'owner': 'Mon pipeline airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 11, 6),
    'retry_delay': timedelta(minutes=5),
    'retries': 2
}


# Initialisation du DAG
with DAG(
    dag_id='etl_dmv',
    default_args=default_args,
    schedule=timedelta(days=1),
    catchup=False,
    description='Pipeline ETL des clients et des commandes'
) as dag:


    # ========================================================
    # 1. EXTRACTION DES DONNÉES
    # ========================================================

    task_extract_customers = PythonOperator(
        task_id='extract_customers',
        python_callable=extract_data,
        op_kwargs={
            'filepath': config_data['customers_filepath'],
            'select_cols': config_data['customers_columns_list'],
            'rename_cols': config_data['customers_columns_rename_dict']
        }
    )


    task_extract_orders = PythonOperator(
        task_id='extract_orders',
        python_callable=extract_data,
        op_kwargs={
            'filepath': config_data['orders_filepath'],
            'select_cols': config_data['orders_columns_list'],
            'rename_cols': config_data['orders_columns_rename_dict']
        }
    )


    # ========================================================
    # 2. TRANSFORMATION DES DONNÉES
    # ========================================================

    task_transform_customers = PythonOperator(
        task_id='transform_customers',
        python_callable=transform_customers,
        op_kwargs={
            'customers_df': task_extract_customers.output
        }
    )


    task_transform_orders = PythonOperator(
        task_id='transform_orders',
        python_callable=transform_orders,
        op_kwargs={
            'orders_df': task_extract_orders.output
        }
    )


    # ========================================================
    # 3. CHARGEMENT DES DONNÉES DANS POSTGRESQL
    # ========================================================

    task_load_customers = PythonOperator(
        task_id='load_customers',
        python_callable=load_data,
        op_kwargs={
            'df': task_transform_customers.output,
            'create_PSQL': config_data['customers_create_PSQL'],
            'insert_PSQL': config_data['customers_insert_PSQL']
        }
    )


    task_load_orders = PythonOperator(
        task_id='load_orders',
        python_callable=load_data,
        op_kwargs={
            'df': task_transform_orders.output,
            'create_PSQL': config_data['orders_create_PSQL'],
            'insert_PSQL': config_data['orders_insert_PSQL']
        }
    )


    # ========================================================
    # 4. DÉFINITION DES DÉPENDANCES
    # ========================================================

    # Branche des clients
    task_extract_customers >> task_transform_customers >> task_load_customers

    # Le chargement des commandes attend les deux tâches précédentes.
    # Branche des commandes
    task_extract_orders >> task_transform_orders

    # Le chargement des commandes attend les deux tâches précédentes.
    task_load_customers >> task_load_orders
    task_transform_orders >> task_load_orders