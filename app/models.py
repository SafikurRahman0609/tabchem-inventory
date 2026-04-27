from app import db

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    formula = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Medicine {self.name}>'
