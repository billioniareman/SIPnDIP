from flask import Flask, render_template, redirect, flash, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from forms import InventoryItemForm, LoginForm, UpdateMenu, BillForm
import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask import send_file
import pandas as pd
app = Flask(__name__)
app.config['SECRET_KEY'] = 'flask@modeonsipndip'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sipndip.db'
app.config['SQLALCHEMY_MODIFICATION_TRACK'] = False
bp = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
