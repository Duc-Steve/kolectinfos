from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtGui import QIcon, QPainter
from Views.choixCollection import ChoixCollectionWindow  # Importation de la fenêtre principale
import os
import sys


basedir = os.path.dirname(__file__)

def resource_path(relative_path):
    """ Donne le chemin absolu, compatible PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Classe principale pour la fenêtre d'accueil
class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Définir le titre et l'icône de la fenêtre
        self.setWindowTitle("Kolectinfos")
        self.setWindowIcon(QIcon(resource_path("Assets/logoKolectinfos.png")))  # Utilise resource_path

        # Définir la taille de la fenêtre
        self.setFixedSize(600, 500)

        # Créer un layout vertical
        layout = QVBoxLayout()

        # Ajouter le logo
        self.logo_label = QLabel(self)
        pixmap =  QPixmap(resource_path("Assets/logoKolectinfos.png"))  # Utilise resource_path
        self.logo_label.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo_label)

        # Message de bienvenue
        self.welcome_label = QLabel("Bienvenue à Kolectinfos")
        self.welcome_label.setAlignment(Qt.AlignCenter)
        self.welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #174140; margin-top: 20px")
        layout.addWidget(self.welcome_label)

        # Phrase d'introduction
        self.message_label = QLabel(
            "Kolectinfos, votre logiciel d'extraction de données qualitatives."
        )
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("font-size: 16px; color: #174140; margin-bottom: 20px")
        layout.addWidget(self.message_label)

        # Bouton "Commencer"
        self.start_button = QPushButton("Commencer")
        self.start_button.setStyleSheet(
            "background-color: #000; color: #FFFFFF; font-size: 18px; padding: 10px 20px; border-radius: 8px; border: 3px solid #FFFFFF;"
        )
        layout.addWidget(self.start_button)
        self.start_button.clicked.connect(self.allez_choix_collection_window)  

        # Centrer les éléments
        layout.setAlignment(Qt.AlignCenter)

        # Créer un widget central et lui appliquer le layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def allez_choix_collection_window(self):
        """Fonction pour rediriger vers la fenêtre de configuration"""
        self.hide()  # Cacher la fenêtre actuelle
        self.choix_collection_window = ChoixCollectionWindow()  # Passer l'instance courante en tant que parent à ChoixCollectionWindow
        self.choix_collection_window.show()
