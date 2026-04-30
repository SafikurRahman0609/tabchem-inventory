import os
from uuid import uuid4

from flask import current_app, flash, redirect, render_template, request, session, url_for
from app import app, db
from app.models import Medicine
from sqlalchemy import String, cast, or_
from werkzeug.utils import secure_filename

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
DEFAULT_SORT_OPTION = 'newest'
SORT_OPTIONS = {
    'newest': Medicine.id.desc(),
    'name_asc': Medicine.name.asc(),
    'price_asc': Medicine.price.asc(),
    'price_desc': Medicine.price.desc(),
    'stock_asc': Medicine.stock.asc(),
    'stock_desc': Medicine.stock.desc(),
}


def _apply_medicine_form(medicine):
    medicine.name = request.form['name'].strip()
    medicine.brand = request.form['brand'].strip()
    medicine.formula = request.form['formula'].strip()
    medicine.dosage = request.form['dosage'].strip()
    medicine.price = float(request.form['price'])
    medicine.stock = int(request.form['stock'])


def _allowed_image(filename):
    if '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_IMAGE_EXTENSIONS


def _delete_image(relative_path):
    if not relative_path:
        return

    image_path = os.path.join(current_app.static_folder, relative_path)
    if os.path.isfile(image_path):
        os.remove(image_path)


def _save_uploaded_image(file_storage, current_filename=None):
    cleaned_name = secure_filename(file_storage.filename)
    if not cleaned_name or not _allowed_image(cleaned_name):
        raise ValueError('Please upload a PNG, JPG, JPEG, GIF, or WEBP image.')

    extension = os.path.splitext(cleaned_name)[1].lower()
    stored_name = f'{uuid4().hex}{extension}'
    relative_path = f"{current_app.config['MEDICINE_IMAGE_SUBDIR']}/{stored_name}"
    absolute_path = os.path.join(current_app.static_folder, relative_path)

    os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
    file_storage.save(absolute_path)

    if current_filename and current_filename != relative_path:
        _delete_image(current_filename)

    return relative_path


def _build_inventory_search_filters(search_query):
    search_pattern = f'%{search_query}%'
    searchable_columns = [
        Medicine.name,
        Medicine.brand,
        Medicine.formula,
        Medicine.dosage,
        cast(Medicine.id, String),
        cast(Medicine.stock, String),
        cast(Medicine.price, String),
    ]
    return [column.ilike(search_pattern) for column in searchable_columns]

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

    search_query = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '').strip()
    sort_option = request.args.get('sort', DEFAULT_SORT_OPTION).strip() or DEFAULT_SORT_OPTION
    selected_sort = sort_option if sort_option in SORT_OPTIONS else DEFAULT_SORT_OPTION

    medicines_query = Medicine.query

    if search_query:
        medicines_query = medicines_query.filter(or_(*_build_inventory_search_filters(search_query)))

    if category_filter:
        medicines_query = medicines_query.filter(Medicine.dosage == category_filter)

    medicines = medicines_query.order_by(SORT_OPTIONS[selected_sort]).all()

    dosage_categories = [
        dosage for (dosage,) in db.session.query(Medicine.dosage)
        .distinct()
        .order_by(Medicine.dosage.asc())
        .all()
        if dosage
    ]

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
                           search_query=search_query,
                           dosage_categories=dosage_categories,
                           selected_category=category_filter,
                           selected_sort=selected_sort)

@app.route('/add', methods=['POST'])
def add_medicine():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_med = Medicine()

        try:
            _apply_medicine_form(new_med)
            image_file = request.files.get('image')
            if image_file and image_file.filename:
                new_med.image_filename = _save_uploaded_image(image_file)
        except ValueError as exc:
            flash(str(exc), 'danger')
            return redirect(url_for('dashboard'))

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
        try:
            _apply_medicine_form(med)
            image_file = request.files.get('image')
            if image_file and image_file.filename:
                med.image_filename = _save_uploaded_image(image_file, current_filename=med.image_filename)
        except ValueError as exc:
            flash(str(exc), 'danger')
            return redirect(request.referrer or url_for('dashboard'))

        db.session.commit()
        flash('Medicine updated successfully!', 'success')
        return redirect(request.referrer or url_for('dashboard'))


@app.route('/medicine/<int:id>/edit', methods=['GET', 'POST'])
def edit_medicine(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    medicine = Medicine.query.get_or_404(id)

    if request.method == 'POST':
        try:
            _apply_medicine_form(medicine)
            image_file = request.files.get('image')
            if image_file and image_file.filename:
                medicine.image_filename = _save_uploaded_image(image_file, current_filename=medicine.image_filename)
        except ValueError as exc:
            flash(str(exc), 'danger')
            return redirect(url_for('edit_medicine', id=id))

        db.session.commit()
        flash('Medicine updated successfully!', 'success')
        return redirect(url_for('edit_medicine', id=id))

    return render_template('edit_medicine.html', medicine=medicine)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_medicine(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    med = Medicine.query.get_or_404(id)
    _delete_image(med.image_filename)
    db.session.delete(med)
    db.session.commit()
    flash('Medicine deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/about')
def about():
    return render_template('about.html')


@app.errorhandler(413)
def request_entity_too_large(_error):
    flash('Please upload an image smaller than 5MB.', 'danger')
    return redirect(request.referrer or url_for('dashboard'))
