import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from sqlalchemy import inspect, text

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

from app import models, routes


def ensure_upload_directory():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def ensure_medicine_schema():
    inspector = inspect(db.engine)
    if not inspector.has_table('medicine'):
        return

    column_names = {column['name'] for column in inspector.get_columns('medicine')}
    if 'image_filename' not in column_names:
        with db.engine.begin() as connection:
            connection.execute(text('ALTER TABLE medicine ADD COLUMN image_filename VARCHAR(255)'))

# Create tables and initial data
with app.app_context():
    db.create_all()
    ensure_upload_directory()
    ensure_medicine_schema()
    # Check if we have data, if not add some samples
    if not models.Medicine.query.first():
        samples = [
            models.Medicine(name='Panochem DSR', brand='TabChem Pharma', formula='Pantoprazole 40mg + Domperidone 30mg', dosage='Capsule', price=65.0, stock=150),
            models.Medicine(name='TabCof', brand='TabChem Pharma', formula='Diphenhydramine + Ammonium Chloride', dosage='100ml Syrup', price=85.0, stock=30),
            models.Medicine(name='AzithroTab 500', brand='TabChem Pharma', formula='Azithromycin 500mg', dosage='Tablet', price=120.0, stock=200),
            models.Medicine(name='ParaTab 650', brand='TabChem Pharma', formula='Paracetamol 650mg', dosage='Tablet', price=30.0, stock=500),
            models.Medicine(name='CetriTab', brand='TabChem Pharma', formula='Cetirizine 10mg', dosage='Tablet', price=25.0, stock=35),
            models.Medicine(name='VitiTab C', brand='TabChem Pharma', formula='Vitamin C 500mg', dosage='Chewable Tablet', price=45.0, stock=350),
            models.Medicine(name='IbuTab 400', brand='TabChem Pharma', formula='Ibuprofen 400mg', dosage='Tablet', price=50.0, stock=120),
            models.Medicine(name='OmeTab 20', brand='TabChem Pharma', formula='Omeprazole 20mg', dosage='Capsule', price=55.0, stock=80)
        ]
        db.session.add_all(samples)
        db.session.commit()
