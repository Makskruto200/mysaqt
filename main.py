# This is a sample Python script.
import sqlite3
import os
import datetime

from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'static/images'
admin1_email = "adminforim1@gmail.com"
admin1_password = "Parov987#"
admin2_email = "pomoyforim16@gmail.com"
admin2_password = "mashin987)"


@app.route('/')
def index():
    list_rows = []
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts')
    rows = cursor.fetchall()
    for row in rows:
        cursor.execute('SELECT * FROM сomments WHERE id= ?', (row[0],))
        comments = cursor.fetchall()
        i = [row[0], row[1], row[2], row[3], row[4], comments]
        list_rows.append(i)
    conn.close()
    print(list_rows)
    return render_template('index.html', rows=list_rows)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = cursor.fetchone()

        if (username == admin1_email and password == admin1_password) or (
                username == admin2_email and password == admin1_password):
            session['username'] = username
            session['admin_is'] = True
            return redirect('/admin')
        elif user:
            session['username'] = username
            session['admin_is'] = False
            conn.close()
            print("УСПЕШНЫЙ ВХОД")
            return redirect('/dashboard')
        else:

            conn.close()
            error = "Неправельный логин или пароль"
            print("ОШИБКА ВХОДА")
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        # Проверка наличия пользователя в базе данных
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            conn.close()
            error = "Пользователь с таким именем уже зарегистрирован"
            return render_template('register.html', error=error)

        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        print("УСПЕШНАЯ РЕГЕСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ")

        return redirect('/login')
    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    user = session['username']
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()



    cursor.execute('SELECT * FROM сomments WHERE  username= ?', (user,))
    rows = cursor.fetchall()
    conn.close()

    if user:
        return render_template('dashboard.html', email=user,comment=rows)
    else:
        return "Пользователь не найден"


@app.route('/admin', methods=["GET"])
def admin():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()
    cursor.execute('SELECT * FROM posts')
    posts = cursor.fetchall()
    cursor.execute('SELECT * FROM сomments')
    comments = cursor.fetchall()

    conn.close()
    return render_template('admin.html', rows=rows, posts=posts, comments=comments)


@app.route('/delete_user/<int:post_id>')
def delete_user(post_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()

    return redirect("/admin")

@app.route('/delete_post/<int:post_id>')
def delete_post(post_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()

    return redirect("/admin")

@app.route('/delete_comment/<string:post_id>')
def delete_comment(post_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    post_id = post_id.replace('%', ' ')
    cursor.execute('DELETE FROM сomments WHERE data = ?', (post_id,))
    conn.commit()
    conn.close()

    return redirect("/admin")


@app.route('/post_create', methods=['GET', 'POST'])
def post_create():
    if request.method == 'POST':

        post_text = request.form['post_text']  # Получаем текст поста из формы
        file = request.files['file_to_upload']  # Получаем файл из формы
        user = session['username']
        data = datetime.datetime.now().replace(microsecond=0)
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        if file:  # Если файл был загружен
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))  # Сохраняем файл на сервере
            cursor.execute("INSERT INTO posts (username, text, file, data) VALUES (?, ?, ?, ?)",
                           (user, post_text, file.filename, data))
        else:
            cursor.execute("INSERT INTO posts (username, text, file, data) VALUES (?, ?, ?, ?)",
                           (user, post_text, "", data))

        # Подтверждаем операцию
        conn.commit()

        # Закрываем соединение
        conn.close()
        return redirect('/')
    return render_template('post_create.html')


@app.route('/create_comment/<int:post_id>', methods=['GET', 'POST'])
def create_comment(post_id):
    if request.method == 'POST':
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        text = request.form['comment']

        data = datetime.datetime.now().replace(microsecond=0)
        try:

            user = session['username']
        except:
            return redirect("/login")
        cursor.execute('INSERT INTO сomments (id,username, text,data) VALUES (?, ?,?,?)', (post_id, user, text, data))
        conn.commit()
        conn.close()
        return redirect("/dashboard")



app.run(port=8080)
