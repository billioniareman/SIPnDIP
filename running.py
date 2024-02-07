from flask import Flask, render_template, redirect, flash, url_for, request, jsonify
from flask_bootstrap import Bootstrap
from forms import LoginForm, InventoryItemForm, UpdateMenu
import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask import send_file
import firebase_admin
from firebase_admin import credentials, auth
from firebase import Firebase
cred = credentials.Certificate("sipndip-2024-firebase-adminsdk-3uqa7-cb25a9dfa4.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sipndip-2024-default-rtdb.firebaseio.com/',  # Replace with your database URL
})
firebaseConfig = {
  apiKey: "AIzaSyB8K9kXGgaCAQEN8WvVIwlNmW9s4EnPTo8",
  authDomain: "sipndip-2024.firebaseapp.com",
  databaseURL: "https://sipndip-2024-default-rtdb.firebaseio.com",
  projectId: "sipndip-2024",
  storageBucket: "sipndip-2024.appspot.com",
  messagingSenderId: "541728222571",
  appId: "1:541728222571:web:cc30ccf6c23d852eb6702e",
  measurementId: "G-6CM1F3PM2H"
}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'flask@modeonsipndip'
bp = Bootstrap(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
firebasecfg=Firebase(firebaseConfig)