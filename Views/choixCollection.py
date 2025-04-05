from PySide6.QtWidgets import QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox, QWidget, QMainWindow
from PySide6.QtCore import Qt
from Services.mongoDb import MongoDB  # Importation de la classe MongoDB
import os  # Pour vérifier l'existence des fichiers et gérer les chemins
import json  # Importation de la bibliothèque JSON
from PySide6.QtGui import QIcon, QPainter
import sys
from Views.listeCollecte import ListeCollecteWindow  # Importation de la fenêtre ListeCollecteWindow


basedir = os.path.dirname(__file__)

def resource_path(relative_path):
    """ Donne le chemin absolu, compatible PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class ChoixCollectionWindow(QWidget):
    def __init__(self, parent=None):
        """Initialise la fenêtre du choix de collection avec un parent optionnel"""
        super().__init__()  # Passer le parent à QWidget
        # Reste du code de l'initialisation de la fenêtre

        self.setWindowTitle("Choix de la collection")
        self.setWindowIcon(QIcon(resource_path("Assets/logoKolectinfos.png")))  # Utilise resource_path
        self.setFixedSize(260, 160)

        layout = QVBoxLayout()

        # Sélection du type_collection pour l’analyse
        self.type_collection_label = QLabel("Collections :")
        self.type_collection_combo = QComboBox()
        layout.addWidget(self.type_collection_label)
        layout.addWidget(self.type_collection_combo)

        self.submit_button = QPushButton("Appliquer")
        self.submit_button.setStyleSheet("background-color: #FFFFFF; font-size: 16px; color: #000; border-radius: 5px; padding: 5px 15px 5px 15px; border: 3px solid #000; margin-top: 25px;")
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

        # Charger les collections
        self.load_collections()

        # Connecter le bouton au slot d'enregistrement
        self.submit_button.clicked.connect(self.save_choix)


    def load_collections(self):
        """Récupère les collections depuis MongoDB et les ajoute au comboBox."""
        try:
            db = MongoDB()
            collections = db.get_all_collections()
            self.type_collection_combo.addItems(collections)  # Ajoute les collections dans le comboBox
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de récupérer les collections : {e}")


    def save_choix(self):
        """
        Enregistre le choix dans un fichier config.json
        """
        selected_collection = self.type_collection_combo.currentText()  # Récupère la collection sélectionnée
        
        config_file = "config.json"
        
        # Vérifier si le fichier existe et charger les données existantes
        if os.path.exists(config_file):
            with open(config_file, 'r') as file:
                config_data = json.load(file)
        else:
            config_data = {}

        # Mettre à jour les données de configuration
        config_data["collection"] = selected_collection

        # Sauvegarder la configuration complète (remplace le contenu du fichier)
        with open(config_file, 'w') as file:
            json.dump(config_data, file, indent=4)  # Remplacement du contenu du fichier
        
        QMessageBox.information(self, "Succès", "Choix appliquer avec succès.")
            
        self.open_principale_window()  # Redirige vers principale
      
          
    def open_principale_window(self):
        """Ouvre le tableau de bord après connexion."""
        self.hide()  # Cacher la fenêtre actuelle
        self.principale_window = ListeCollecteWindow()  # Remplacez par votre fenêtre principale
        self.principale_window.show()

