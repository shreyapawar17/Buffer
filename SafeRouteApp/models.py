from app import db  # Import db from app.py

# Define database models
class DistressWord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(50), unique=True, nullable=False)

class EmergencyContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    location = db.Column(db.String(200), nullable=False)

# Ensure database tables are created
if __name__ == "__main__":
    db.create_all()
    print("Database tables created successfully!")


