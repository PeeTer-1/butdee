from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

# สร้างตารางสินค้า
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=True)

# สร้างฐานข้อมูล
with app.app_context():
    db.create_all()

# หน้าหลัก แสดงรายการสินค้า
@app.route('/')
@app.route('/products', methods=['GET'])
def product_list():
    search_query = request.args.get('search', '')
    if search_query:
        products = Product.query.filter(Product.product_name.contains(search_query)).all()
    else:
        products = Product.query.all()
    return render_template('product_list.html', products=products, search_query=search_query)

# เพิ่มสินค้า
@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_name = request.form['product_name']
        price = float(request.form['price'])
        description = request.form['description']
        
        files = request.files.getlist('images')
        filenames = []
        for file in files:
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                filenames.append(filename)

        new_product = Product(product_name=product_name, price=price, description=description, images=",".join(filenames))
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('product_list'))

    return render_template('add_product.html')

# แก้ไขสินค้า
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get(id)
    if request.method == 'POST':
        product.product_name = request.form['product_name']
        product.price = float(request.form['price'])
        product.description = request.form['description']
        
        file = request.files['image']
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            product.image = filename

        db.session.commit()
        return redirect(url_for('product_list'))

    return render_template('edit_product.html', product=product)

# ลบสินค้า
@app.route('/delete/<int:id>', methods=['POST'])
def delete_product(id):
    product = Product.query.get(id)
    if product:
        db.session.delete(product)
        db.session.commit()
    return redirect(url_for('product_list'))

if __name__ == '__main__':
    app.run(debug=True)
