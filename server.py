from flask import Flask, render_template, request, redirect, session, flash
from flask_bcrypt import Bcrypt
import re # the "re" module will let us perform some regular expression operations
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
from mysqlconnection import connectToMySQL
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "008f1818-b9a9-4c67-bd0e-752c56cbaf74"


@app.route("/")
def index():
    return render_template("choose.html")

@app.route("/reg")
def register():
    return render_template("index.html")

@app.route("/log")
def login():
    return render_template("login.html")

@app.route("/process", methods=['POST'])
def processreg():
    session['email'] = request.form['email']
    session['first_name'] = request.form['first_name']
    session['last_name'] = request.form['last_name']
    session['password'] = request.form['password']
    session['password_confirm'] = request.form['password_confirm']
    if not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email Address!")
        return redirect('/reg')
    if len(request.form['first_name']) < 1:
        flash("please complete all required fields prior to submission")# just pass a string to flass function broski
        return redirect('/reg')
    if not request.form['first_name'].isalpha():
        flash("name fields will not except numbers")# just pass a string to flass function broski
        return redirect('/reg')
    if not request.form['last_name'].isalpha():
        flash("name fields will not except numbers")# just pass a string to flass function broski
        return redirect('/reg')
    if len(request.form['last_name']) < 1:
        flash("please complete all required fields prior to submission")# just pass a string to flass function broski
        return redirect('/reg')
    if len(request.form['password']) < 1:
        flash("please complete all required fields prior to submission")# just pass a string to flass function broski
        return redirect('/reg')
    if len(request.form['password_confirm']) < 1:
        flash("please complete all required fields prior to submission")# just pass a string to flass function broski
        return redirect('/reg')
    if len(request.form['password']) < 8:
        flash("password must be at least 8 characters")# just pass a string to flass function broski
        return redirect('/reg')
    if len(request.form['password_confirm']) < 8:
        flash("password must be at least 8 characters")# just pass a string to flass function broski
        return redirect('/reg')
    if request.form['password_confirm'] != request.form['password']:
        flash("password fields do not match")# just pass a string to flass function broski
        return redirect('/reg')
    else:
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        print(pw_hash)
        data = {
            'email': request.form['email'],
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'password_hash': pw_hash
        }
        mysql = connectToMySQL("login_registration")
        query = "SELECT email From users WHERE email = '"+request.form['email']+"'"
        print (query)
        new_email_id = mysql.query_db(query, data)
        print (new_email_id)
        if new_email_id:
            flash("Email already in database!")
            return redirect('/reg')

        mysql = connectToMySQL("login_registration")
        query = "INSERT INTO users(email, first_name, last_name, password, created_at, updated_at) VALUES(%(email)s, %(first_name)s, %(last_name)s, %(password_hash)s, NOW(), NOW());"
        new_email_id = mysql.query_db(query, data)
        session['email'] = request.form['email']
        session['userid'] = new_email_id
        flash("Thanks for submittng your info")# just pass a string to flass function broski
        return redirect("/result")


@app.route("/processlog", methods=['POST'])
def processlog():
    session['email'] = request.form['email']
    session['password'] = request.form['password']

    if not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email Address!")
        return redirect('/log')
    if len(request.form['password']) < 1:
        flash("please complete all required fields")# just pass a string to flass function broski
        return redirect('/log')
    if len(request.form['password']) < 8:
        flash("password is at least 8 characters")# just pass a string to flass function broski
        return redirect('/log')
    else:
        mysql = connectToMySQL("login_registration")
        query = "SELECT * From users WHERE email = %(email)s;"
        data = { 'email': request.form['email'] }
        print (query)
        result = mysql.query_db(query, data)
        print (result)
        if result:
            if bcrypt.check_password_hash(result[0]['password'], request.form['password']):
                session['userid'] = result[0]['id']
                session['first_name'] = result[0]['first_name']
                flash("logged in")# just pass a string to flass function broski
                return redirect("/main")
            else:
                flash("invalid credentials")
                return redirect('/log')
        else:
            flash("invalid email")
            return redirect('/log')
        

@app.route("/result", methods=['Get'])
def result():
    return render_template("index2.html")






@app.route("/main", methods=['Get'])
def main():
    if not session:
        return redirect('/')
    mysql = connectToMySQL("login_registration")
    data = { 'id': session['userid']}
    query = "SELECT id, first_name From users where id <> %(id)s;"
    users = mysql.query_db(query, data)

    mysql = connectToMySQL("login_registration")
    data = { 'id': session['userid']}
    query = "SELECT count(*) as count from messages where recipient_id = %(id)s;"
    messagetotal = mysql.query_db(query, data)

    mysql = connectToMySQL("login_registration")
    data = { 'id': session['userid']}
    query = "SELECT count(*) as count from messages where user_id = %(id)s;"
    totalmessage = mysql.query_db(query, data)

    mysql = connectToMySQL("login_registration")
    query = "SELECT messages.id, users.first_name, messages.content, messages.created_at From users left join messages on users.id = messages.user_id where messages.recipient_id = %(userid)s;"
    data = { 'userid': session['userid'] }
    messages = mysql.query_db(query, data)
    print(messages)

    return render_template("main.html", users=users, messagetotal=messagetotal[0]['count'], totalmessage=totalmessage[0]['count'], messages=messages)

@app.route('/sendmessage', methods= ['POST'])
def sendmessage():
    if len(request.form['content']) < 1:
        flash("messages must be greater than 1 character")# just pass a string to flass function broski
        return redirect('/main')
    else:
        mysql = connectToMySQL("login_registration")
        query = "INSERT into messages (content, user_id, recipient_id, created_at) values (%(content)s, %(user_id)s, %(recipient_id)s, NOW());"
        data = { 'content': request.form['content'],
                'user_id': session['userid'],
                'recipient_id': request.form['recipient_id']}
        print (query)
        sent = mysql.query_db(query, data)
        print (sent)
    return redirect('/main')

@app.route('/delete/<id>')
def delete(id):
    if 'userid' not in session:
        session.clear()
        return redirect('/') 
    data = { 'id': id }
    mysql = connectToMySQL('login_registration')
    query = 'DELETE FROM messages WHERE id = %(id)s'
    mysql.query_db(query, data)
    return redirect('/main')






@app.route("/logout", methods=['Get'])
def logout():
    session.clear()
    return redirect('/')



if __name__ == "__main__":
    app.run(debug=True)