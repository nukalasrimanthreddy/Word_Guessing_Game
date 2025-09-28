from gameapp.mongo import words_col

words = [
    "APPLE", "BANJO", "CRISP", "DRINK", "EAGLE",
    "FAITH", "GLASS", "HONEY", "INDEX", "JOKER",
    "KNIFE", "LEMON", "MOUSE", "NURSE", "OPERA",
    "PLANT", "QUEST", "ROBIN", "SWEET", "TRAIN"
]

for w in words:
    if not words_col.find_one({"word": w}):
        words_col.insert_one({"word": w})

print("20 words seeded successfully!")
