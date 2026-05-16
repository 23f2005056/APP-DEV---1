from flask import Flask
from models import *


app=None #initially none


def init_app():
    influ=Flask(__name__) #object of Flask
    influ.debug=True
    influ.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///influ.sqlite3"
    influ.app_context().push()
    influ.config["SECRET_KEY"]="SECRET_KEY" #Direct access app by other modules(db, authentication)
    db.init_app(influ) #object.method(<parameter>)
    print("INFLUENCER ENGAGEMENT")
    return influ

app=init_app()
from controllers import *

if __name__=="__main__":
    with app.app_context():
        db.create_all()
    app.run()