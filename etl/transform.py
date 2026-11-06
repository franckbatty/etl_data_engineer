"""Nettoyage et standardisation des données avec pandas."""
import pandas as pd

def transform_customers(customers_df):
    customers = customers_df.copy()
    customers["email"] = customers["email"].astype("string").str.strip().str.lower()
    customers["ville"] = customers["ville"].astype("string").str.strip().str.title()
    customers["date_inscription"] = pd.to_datetime(customers["date_inscription"], errors="coerce")
    customers = customers.drop_duplicates(subset=["id_client"], keep="first")
    return customers_df

def transform_orders(orders_df):
    orders = orders_df.copy()
    orders["produit"] = orders["produit"].astype("string").str.strip().str.title()
    orders["statut"] = orders["statut"].astype("string").str.strip().str.lower()
    orders["date_commande"] = pd.to_datetime(orders["date_commande"], errors="coerce")
    orders["quantite"] = pd.to_numeric(orders["quantite"], errors="coerce")
    orders["prix_unitaire"] = pd.to_numeric(orders["prix_unitaire"], errors="coerce")

    # Dédupliquer les commandes par identifiant.
    orders = orders.drop_duplicates(subset=["id_commande"], keep="first")
    orders["total_amount"] = orders["quantite"] * orders["prix_unitaire"]
    return orders_df  
