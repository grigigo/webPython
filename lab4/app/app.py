from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from my_sql_db import MySQL

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к данной странице необходимо пройти процедуру аутентификации'
login_manager.login_message_category = 'warning'

app = Flask(__name__)
application = app

app.config.from_pyfile('config.py')

login_manager.init_app(app)

mysql = MySQL(app)

class User(UserMixin):
    def __init__(self, user_id, login, password):
        super().__init__()
        self.id = user_id  # обязательно id
        self.login = login
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    with mysql.connection.cursor(named_tuple=True) as cursor:
        cursor.execute('SELECT * FROM users WHERE id=%s;', (user_id,))
        db_user = cursor.fetchone()  # .fetchmany()
    if db_user:
        return User(user_id=db_user.id, login=db_user.login)
    return None


def get_users():
    return [{'user_id': 1, 'login': 'user', 'password': 'qwerty'}]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        with mysql.connection.cursor(named_tuple=True) as cursor:
            cursor.execute('SELECT * FROM users WHERE login=%s AND password_hash=SHA2(%s, 256);', (login, password))
            db_user = cursor.fetchone()
        if db_user:
            login_user(User(user_id=db_user.id, login=db_user.login), remember=remember)
            flash('Вы успешно прошли процедуру аутентификации!', 'success')
            return redirect(url_for('index'))
        flash('Были введены неверные логин и/или пароль!', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


