# importation du module
import pandas as pd

# Fonction extract data
def extract_data(filepath: object, select_cols: list, rename_cols: dict) -> object:
    """
       :filepath: Chemin du fichier CSV (de type chaîne de caractères).
       :select_cols : liste des colonnes à sélectionner à partir du fichier CSV.
       rename_cols : Dictionnaire pour renommer les colonnes sélectionnées.
    """
    try:
        # Le bloc try contient le code qui peut potentiellement causer des erreurs
        # Lire le CSV fichier
        df = pd.read_csv(filepath)
        df = df[select_cols]
        df = df.rename(columns={rename_cols})

    # Ce bloc capture l'erreur FileNotFoundError, qui se produit si le fichier spécifié par filepath
    #  n'est pas trouvé. L'erreur est assignée à la variable e et un message d'erreur est imprimé.
    except FileNotFoundError as e:
        print(f"Error: {e}")

    # Ce bloc capture toutes les autres exceptions qui ne sont pas spécifiquement gérées 
    # par les blocs except précédents
    except Exception as e:
        print(f"Error: {e}")

    return df

'''
except FileNotFoundError as e: : Ce bloc capture l'erreur FileNotFoundError, 
qui se produit si le fichier spécifié par filepath n'est pas trouvé. 
L'erreur est assignée à la variable e et un message d'erreur est imprimé.

print(f"Error: {e}") : Cette ligne imprime le message d'erreur lié à l'exception FileNotFoundError.

except Exception as e: : Ce bloc capture toutes les autres exceptions qui ne sont pas 
spécifiquement gérées par les blocs except précédents. Cela permet de gérer toute autre 
erreur non prévue. L'erreur est assignée à la variable e et un message d'erreur est imprimé.

print(f"Error: {e}") : Cette ligne imprime le message d'erreur lié à toute autre exception 
non spécifiée.
'''