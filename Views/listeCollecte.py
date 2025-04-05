from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QDialog, QPushButton, QHBoxLayout, QLineEdit,
    QTableWidget, QTableWidgetItem, QInputDialog, QFileDialog, QMessageBox, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPainter
from PySide6.QtCore import QSize
from Views.dataExtraction import DataExtractorApp  # Import de la fenêtre DataExtractorApp
from Services.mongoDb import MongoDB  # Importation de la classe MongoDB
import pandas as pd  # Pour l'export en Excel
from Services.dataAction import save_message  # Service pour enregistrer les données
import os
import sys


basedir = os.path.dirname(__file__)

def resource_path(relative_path):
    """ Donne le chemin absolu, compatible PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)



class ListeCollecteWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Données")
        self.setWindowIcon(QIcon(resource_path("Assets/logoKolectinfos.png")))  # Utilise resource_path
        self.setFixedSize(1200, 650)
        
        main_layout = QVBoxLayout()
        
        
        # Layout des boutons en haut
        top_button_layout = QHBoxLayout()

        # Ajouter un espace vide de 80% au début (les boutons occuperont 80% de l'espace)
        top_button_layout.addStretch(1)  # Cette ligne fait en sorte que les boutons occupent 80% de l'espace

        # Bouton "Changer de collection"
        add_button = QPushButton("Changer de collection")
        add_button.clicked.connect(self.ouvrir_changer_collecte)
        add_button.setStyleSheet("margin-bottom: 15px; padding: 10px; padding-top: 15px; padding-bottom: 15px; font-size: 14px; background-color: #000; color: #FFFFFF; border-radius: 5px; border: 3px solid #FFFFFF;")
        top_button_layout.addWidget(add_button)

        # Bouton "Exporter"
        export_button = QPushButton("Exporter")
        export_button.clicked.connect(self.show_export_options)
        export_button.setStyleSheet("margin-bottom: 15px; padding: 10px; padding-top: 15px; padding-bottom: 15px; font-size: 14px; background-color: #000; color: #FFFFFF; border-radius: 5px; border: 3px solid #FFFFFF;")
        top_button_layout.addWidget(export_button)

        # Bouton "Transformation"
        self.transformation_button = QPushButton("Transformation")
        self.transformation_button.setStyleSheet("margin-bottom: 15px; padding: 10px; padding-top: 15px; padding-bottom: 15px; font-size: 14px; background-color: #000; color: #FFFFFF; border-radius: 5px; border: 3px solid #FFFFFF;")
        self.transformation_button.clicked.connect(self.open_data_transformation)
        top_button_layout.addWidget(self.transformation_button)

        # Bouton "Extracteur"
        self.extract_button = QPushButton("Extracteur")
        self.extract_button.setStyleSheet("margin-bottom: 15px; padding: 10px; padding-top: 15px; padding-bottom: 15px; font-size: 14px; background-color: #FFFFFF; color: #000; border-radius: 5px; border: 3px solid #000;")
        self.extract_button.clicked.connect(self.open_data_extractor)
        top_button_layout.addWidget(self.extract_button)

        # Bouton "Rafraichir"
        rafraichir_button = QPushButton()
        rafraichir_button.setIcon(QIcon("Assets/icons/refresh.png"))  # Chemin de l'icône de rafraîchissement
        rafraichir_button.setIconSize(QSize(40, 40))  # Taille de l'icône
        rafraichir_button.setStyleSheet("margin-bottom: 15px; padding: 10px; padding-top: 15px; padding-bottom: 15px; font-size: 14px; background-color: #FFFFFF; color: #000; border-radius: 5px; border: 3px solid red;")
        rafraichir_button.clicked.connect(self.refresh_tableau)
        top_button_layout.addWidget(rafraichir_button)

        # Ajouter un espace vide de 20% à la fin (cela prend 20% de l'espace restant)
        spacer = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        top_button_layout.addItem(spacer)
        
        main_layout.addLayout(top_button_layout)
        
        # Ajout de la barre de recherche
        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher...")
        self.search_input.textChanged.connect(self.update_table_data)
        filter_layout.addWidget(self.search_input)
        main_layout.addLayout(filter_layout)
        

        # Création du tableau avec **0 lignes** et **4 colonnes**
        self.table = QTableWidget(0, 4, self)  # Pas de ligne par défaut
        self.table.setFixedSize(1180, 500)
        
        # Titres des colonnes
        column_titles = ["Pertinence", "Contexte", "Informations clés", "Source"]
        self.table.setHorizontalHeaderLabels(column_titles)
        
        # Remplir le tableau avec des données
        self.populate_table()
        
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)
        
    
    def open_data_transformation(self):
        """ Transformation des données"""
        db = MongoDB()
        documents = db.get_all_messages()  # Récupère les documents de la collection
        
        # Supprimer tous les messages existants après récupération
        delete = db.delete_all_messages()

        # Liste pour stocker les données transformées
        transformed_data = []
        
        for doc in documents:
            # Récupère les informations brutes des documents
            raw_info = doc.get("informations_cles", "")
            context = doc.get("contexte", "")
            source = doc.get("source", "")
            pertinence = doc.get("pertinence", "")

            # Transformation des informations brutes en un format plus structuré
            processed_info = self.process_information(raw_info)
            
            # Créer un dictionnaire pour la donnée transformée
            transformed_data = {
                "contexte": context,
                "informations_cles": processed_info,
                "source": source,
                "pertinence": pertinence
            }
            
            # Sauvegarde de la donnée transformée dans la base de données
            save_message(transformed_data)
            
        QMessageBox.information(self, "Transformation", "Transformation réussi avec succès")



    def process_information(self, raw_info):
        """Transforme les informations brutes en un format plus exploitable"""
        # Exemple de traitement: Supprimer les lignes vides et fusionner en une seule phrase
        processed_info = raw_info.split("\n")  # Supposons que les informations sont séparées par des sauts de ligne
        
        # Nettoyer les lignes vides et fusionner en une seule chaîne
        processed_info = " ".join([item.strip() for item in processed_info if item.strip()])
        
        return processed_info
        
        
    def mettre_a_jour_tableau(self):
        """Mettre à jour le tableau avec les nouveaux pays"""
        # Cette méthode devrait recharger les données de l'API et mettre à jour le tableau
        self.populate_table()
        
            
    def refresh_tableau(self):
        """Rafraîchir le tableau"""
        QMessageBox.information(self, "Rafraîchissement", "Vous venez de rafraîchir les données")
        self.populate_table()
          
    def populate_table(self):
        """Remplir le tableau avec des données de MongoDB"""
        db = MongoDB()
        documents = db.get_all_messages()  # Récupère les documents de la collection
        
        self.table.setRowCount(len(documents))  # Définit le nombre de lignes du tableau
        
        # Définition des largeurs des colonnes
        self.table.setColumnWidth(0, 100)  # Largeur de la colonne pertinence
        self.table.setColumnWidth(1, 170)  # Largeur de la colonne Contexte
        self.table.setColumnWidth(2, 500)  # Largeur de la colonne Informations Clés
        self.table.setColumnWidth(3, 350)  # Largeur de la colonne Source

        for row, doc in enumerate(documents):
            # Vérifier si `_id` est un dictionnaire contenant `$oid`, sinon le convertir en chaîne
            doc_id = str(doc.get('_id', {}).get('$oid', 'N/A')) if isinstance(doc.get('_id'), dict) else str(doc.get('_id', 'N/A'))

            self.table.setItem(row, 0, QTableWidgetItem(doc.get('pertinence', '')))  # Contexte
            self.table.setItem(row, 1, QTableWidgetItem(doc.get('contexte', '')))  # Contexte
            self.table.setItem(row, 2, QTableWidgetItem(doc.get('informations_cles', '')))  # Informations clés
            self.table.setItem(row, 3, QTableWidgetItem(doc.get('source', '')))  # Source
        
    def open_data_extractor(self):
        """Ouvre l'extracteur."""
        self.data_extractor_window = DataExtractorApp()
        self.data_extractor_window.donnee_extrait.connect(self.mettre_a_jour_tableau)
        self.data_extractor_window.exec_()
        
    def update_table_data(self):
        search_text = self.search_input.text().lower()
        
        for row in range(self.table.rowCount()):
            text_match = any(
                search_text in (self.table.item(row, col).text().lower() if self.table.item(row, col) else "")
                for col in range(self.table.columnCount())
            )
            
            if text_match:
                self.table.showRow(row)
            else:
                self.table.hideRow(row)
    
    def show_export_options(self):
        options = ["Excel"]
        selected_option, ok = QInputDialog.getItem(self, "Choisir le format", "Format d'exportation :", options, 0, False)
        
        if ok and selected_option:
            if selected_option == "Excel":
                self.export_to_excel()
    
    def export_to_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "Enregistrer le fichier Excel", "", "Fichiers Excel (*.xlsx)")
        if not path:
            return

        data = []
        headers = [self.table.horizontalHeaderItem(col).text() for col in range(self.table.columnCount())]
        
        for row in range(self.table.rowCount()):
            if not self.table.isRowHidden(row):
                row_data = [self.table.item(row, col).text() if self.table.item(row, col) else "" for col in range(self.table.columnCount())]
                data.append(row_data)
        
        df = pd.DataFrame(data, columns=headers)
        try:
            df.to_excel(path, index=False)
            QMessageBox.information(self, "Exportation réussie", f"Le fichier a été exporté avec succès à l'emplacement : {path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur d'exportation", f"Une erreur s'est produite : {str(e)}")
    

    def ouvrir_changer_collecte(self):
        from Views.choixCollection import ChoixCollectionWindow  # Importation de la fenêtre ChoixCollectionWindow
        """Ouvre la fenetre de choix."""
        self.hide()  # Cacher la fenêtre actuelle
        self.choix_window = ChoixCollectionWindow()  # Remplacez par votre fenêtre principale
        self.choix_window.show()
        