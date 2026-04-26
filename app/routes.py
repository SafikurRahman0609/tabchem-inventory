from flask import render_template, request, redirect, url_for, flash, session
from app import app, db
from app.models import Medicine

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
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
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/inventory')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    search_query = request.args.get('search', '')
    
    if search_query:
        medicines = Medicine.query.filter(Medicine.name.contains(search_query)).all()
    else:
        medicines = Medicine.query.all()
    
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
    return render_template('about.html')
