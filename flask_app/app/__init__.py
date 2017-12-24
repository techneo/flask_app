# main module to make this app work
from flask import Flask 

# app is a instance of Flask class 
#  __name__ in this case is app
app = Flask(__name__)

# get routes from the routes.py
from app import routes

