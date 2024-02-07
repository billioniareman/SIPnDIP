from running import *
import soldtableclean
import xlsxwriter
from firebase_admin import auth
app.app_context().push()


class InventoryItem:
    def __init__(self, product_name, product_price, quantity, total_price, date):
        self.product_name = product_name
        self.product_price = product_price
        self.quantity = quantity
        self.total_price = total_price
        self.date = date

    def save_to_firestore(self):
        inventory_ref = firestore_db.collection('inventory_items')
        inventory_ref.add({
            'product_name': self.product_name,
            'product_price': self.product_price,
            'quantity': self.quantity,
            'total_price': self.total_price,
            'date': self.date,
        })


class SoldItem:
    def __init__(self, product_name, quantity, total_price, date, method):
        self.product_name = product_name
        self.quantity = quantity
        self.total_price = total_price
        self.date = date
        self.method = method

    def save_to_firestore(self):
        sales_ref = firestore_db.collection('sales')
        sales_ref.add({
            'product_name': self.product_name,
            'quantity': self.quantity,
            'total_price': self.total_price,
            'date': self.date,
            'method': self.method,
        })


class Menu:
    def __init__(self, product_category, product_name, product_rate):
        self.product_category = product_category
        self.product_name = product_name
        self.product_rate = product_rate

    def save_to_firestore(self):
        menu_ref = firestore_db.collection('menu')
        menu_ref.add({
            'product_category': self.product_category,
            'product_name': self.product_name,
            'product_rate': self.product_rate,
        })


@login_manager.user_loader
def load_user(user_id):
    try:
        user = auth.get_user(user_id)
        return user
    except auth.AuthError:
        return None

@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.username.data  # Assuming email is used for login
        password = form.password.data

        # Validate email address format
        if '@' not in email:
            flash('Invalid email address', 'error')
            return render_template('index.html', form=form)

        try:
            user = auth.get_user_by_email(email)
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        except auth.InvalidIdTokenError:
            flash('Invalid credentials', 'error')
        except auth.UserNotFoundError:
            flash('User not found', 'error')

    return render_template('index.html', form=form)

@app.route('/main')
@login_required
def index():
    return render_template('main.html')
@app.route('/add_stock', methods=['GET', 'POST'])
@login_required
def add_stock():
    form = InventoryItemForm()

    if form.validate_on_submit():
        product_name = form.product_name.data
        product_price = form.product_price.data
        quantity = form.quantity.data
        date = form.date.data
        total_price = product_price * quantity

        # Check if the item already exists in Firestore
        existing_item = firestore_db.collection('inventory_items').where('product_name', '==', product_name).get()

        if existing_item:
            # If the item exists, update it
            existing_item_data = existing_item[0].to_dict()
            existing_item_data['product_price'] += product_price
            existing_item_data['quantity'] += quantity
            existing_item_data['total_price'] += total_price
            existing_item_data['date'] = date
            firestore_db.collection('inventory_items').document(existing_item[0].id).set(existing_item_data)
        else:
            # If the item doesn't exist, create a new one
            new_item_data = {
                'product_name': product_name,
                'product_price': product_price,
                'quantity': quantity,
                'total_price': total_price,
                'date': date,
            }
            firestore_db.collection('inventory_items').add(new_item_data)
            flash('Stock added successfully!', 'success')

        return redirect(url_for('add_stock'))

    return render_template('addstock.html', form=form)


@app.route('/place_order', methods=['POST', 'GET'])
@login_required
def billing():
    inventory_ref = firestore_db.collection('menu')
    inventory = inventory_ref.get()

    if request.method == 'POST' or request.method == 'GET':
        category = request.form.get('category')
        products_selected = request.form.get('selectedProducts')
        rst = soldtableclean.Soldtableclean(products_selected).str_to_list()
        item = soldtableclean.Setdatabase(rst).list_of_item()
        quantity = soldtableclean.Setdatabase(rst).list_of_quantities()

        date = datetime.now()
        method = request.form.get('paymentMethod')

        quantity_str = ','.join(str(q) for q in quantity) if all(quantity) else '0'

        total_price = 0
        for i in item:
            menu_item = next((doc.to_dict() for doc in inventory if doc.id == i), None)
            if menu_item:
                total_price += menu_item['product_rate']

        print('category', category)
        if category is None:
            flash('Add items to proceed')
        else:
            billing_item = {
                'product_name': ','.join(item),
                'quantity': quantity_str,
                'total_price': total_price,
                'date': date,
                'method': method
            }
            firestore_db.collection('sales').add(billing_item)
            flash('Order placed successfully!', 'success')
            return redirect(url_for('order_confirmation'))

        return render_template('billing.html', inventory=inventory,
                               categories=set(item['product_category'] for item in inventory))
    else:
        return redirect('index')


