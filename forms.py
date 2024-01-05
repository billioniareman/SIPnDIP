from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField, DateField
from wtforms.validators import DataRequired, NumberRange


class InventoryItemForm(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired()])
    product_price = FloatField('Product Price', validators=[DataRequired(), NumberRange(min=0.01)])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    total_price = FloatField('Total Price', render_kw={'readonly': True})


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class BillForm(FlaskForm):
    submit = SubmitField('Submit')


class UpdateMenu(FlaskForm):
    Item = StringField('Item Name', validators=[DataRequired()])
    Category = StringField('Category', validators=[DataRequired()])
    Price = FloatField('Price', validators=[DataRequired(), NumberRange()])
    submit = SubmitField('Submit')
