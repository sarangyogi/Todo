from datetime import datetime
from flask import Flask, flash, redirect,render_template,request, url_for
from flask_login import LoginManager, UserMixin,login_user,logout_user,login_manager,current_user,login_required;
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash;

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
app.config["SECRET_KEY"]="mysupersecret"
db=SQLAlchemy(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(100),nullable=False)
    password=db.Column(db.String(500),nullable=False)
    CreatedAt=db.Column(db.DateTime,default=datetime.utcnow())
    todos=db.relationship('Todo')

class Todo(db.Model):
    sno=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(100),nullable=False)
    desc=db.Column(db.String(500),nullable=False)
    CreatedAt=db.Column(db.DateTime,default=datetime.utcnow())
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))

@app.route('/',methods=["POST","GET"])
@login_required
def home_page():
    if(request.method=="POST"):
        title=request.form["title"]
        description=request.form["desc"]
        user_id=current_user.id
        data=Todo(title=title,desc=description,user_id=user_id)
        db.session.add(data)
        db.session.commit()
    return render_template('index.html',user=current_user)

@app.route('/delete/<int:sno>')
def deleteItem(sno):
    data=Todo.query.filter_by(sno=sno).first()
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for('.home_page'))

@ app.route('/update/<int:sno>',methods=["POST","GET"])
def updateTodo(sno):
    if(request.method=="POST"):
        title=request.form["title"]
        description= request.form["desc"]
        data=Todo.query.filter_by(sno=sno).first()
        data.title=title
        data.desc=description
        db.session.add(data)
        db.session.commit()
        return redirect(url_for('.home_page'))
    data=Todo.query.filter_by(sno=sno).first()
    return render_template('update.html',todo=data,user=current_user)
@app.route('/about')
def about():
    return render_template('about.html',user=current_user)

@app.route('/login',methods=["POST","GET"])
def login():
    if(request.method=="POST"):
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()
        if(user):
            if(check_password_hash(user.password,password)):
                login_user(user,remember=True)
                flash("Successfully Logged In!",category="success")
                return redirect(url_for('.home_page'))
            else:
                flash("Wrong Credentials!",category="error")
        else:
            flash("You've to register first!",category="error")
    return render_template('login.html')

@app.route('/register',methods=["POST","GET"])
def register():
    if(request.method=='POST'):
        name=request.form.get('name')
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()
        if(user):
            flash("User already exists, You may login")
        elif(len(password)<3):
            flash("Password length must be greater than 3",category="error")
        else:
            flash("Successfully registered!",category="success")
            data=User(name=name,email=email,password=generate_password_hash(password,method="sha256"))
            print(data)
            db.session.add(data)
            db.session.commit()
            return redirect(url_for('.login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('.login'))

if __name__=="__main__":
    app.run(debug=True)
