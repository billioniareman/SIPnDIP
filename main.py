from sqlalchemy import func
from running import *
import soldtableclean

app.app_context().push()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)


class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100))
    product_price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    total_price = db.Column(db.Float)
    date = db.Column(db.Date)

    def __init__(self, product_name, product_price, quantity, total_price, date):
        self.product_name = product_name
        self.product_price = product_price
        self.quantity = quantity
        self.total_price = total_price
        self.date = date


class SoldItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100))
    quantity = db.Column(db.String(100))
    total_price = db.Column(db.Float)
    method = db.Column(db.String(100))
    date = db.Column(db.Date)

    def __init__(self, product_name, quantity, total_price, date, method):
        self.product_name = product_name
        self.quantity = quantity
        self.total_price = total_price
        self.date = date
        self.method = method


class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100))
    product_rate = db.Column(db.Integer)

    def __init__(self, product_name, product_rate):
        self.product_name = product_name
        self.product_rate = product_rate



# app.py

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            login_user(user)
            return redirect(    url_for('index'))
        else:
            return 'Invalid credentials'

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'Logged out successfully'

@app.route('/main')
@login_required
def index():
    return render_template('index.html')


@app.route('/add_stock', methods=['GET', 'POST'])
@login_required
def add_stock():
    form = InventoryItemForm()
    inventory = InventoryItem.query.all()

    if form.validate_on_submit():
        product_name = form.product_name.data
        product_price = form.product_price.data
        quantity = form.quantity.data
        date = form.date.data
        total_price = product_price * quantity

        product_found = False

        for record in inventory:
            if record.product_name == product_name and record.date == date:
                # Update existing record
                record.product_price += product_price
                record.total_price += total_price
                record.date = date
                record.quantity += quantity
                db.session.commit()
                product_found = True
                break

        if not product_found:
            new_item = InventoryItem(
                product_name=product_name,
                product_price=product_price,
                quantity=quantity,
                total_price=total_price,
                date=date
            )
            db.session.add(new_item)
            db.session.commit()

        return redirect(url_for('add_stock'))
    return render_template('addstock.html', form=form, inventory=inventory)


@app.route('/place_order', methods=['POST', 'GET'])
@login_required
def billing():
    form = BillForm()
    if request.method == 'POST' or request.method == 'GET':
        products_selected = request.form.get('selectedProducts')
        rst = soldtableclean.Soldtableclean(products_selected).str_to_list()
        item = soldtableclean.Setdatabase(rst).list_of_item()
        quantity = soldtableclean.Setdatabase(rst).list_of_quantities()

        date = datetime.datetime.today()
        method = request.form.get('paymentMethod')

        quantity_str = ','.join(str(q) for q in quantity) if all(quantity) else '0'

        total_price = 0
        for i in item:
            menu_item = Menu.query.filter_by(product_name=i).first()
            if menu_item:
                total_price += menu_item.product_rate
        if ' '.join(item) is None or ' '.join(item) == 'None':
            flash('Add items to proceed')
        else:
            billing_item = SoldItem(product_name=' '.join(item), quantity=quantity_str, total_price=total_price,
                                    date=date, method=method)
            db.session.add(billing_item)
            db.session.commit()

        return render_template('billing.html', inventory=Menu.query.all(), form=form)
    else:
        return redirect(url_for('index'))


# ===========================================================================================================
@app.route('/admin')
@login_required
def admin():
    chart_data = {
        'today_revenue': SoldItem.query.filter_by(date=datetime.date.today()).with_entities(
            func.sum(SoldItem.total_price)).scalar() or 0,

        'labels': ['31/12/2023', '01/01/2024', '02/02/2024'],
        'data': [
            SoldItem.query.filter_by(date='2023-12-31').with_entities(func.sum(SoldItem.total_price)).scalar() or 0,
            SoldItem.query.filter_by(date='2024-01-01').with_entities(func.sum(SoldItem.total_price)).scalar() or 0,
            SoldItem.query.filter_by(date='2024-01-02').with_entities(func.sum(SoldItem.total_price)).scalar() or 0],
    }
    pie_data = {
        'labels': ['Category A', 'Category B', 'Category C', 'Category D', 'Category E'],
        'data': [30, 15, 25, 20, 10],
    }

    return render_template('admin.html', chart_data=chart_data, pie_data=pie_data)


@app.route('/update_menu', methods=['POST', 'GET'])
@login_required
def update_menu():
    form = UpdateMenu()
    menu = Menu.query.all()
    if form.validate_on_submit():
        name = form.Item.data
        price = form.Price.data
        updateproduct = Menu.query.filter_by(product_name=name).first()
        if updateproduct:
            updateproduct.product_rate = price
            flash('Product updated successfully!', 'success')
        else:
            new_item = Menu(product_name=name, product_rate=price)
            db.session.add(new_item)
            flash(f'Product with name {name} is not updated', 'danger')
        db.session.commit()
    return render_template('updatemenu.html', menu=menu, form=form)


@app.route('/view_inventory')
@login_required
def view_inventory():
    inventory = InventoryItem.query.all()
    return render_template('view_inventory.html', inventory=inventory)


if __name__ == '__main__':
    app.run(debug=True)
    app.app_context().pop()
