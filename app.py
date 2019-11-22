import os
from flask import Flask, flash, redirect, render_template, request, url_for, make_response, escape, session, abort
import pymysql

app = Flask(__name__)
app.secret_key = os.urandom(16)
print(os.urandom(16))

conn = pymysql.connect(host='tsuts.tskoli.is', port=3306, user='2303023320', password='mypassword', database='2303023320_vef2_v7')


@app.route('/')
def index():
    '''
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        x = cur.fetchall()

        for i in x:
            print(i[2])
    '''

    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('user_name')
        psw = request.form.get('user_password')

        conn = pymysql.connect(host='tsuts.tskoli.is', port=3306, user='2303023320', password='mypassword', database='2303023320_vef2_v7')
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM 2303023320_vef2_v7.users where user_name=%s and user_password=%s",(user, psw))
        result = cur.fetchone()
        print(result)

        if result[0] == 1:
            cur.close()
            conn.close()
            flash('Innskráning tókst, ')
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            error = 'Innskráning mistókst - reyndu aftur'
        return render_template('index.tpl', error=error)


@app.route('/nyskra', methods=['GET', 'POST'])
def nyskra():
    error = None
    if request.method == "POST":
        userDetails = request.form
        user = userDetails['user_name']
        email = userDetails['user_email']
        password = userDetails['user_password']
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO 2303023320_vef2_v7.users(user_name, user_email, user_password) VALUES (%s, %s, %s )",
                (user, email, password))
            conn.commit()
            cur.close()
            flash('Nýskráning tókst og þú ert skráður í gagnagrunninni')
            # return redirect("/users")
            return redirect(url_for("users"))
        except pymysql.IntegrityError:
            error = "Notandi er þegar skráður með þessu nafni og/eða lykllorði"


@app.route('/users')
def users(): 
    cur = conn.cursor()
    resultValue = cur.execute("SELECT user_name FROM 2303023320_vef2_v7.users")
    if resultValue > 0:
        userDetails = cur.fetchall()
        return render_template('users.html', userDetails=userDetails)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        n = request.form['notandanafn']
        pw = request.form['password']
        nafn = request.form['nafn']

        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM users where user = %s", (n))
        p = cur.fetchone()
        if p[0] != 1:
            cur.execute("INSERT INTO users(user,pass,nafn) VALUES(%s,%s,%s)", (n, pw, nafn))
            conn.commit()
            cur.close()
            return render_template("nyr.html")

        else:
            return render_template("tekidfra.html")


@app.route('/utskra')
def utskra():
    listi = []
    session['logged_in'] = listi

    return render_template("utskraning.html")


@app.route('/vefur')
def vefur():
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    p = cur.fetchall()
    for i in p:
        if i[0] in session['logged_in']:
            nafn = i[2]

    return render_template("vefur.html", p=p, n=nafn)

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        try:
            cur = conn.cursor()
            resultValue = cur.execute("SELECT * FROM 2303023320_vef2_v7.users")  # * = allir dálkar
            if  resultValue > 0:
                userDetails = cur.fetchall()
                flash('velkomin')
                return render_template('admin.html',userDetails=userDetails)
        except pymysql.IntegrityError:
            error = 'Þú hefur ekki aðgang að þessari síðu'
        return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
