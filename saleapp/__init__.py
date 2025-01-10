from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import cloudinary
from flask_login import LoginManager

app = Flask(__name__) #name of current module
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Abc12345@localhost/labsaledb?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['PAGE_SIZE'] = 4
app.config['COMMENT_SIZE'] = 20
app.secret_key = '08/12%sinh%nhat%cua%toi@kekeke'

cloudinary.config(
    cloud_name = 'dofw2gfy4',
    api_key = '878761217385499',
    api_secret = '11dpGM9VIDk_SGgNmiKAROvQXyE'
)
db = SQLAlchemy(app=app)

login = LoginManager(app)
