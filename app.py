from flask import Flask, render_template,session, redirect,request,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'mysecretkey'

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///data.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Notes(db.Model) :

    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(25),nullable=False)
    content = db.Column(db.String(255), nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str :
        return f" {self.id} : {self.title}"

class User(db.Model) :

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(255),nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self) -> str :
        return f" {self.id} : {self.name}"

@app.route('/notes', methods=['GET', 'POST'])
def notes() :

    if 'name' not in session:
        flash("Please sign up or log in first!", "warning")
        return redirect('/')
     
    if request.method == 'POST' :

        title = request.form.get('title')
        content = request.form.get('content')
        notes = Notes(title=title, content=content)
        db.session.add(notes)
        db.session.commit()
    
    allnotes = Notes.query.all()
    return render_template("notes.html", notes=allnotes)
    

@app.route('/', methods=['GET', 'POST'])
def signup() :
    if request.method == 'POST' :
        
        name = request.form.get("name")
        email = request.form.get("email")
        password= request.form.get("password")
        re_password = request.form.get("confirm_password")

        user = User(name = name, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        if re_password == password :
            return redirect('/notes')
        else :
            flash("Passwords do not match!", "danger")
            return render_template('signup.html')
    return render_template('signup.html')


@app.route("/delete/<int:id>")
def delete(id) :

    note = Notes.query.filter_by(id = id).first()
    db.session.delete(note)
    db.session.commit()

    return redirect('/notes')

@app.route("/update/<int:id>", methods=['GET', 'POST'])
def update(id) :

    note = Notes.query.filter_by(id=id).first()
    if request.method == 'POST' :
        note.title = request.form.get('title')
        note.content = request.form.get('content')
        
        db.session.commit()
        return redirect('/notes')

    return render_template('update.html', note=note)


@app.route("/login", methods=['GET', 'POST'])
def login():
    
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(name=username).first()

    if user and user.password == password :
        session['name'] = user.name
        return redirect('/notes')
    else:
        flash("Invalid credentials", "danger")

    return render_template("login.html")



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