@app.route('/order_confirmation')
def order_confirmation():
    return render_template('order_confirmation.html')


@app.route('/get_categories')
def get_categories():
    menu_ref = firestore_db.collection('menu')
    menu = menu_ref.get()
    categories = set(list(item.to_dict()['product_category'] for item in menu))
    return jsonify(categories)


@app.route('/get_products/<category>')
def get_products(category):
    menu_ref = firestore_db.collection('menu')
    menu = menu_ref.get()
    products = [item.to_dict()['product_name'] for item in menu if item.to_dict()['product_category'] == category]
    return jsonify(products)


@app.route('/admin')
@login_required
def admin():
    today = datetime.date.today()
    previous_two_days = [today - timedelta(days=i) for i in range(2, -1, -1)]
    formatted_dates = [date.strftime('%Y-%m-%d') for date in previous_two_days]
    chart_data = {
        'today_revenue': firestore_db.collection('sales').where('date', '==', today).get(),
        'labels': formatted_dates,
        'data': [
            firestore_db.collection('sales').where('date', '==', date).get() or 0
            for date in formatted_dates
        ],
    }
    online_data = firestore_db.collection('sales').where('date', '==', today).where('method', '==', 'online').get()

    cash_data = firestore_db.collection('sales').where('date', '==', today).where('method', '==', 'offline').get()

    pie_data = {
        'labels': ['Online', 'Cash'],
        'data': [online_data, cash_data],
    }
    return render_template('admin.html', chart_data=chart_data, pie_data=pie_data)


@app.route('/delete_item/<int:id>', methods=['POST'])
@login_required
def delete_item(id):
    # Assuming you have a 'menu' collection in Firestore for products
    menu_ref = firestore_db.collection('menu')
    menu_ref.document(str(id)).delete()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('update_menu'))


@app.route('/update_menu', methods=['POST', 'GET'])
@login_required
def update_menu():
    form = UpdateMenu()
    menu_ref = firestore_db.collection('menu')
    menu = menu_ref.get()
    if form.validate_on_submit():
        name = str.lower(form.Item.data)
        price = form.Price.data
        category = str.upper(form.Category.data)
        name = name.replace(' ', '-')
        updateproduct = menu_ref.where('product_category', '==', category).where('product_name', '==', name).get()
        if updateproduct:
            updateproduct_data = updateproduct[0].to_dict()
            updateproduct_data['product_rate'] = price
            menu_ref.document(updateproduct[0].id).set(updateproduct_data)
        else:
            new_item_data = {
                'product_category': str.upper(category),
                'product_name': str.lower(name),
                'product_rate': price,
            }
            firestore_db.collection('menu').add(new_item_data)
        flash('Menu updated successfully!', 'success')

    return render_template('updatemenu.html', menu=menu, form=form)


@app.route('/view_inventory')
@login_required
def view_inventory():
    # Assuming your Firestore collection is named 'inventory_items'
    inventory_ref = firestore_db.collection('inventory_items')

    # Get all documents from the 'inventory_items' collection
    inventory_query = inventory_ref.stream()

    # Convert Firestore documents to a list of dictionaries
    inventory = [item.to_dict() for item in inventory_query]

    return render_template('view_inventory.html', inventory=inventory)


@app.route('/download_menu_excel', methods=['GET'])
@login_required
def download_menu_excel():
    start_date_param = request.args.get('start_date')
    end_date_param = request.args.get('end_date')

    if not (start_date_param and end_date_param):
        return "Both start_date and end_date parameters are required.", 400

    sales_ref = firestore_db.collection('sales')
    sales = sales_ref.where('date', '>=', start_date_param).where('date', '<=', end_date_param).get()

    excel_file_path = f'sales' + str(datetime.date.today()) + '.xlsx'
    workbook = xlsxwriter.Workbook(excel_file_path)
    worksheet = workbook.add_worksheet()

    headers = ['ID', 'Product Name', 'Total Price', 'Quantity', 'Payment Mode', 'Date']
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header)

    for row_num, item in enumerate(sales, start=1):
        worksheet.write(row_num, 0, item.id)
        worksheet.write(row_num, 1, item.to_dict()['product_name'])
        worksheet.write(row_num, 2, item.to_dict()['total_price'])
        worksheet.write(row_num, 3, item.to_dict()['quantity'])
        worksheet.write(row_num, 4, item.to_dict()['method'])
        worksheet.write(row_num, 5, str(item.to_dict()['date']))

    workbook.close()

    return send_file(excel_file_path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
    app.app_context().pop()
