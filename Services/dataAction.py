# Importer la classe MongoDB depuis Services.mongoDb
from Services.mongoDb import MongoDB

# Créer une instance de MongoDB
mongo_db = MongoDB()

# Appeler directement la méthode save_message de MongoDB
def save_message(messages):
    # Enregistrement direct dans la base de données
    mongo_db.save_data(messages)
