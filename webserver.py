from flask import Flask, render_template, request, session, g, redirect, url_for,abort, render_template, flash, Blueprint
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import login_required, current_user, login_user, LoginManager, UserMixin, logout_user

app = Flask(__name__)
app.config["SECRET_KEY"] = "ThisSecret"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    password = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, default=datetime.now)

class Voted(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=True)
    message = db.Column(db.String(500))
    user = db.Column(db.String(50), unique=False)



@login_manager.user_loader
def get_user(ident):
  return User.query.get(int(ident))

@app.route("/voted/<title>/<message>")
def voted(title, message):
    vote = Voted(title=title, message=message, user=current_user.name)
    db.session.add(vote)
    db.session.commit()



@app.route("/authorize/<name>/<password>")
def authorization(name, password):

    try:
        if (User.query.filter_by(name=name).first()):
            TargetUser = User.query.filter_by(name=name).first()
            if(TargetUser.name == name and TargetUser.password == password):
                login_user(TargetUser)
                db.session.commit()

                return redirect("/")
    except:
        print("")
    return redirect("/authorize")

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/latest/votes")
def votes():
    votes = Voted.query.order_by(Voted.id).all()
    return render_template("last_votes.html", votes=votes)

@app.route("/create/user", methods=["POST"])
def create_new_user():
    if request.method == "POST":
        req = request.form
        username = req.get("username")
        password = request.form["password"]

        return redirect(f"/create/user/{ username }/{ password }")
        return redirect(f"/authorize/{ username }/{ password }")
    return redirect(f"/")


@app.route("/create/user/<name>/<password>")
def new_user(name, password):
    user = User(name=name, password=password)
    db.session.add(user)
    db.session.commit()
    return redirect(f"/authorize")


@app.route("/authorize", methods=["GET", "POST"])
def authorize():
    if request.method == "POST":
        req = request.form
        username = req.get("username")
        password = request.form["password"]

        return redirect(f"/authorize/{ username }/{ password }")
    return render_template("authorize.html")

@app.route("/unauthorize/<name>/<id>", methods=["GET"])
def unauthorize(name, id):
    user = User.query.filter_by(name=name).first()
    logout_user()
    return redirect(f"/")


@app.route('/user/<name>')
def get_user(name):
    user = User.query.filter_by(name=name).first()
    return f'<h1>The user has id: { user.id }</h1>'

@app.route('/database')
def get_users():
    users = User.query.order_by(User.name).all()
    return render_template("users.html", users=users)


@app.route('/delete/<id>')
def delete_user(id):
    user = User.query.filter_by(id=id).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(f"/database")

if __name__ == '__main__':
    app.run(port=5000, debug=True, host='192.168.1.65', use_reloader=True)
