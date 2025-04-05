import json  # Module pour manipuler les fichiers JSON
import os  # Module pour vérifier l'existence de fichiers
from PySide6.QtWidgets import QApplication, QMessageBox  # Classes Qt pour la GUI
from Views.choixCollection import ChoixCollectionWindow  # Importation de la fenêtre principale
from Views.bienvenueKolectinfos import WelcomeWindow  # Importation de la fenêtre principale
import sys



# Nom du fichier de configuration JSON
CONFIG_FILE = "config.json"

def load_configuration():
    """ Charge les données de configuration depuis le fichier JSON. """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as file:
                return json.load(file)  # Charge les données JSON depuis le fichier
        except json.JSONDecodeError:
            # Gère les erreurs de décodage JSON
            QMessageBox.critical(None, "Erreur", "Le fichier de configuration est corrompu ou invalide.")
            return False
        except Exception as e:
            # Gère toute autre erreur
            QMessageBox.critical(None, "Erreur", f"Une erreur est survenue lors de la lecture du fichier de configuration : {str(e)}")
            return False
    else:
        # Si le fichier n'existe pas, retourne False
        return False


def main():
    """Point d'entrée principal de l'application."""
    app = QApplication([])  # Création de l'application Qt

    # Charge la configuration depuis le fichier JSON
    config = load_configuration()
    
    if config is False:
        # Si la configuration est valide, afficher la fenêtre WelcomeWindow
        welcome_window = WelcomeWindow()
        welcome_window.show()
    else:
        # Si la configuration n'est pas trouvée ou est invalide, afficher la fenêtre ChoixCollectionWindow
        choix_collection_window = ChoixCollectionWindow()
        choix_collection_window.show()

    # Exécute la boucle principale de l'application
    app.exec()


if __name__ == "__main__":
    main()  # Démarrer l'application
