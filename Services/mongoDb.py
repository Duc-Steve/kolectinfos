import os
import json
from pymongo import MongoClient
from PySide6.QtWidgets import QMessageBox

# Nom du fichier de configuration JSON
CONFIG_FILE = "config.json"

class MongoDB:
    def __init__(self):
        """Connexion à MongoDB"""
        try:
            self.config = self.load_configuration()  # Charger la configuration
            self.client = MongoClient("mongodb://localhost:27017/")  # Connexion à MongoDB
            self.db = self.client["kolectinfos"]  # Accéder à la base de données "kolectinfos"
            self.collection = self.db[self.config.get("collection")]  # Utilisation de la collection définie
        except Exception as e:
            QMessageBox.critical(None, "Erreur", f"Erreur de connexion : {e}")

    def save_data(self, message):
        """Enregistre un message dans MongoDB."""
        if message:
            self.collection.insert_one(message)  # Enregistrement direct des données
            return True
        return False

    def get_all_messages(self):
        """Récupère tous les messages stockés."""
        try:
            messages = list(self.collection.find({}, {"_id": 0}).sort("_id", -1))  # Exclut `_id`
            return messages if messages else []  # Retourne une liste vide si aucun message n'est trouvé
        except Exception as e:
            print(f"Erreur lors de la récupération des messages : {e}")
            return []
            
        
    def delete_all_messages(self):
        """Supprime tous les messages stockés."""
        try:
            result = self.collection.delete_many({})  # Supprime tous les documents de la collection
            if result.deleted_count > 0:
                print(f"{result.deleted_count} message(s) supprimé(s) avec succès.")
            else:
                print("Aucun message à supprimer.")
        except Exception as e:
            print(f"Erreur lors de la suppression des messages : {e}")


    def get_all_collections(self):
        """Récupère la liste de toutes les collections de la base de données."""
        return self.db.list_collection_names()

    def load_configuration(self):
        """Charge les données de configuration depuis le fichier JSON."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as file:
                    return json.load(file)  # Charge les données JSON
            except json.JSONDecodeError:
                QMessageBox.critical(None, "Erreur", "Le fichier de configuration est corrompu.")
        return self.create_default_config()

    def create_default_config(self):
        """Crée un fichier de configuration par défaut si inexistant ou corrompu."""
        default_config = {"collection": "informations"}
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as file:
                json.dump(default_config, file, indent=4)
        except Exception as e:
            QMessageBox.critical(None, "Erreur", f"Impossible de créer le fichier de configuration : {e}")
        return default_config
