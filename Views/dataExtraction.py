import sys
import re
import os
import requests
import pdfplumber
import spacy
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
    QComboBox, QTextEdit, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPainter
from bs4 import BeautifulSoup
from Services.dataAction import save_message  # Service pour enregistrer les données
from sklearn.feature_extraction.text import TfidfVectorizer
from PySide6.QtCore import Signal
import os
import sys


basedir = os.path.dirname(__file__)

def resource_path(relative_path):
    """ Donne le chemin absolu, compatible PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)





# Charger le modèle NLP en français
nlp = spacy.load("fr_core_news_lg")

class DataExtractorApp(QDialog):
    
    # Définir un signal personnalisé
    donnee_extrait = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Extracteur des Données")
        self.setWindowIcon(QIcon(resource_path("Assets/logoKolectinfos.png")))  # Utilise resource_path
        self.setFixedSize(700, 450)  # Définit la taille fixe de la fenêtre
        
        layout = QVBoxLayout()  # Layout principal en vertical
        
         # Sélection du type de fichier
        self.type_label = QLabel("Type de contenu :")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["HTML", "PDF", "TEXTE"])
        self.type_combo.currentIndexChanged.connect(self.toggle_input_fields)
        layout.addWidget(self.type_label)
        layout.addWidget(self.type_combo)

        # Champ pour entrer l'URL ou le fichier à analyser
        self.url_label = QLabel("URL web ou fichier :")
        self.url_input = QLineEdit()
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)

        # Textarea pour la saisie (initialement caché)
        self.text_area = QTextEdit()
        self.text_area.setPlaceholderText("Saisir la description ici...")
        self.text_area.hide()  # Caché au démarrage
        layout.addWidget(self.text_area)

        # Sélection du contexte pour l'analyse
        self.contexte_label = QLabel("Contextes :")
        self.contexte_combo = QComboBox()
        self.contexte_combo.addItems([
            "Politique et légal", "Economique", "Socioculturel", 
            "Technologique", "Environnemental", "Financements internationaux"
        ])
        layout.addWidget(self.contexte_label)
        layout.addWidget(self.contexte_combo)

        # Champ pour entrer les mots-clés à rechercher
        self.keywords_label = QLabel("Mots-clés à rechercher (séparés par des virgules) :")
        self.keywords_input = QLineEdit()
        layout.addWidget(self.keywords_label)
        layout.addWidget(self.keywords_input)
        
        # Ajouter les boutons Enregistrer et Annuler
        self.button_layout = QHBoxLayout()
        self.button_layout.setContentsMargins(0, 30, 0, 0)  # Marges pour le bouton
        self.cancel_button = QPushButton("Annuler")
        self.extract_button = QPushButton("Extraire les données")
        # Styles pour les boutons
        self.extract_button.setStyleSheet("background-color: #FFFFFF; font-size: 16px; color: #000; border-radius: 5px; padding: 5px 15px 5px 15px; border: 3px solid #000;")
        self.cancel_button.setStyleSheet("background-color: #000; font-size: 16px; color: #FFFFFF; border-radius: 5px; padding: 5px 15px 5px 15px; border: 3px solid #FFFFFF;")
        
        # action
        self.extract_button.clicked.connect(self.extract_data)
        self.cancel_button.clicked.connect(self.close)  # Fermer la fenêtre à la demande

        # Alignement à droite des boutons
        self.button_layout.addStretch()  # Ajoute un espace élastique pour pousser les boutons à droite
        self.button_layout.addWidget(self.extract_button)
        self.button_layout.addWidget(self.cancel_button)

        layout.addLayout(self.button_layout)
        
        self.setLayout(layout)  # Appliquer le layout principal
        
    def toggle_input_fields(self):
        """Affiche ou cache les champs en fonction du type sélectionné."""
        if self.type_combo.currentText() == "TEXTE":
            self.url_label.show()
            self.url_input.show()
            self.text_area.show()
        else:
            self.text_area.hide()
            self.url_label.show()
            self.url_input.show()
            
    def extract_text(self, url, content_type):
        """Récupère le texte d'une URL selon le type de contenu (HTML ou PDF)"""
        try:
            response = requests.get(url, timeout=30)  # Récupère la page avec un timeout de 30 secondes
            response.raise_for_status()  # Vérifie si la requête a réussi
            
            if content_type == "HTML":
                # Extraction du texte brut à partir du HTML
                soup = BeautifulSoup(response.text, "html.parser")
                return soup.get_text(separator='\n', strip=True)
            
            elif content_type == "PDF":
                # Télécharge et enregistre temporairement le PDF
                with open("temp.pdf", "wb") as f:
                    f.write(response.content)

                # Extraction du texte depuis le fichier PDF
                with pdfplumber.open("temp.pdf") as pdf:
                    texte = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

                # Suppression du fichier temporaire
                os.remove("temp.pdf")

                # Retour du texte extrait
                return texte
        
        except requests.exceptions.RequestException as e:
            # Affiche une erreur si la récupération échoue
            QMessageBox.critical(self, "Erreur", f"Impossible de récupérer la page : {e}")
            return None
            
    def analyze_text(self, text, keywords, contexte_type, content_type, url):
        """Analyse et extrait les phrases pertinentes selon les mots-clés"""
        
        doc = nlp(text)  # Analyse NLP du texte
        extracted_data = []  # Liste pour stocker les phrases extraites

        # Prétraitement des mots-clés (évite les recalculs)
        keyword_docs = {kw: nlp(kw) for kw in keywords}
        
        # Créer le vectoriseur TF-IDF
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([text])  # Transforme le texte en matrice TF-IDF
        

        for sent in doc.sents:  # Parcourir chaque phrase
            sent_doc = nlp(sent.text)  # Analyse NLP de la phrase
            
            # si ces un pdf
            if content_type == "PDF":
                
                # Vérification de la similarité NLP avec un seuil dynamique
                for keyword, keyword_doc in keyword_docs.items():
                    if sent_doc.vector_norm and keyword_doc.vector_norm:
                        similarity = sent_doc.similarity(keyword_doc)
                        
                        # Appliquer un seuil adaptatif
                        seuil = 0.65 
                        if similarity > seuil:
                            extracted_data.append({
                                "contexte": contexte_type + " (" + keyword + ")",
                                "informations_cles": sent.text,
                                "source": url,
                                "pertinence": f"similarité NLP ({similarity:.2f})"
                            })
                
            else:
                
                # Vérification du mot-clé exact
                for keyword in keywords:
                    if keyword.lower() in sent.text.lower():  # Vérification du mot-clé exact
                        extracted_data.append({
                            "contexte": contexte_type + " (" + keyword + ")",
                            "informations_cles": sent.text,
                            "source": url,
                            "pertinence": "mot-clé exact"
                        })

                # Vérification de la similarité NLP avec un seuil dynamique
                for keyword, keyword_doc in keyword_docs.items():
                    if sent_doc.vector_norm and keyword_doc.vector_norm:
                        similarity = sent_doc.similarity(keyword_doc)
                        
                        # Appliquer un seuil adaptatif
                        seuil = 0.5 if len(keyword) < 5 else 0.6  # Plus strict pour mots courts
                        if similarity > seuil:
                            extracted_data.append({
                                "contexte": contexte_type + " (" + keyword + ")",
                                "informations_cles": sent.text,
                                "source": url,
                                "pertinence": f"similarité ({similarity:.2f})"
                            })
                
                # Vérification TF-IDF pour chaque mot-clé
                tfidf_scores = [tfidf_matrix[0, vectorizer.vocabulary_.get(keyword, 0)] for keyword in keywords]
                max_tfidf = max(tfidf_scores) if tfidf_scores else 0

                if max_tfidf > 0.1:
                    extracted_data.append({
                        "contexte": contexte_type + " (" + keyword + ")",
                        "informations_cles": sent.text,
                        "source": url,
                        "pertinence": f"vérification ({max_tfidf:.2f})"
                    })
                
        # Suppression des doublons et gestion de la pertinence
        seen_sentences = {}  # Dictionnaire pour suivre les phrases et leur fréquence
        cleaned_data = []
        
        for item in extracted_data:
            sentence = item["informations_cles"]
            if sentence in seen_sentences:
                seen_sentences[sentence] += 1  # Incrémente le compteur pour cette phrase
            else:
                seen_sentences[sentence] = 1
            
            # Mise à jour de la pertinence selon la fréquence de la phrase
            if seen_sentences[sentence] != 1:
                item["pertinence"] = "bon"  # Phrase répétée, pertinence bon

            # Ajouter la phrase à cleaned_data uniquement si elle n'a pas déjà été ajoutée
            if seen_sentences[sentence] == 1:
                cleaned_data.append(item)

        # Sauvegarde des données nettoyées
        for item in cleaned_data:
            save_message(item)


    def extract_data(self):
        """Extraction et analyse des données"""
        url = self.url_input.text().strip()  
        content_type = self.type_combo.currentText()  # Type de fichier sélectionné
        contexte_type = self.contexte_combo.currentText()  # Contexte choisi
        keywords = [kw.strip().lower() for kw in self.keywords_input.text().split(",") if kw.strip()]  # Liste des mots-clés

        # Vérification des champs obligatoires
        if not contexte_type or not keywords:
            QMessageBox.warning(self, "Attention", "Veuillez entrer un contexte et des mots-clés.")
            return
        
        if not url:
            QMessageBox.warning(self, "Attention", "Veuillez entrer une URL valide.")
            return

        if content_type in ["HTML", "PDF"]:
            
            text = self.extract_text(url, content_type)  # Extraction du texte via URL
            if not text:
                QMessageBox.warning(self, "Erreur", "Impossible d'extraire le texte de l'URL.")
                return
        else:
            # Pour TEXTE, on récupère le texte depuis QTextEdit
            text = self.text_area.toPlainText().strip()
            if not text:
                QMessageBox.warning(self, "Attention", "Veuillez saisir du texte avant de procéder.")
                return

        # Analyse du texte récupéré
        self.analyze_text(text, keywords, contexte_type, content_type, url)

        QMessageBox.information(self, "Succès", "Données enregistrées avec succès.")

        # Réinitialisation des champs
        self.url_input.clear() 
        self.keywords_input.clear()
        
        if content_type in ["TEXTE"]:
            self.text_area.clear()
        
        # Émettre le signal pour informer la fenêtre principale
        self.donnee_extrait.emit()
        self.accept()  # Fermer la fenêtre


    def clean_extracted_text(self, text):
        """Nettoie le texte extrait en supprimant les espaces et lignes inutiles."""
        text = re.sub(r"\n{2,}", "\n", text.strip())  # Réduit les lignes vides multiples à une seule
        return text

