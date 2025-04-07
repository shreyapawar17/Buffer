from app import db

class DistressWord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(50), nullable=False)

    def __init__(self, word):
        self.word = word
