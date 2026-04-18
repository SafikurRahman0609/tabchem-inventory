from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
# For sessions and flash messages, we need a secret key
app.config['SECRET_KEY'] = 'tabchem-pharma-secret-key'

# Configure SQLite DB
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'inventory.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    formula = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Medicine {self.name}>'

# Create tables and initial data
with app.app_context():
    db.create_all()
    # Check if we have data, if not add some samples
    if not Medicine.query.first():
        samples = [
            Medicine(name='Panochem DSR', brand='TabChem Pharma', formula='Pantoprazole 40mg + Domperidone 30mg', dosage='Capsule', price=65.0, stock=150),
            Medicine(name='TabCof', brand='TabChem Pharma', formula='Diphenhydramine + Ammonium Chloride', dosage='100ml Syrup', price=85.0, stock=30),
            Medicine(name='AzithroTab 500', brand='TabChem Pharma', formula='Azithromycin 500mg', dosage='Tablet', price=120.0, stock=200),
            Medicine(name='ParaTab 650', brand='TabChem Pharma', formula='Paracetamol 650mg', dosage='Tablet', price=30.0, stock=500),
            Medicine(name='CetriTab', brand='TabChem Pharma', formula='Cetirizine 10mg', dosage='Tablet', price=25.0, stock=35),
            Medicine(name='VitiTab C', brand='TabChem Pharma', formula='Vitamin C 500mg', dosage='Chewable Tablet', price=45.0, stock=350),
            Medicine(name='IbuTab 400', brand='TabChem Pharma', formula='Ibuprofen 400mg', dosage='Tablet', price=50.0, stock=120),
            Medicine(name='OmeTab 20', brand='TabChem Pharma', formula='Omeprazole 20mg', dosage='Capsule', price=55.0, stock=80)
        ]
        db.session.add_all(samples)
        db.session.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Simple hardcoded authentication for the class presentation demo
        if username.lower() == 'emp1' and password == 'laiba@1':
            session['logged_in'] = True
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/')
def home():
    # Protect Route
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/inventory')
def dashboard():
    # Protect Route
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    # Provide search functionality
    search_query = request.args.get('search', '')
    
    if search_query:
        medicines = Medicine.query.filter(Medicine.name.contains(search_query)).all()
    else:
        medicines = Medicine.query.all()
    
    # Calculate statistics based on all medicines to keep summaries accurate even when filtering
    all_medicines = Medicine.query.all()
    total_medicines = len(all_medicines)
    total_units = sum(med.stock for med in all_medicines)
    total_value = sum(med.price * med.stock for med in all_medicines)
    low_stock = len([med for med in all_medicines if med.stock <= 40])
    
    return render_template('dashboard.html', 
                           medicines=medicines, 
                           total_medicines=total_medicines,
                           total_units=total_units,
                           total_value=total_value,
                           low_stock=low_stock,
                           search_query=search_query)

@app.route('/add', methods=['POST'])
def add_medicine():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        brand = request.form['brand']
        formula = request.form['formula']
        dosage = request.form['dosage']
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        
        new_med = Medicine(name=name, brand=brand, formula=formula, dosage=dosage, price=price, stock=stock)
        db.session.add(new_med)
        db.session.commit()
        
        flash('Medicine added successfully!', 'success')
        return redirect(url_for('dashboard'))

@app.route('/update/<int:id>', methods=['POST'])
def update_medicine(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    med = Medicine.query.get_or_404(id)
    if request.method == 'POST':
        med.name = request.form['name']
        med.brand = request.form['brand']
        med.formula = request.form['formula']
        med.dosage = request.form['dosage']
        med.price = float(request.form['price'])
        med.stock = int(request.form['stock'])
        
        db.session.commit()
        flash('Medicine updated successfully!', 'success')
        return redirect(url_for('dashboard'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_medicine(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    med = Medicine.query.get_or_404(id)
    db.session.delete(med)
    db.session.commit()
    flash('Medicine deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/about')
def about():
    # Demonstrates Jinja multi-page routing
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
