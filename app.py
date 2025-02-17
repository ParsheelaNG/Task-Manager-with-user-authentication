from flask import Flask,request,redirect,url_for,session,flash,render_template
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,IntegerField
from wtforms.validators import InputRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash
import re


app=Flask(__name__)
app.secret_key=("user")

#configure
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '2004'
app.config['MYSQL_DB'] = 'user'
mysql = MySQL(app)

class user:
    def __init__(self,Id,Username,Password):
        self.Id=Id
        self.Username=Username
        self.Password=Password
 
class signupform(FlaskForm):
    Id=IntegerField('Id')  
    Username=StringField('Username',validators=[InputRequired(),Length(min=3,max=20)])
    Password=PasswordField('Password',validators=[InputRequired(),Length(min=6,max=20)])
    MailID=StringField('MailID',validators=[InputRequired(),Length(min=10,max=30)])
    PhoneNumber=StringField('PhoneNumber',validators=[InputRequired(),Length(min=10,max=10)])
    Place=StringField('Place',validators=[InputRequired(),Length(min=5,max=15)])   
    Submit=SubmitField('Signup')


class loginform(FlaskForm):
    Username=StringField('Username',validators=[InputRequired(),Length(min=3,max=20)])
    Password=PasswordField('Password',validators=[InputRequired(),Length(min=6,max=20)])
    Submit=SubmitField('Login')

def passwordstrength(Password):
    strength = 0
    criteria = {
        "length": len(Password) >= 8,
        "uppercase": bool(re.search(r"[A-Z]", Password)),
        "lowercase": bool(re.search(r"[a-z]", Password)),
        "digit": bool(re.search(r"\d", Password)),
        "special_char": bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", Password))
    }
    strength = sum(criteria.values())
    if strength == 5:
        return "Very Strong"
    elif strength == 4:
        return "Strong"
    elif strength == 3:
        return "Moderate"
    elif strength == 2:
        return "Weak"
    else:
        return "Very Weak"
    
@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = signupform()
    if form.validate_on_submit():
        Username = form.Username.data
        Password = form.Password.data
        MailID=form.MailID.data
        PhoneNumber=form.PhoneNumber.data
        Place=form.Place.data
        if not passwordstrength(Password) :
            flash('Re-enter the password,it must contain uppercase,lowercase,digit and special characters','danger')
            return redirect(url_for('signup'))
        Hashed_password=generate_password_hash(Password)
        cur=mysql.connection.cursor()
        cur.execute("SELECT Id FROM signup WHERE Username = %s", (Username,))
        existing_user = cur.fetchone()
        if existing_user:
            cur.close()
            flash('Username already taken. Please choose a different one.', 'danger')
            return render_template("signup.html", form=form)
        cur.execute("INSERT INTO signup (Username, Password, MailID, PhoneNumber, Place) VALUES (%s, %s, %s, %s, %s)",(Username, Hashed_password, MailID, PhoneNumber, Place))
        mysql.connection.commit()
        session['Username'] = Username
        session['Email'] = MailID
        session['Mobile'] = PhoneNumber
        session['Place'] = Place
        cur.close()
        flash('Signup successful', 'success')
        return redirect(url_for('login'))
    return render_template("signup.html", form=form)


@app.route("/login", methods=['GET','POST'])
def login():
    form = loginform()
    if form.validate_on_submit():
        Username = form.Username.data
        Password = form.Password.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT Id, Username, Password, MailID, PhoneNumber, Place FROM signup WHERE Username = %s", (Username,))
        data = cur.fetchone() 
        cur.close()
        if data and check_password_hash(data[2], Password): 
            session['Username'] = data[1] 
            session['Email'] = data[3]  
            session['Mobile'] = data[4] 
            session['Place'] = data[5] 
            flash('Login Successful', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid Username or Password!', 'danger')
    return render_template("login.html", form=form)


@app.route("/")
def home():
    return render_template("navbar.html")

@app.route('/myprofile')
def profile():
    if 'Username' not in session:
        flash("Please Sign up or log in to access your profile.", "warning")
        return redirect(url_for('login'))
    user = {
    "username": session.get("Username", "Guest"),
    "email": session.get("Email", "Guest"),
    "mobile": session.get("Mobile", "Guest"),
    "place": session.get("Place", "Guest"),
}
    return render_template("profile.html", user=user)


@app.route("/Tasks",methods=["POST","GET"])
def tasks():
    if request.method == 'POST':
        Tname=request.form.get("taskname")
        Tdescription=request.form.get("taskdescription")
        Tdeadline=request.form.get("deadline")
        Tpriority=request.form.get("priority")
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO tasks(Taskname,Taskdescription,Deadline,Priority) VALUES (%s,%s,%s,%s)",(Tname,Tdescription,Tdeadline,Tpriority))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("display"))
    return render_template("index.html")

@app.route("/display")
def display():
    if 'Username' not in session:
        flash("Please log in first", "danger")
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tasks")
    data = cur.fetchall()
    cur.close()
    return render_template("table.html", data=data)


@app.route("/logout")
def logout():
    session.clear()  
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))



if __name__=="__main__":
    app.run(debug=True)
        
        






