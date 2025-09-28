from pymongo import MongoClient
from django.conf import settings
client = MongoClient(settings.MONGO_URI)
db = client['wordgame']

users_col = db['users']
words_col = db['words']
games_col = db['games']
guesses_col = db['guesses']
