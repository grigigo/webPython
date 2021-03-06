from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from my_sql_db import MySQL
import mysql.connector as connector
from test import pass_test, login_test

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к данной странице необходимо пройти процедуру аутентификации.'
login_manager.login_message_category = 'warning'

app = Flask(__name__)
# application = app

app.config.from_pyfile('config.py')

login_manager.init_app(app)

mysql = MySQL(app)

CREATE_PARAMS = ['login', 'password', 'first_name', 'last_name', 'middle_name', 'role_id']
UPDATE_PARAMS = ['first_name', 'last_name', 'middle_name', 'role_id']

def request_params(params_list):
    params = {}
    for param_name in params_list:
        params[param_name] = request.form.get(param_name) or None
    return params

def load_roles():
    with mysql.connection.cursor(named_tuple=True) as cursor:
        cursor.execute('SELECT * FROM roles;')
        roles = cursor.fetchall()
    return roles

class User(UserMixin):
    def __init__(self, user_id, login):
        # super().__init__()
        self.id = user_id
        self.login = login

@login_manager.user_loader
def load_user(user_id):
    with mysql.connection.cursor(named_tuple=True) as cursor:
        cursor.execute('SELECT * FROM users WHERE id=%s;', (user_id,))
        db_user = cursor.fetchone()
    if db_user:
        return User(user_id=db_user.id, login=db_user.login)
    return None

def get_users():
    return [{'user_id': 1, 'login': 'user', 'password': 'qwerty'}]

@app.route('/')
def index():  # put application's code here
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == 'on'

        with mysql.connection.cursor(named_tuple=True) as cursor:
            cursor.execute('SELECT * FROM users WHERE login=%s AND password_hash=SHA2(%s, 256);', (login, password))
            #sqlinject
            #cursor.execute(f"SELECT * FROM users WHERE login='{login}' AND password_hash=SHA2('{password}', 256);")
            db_user = cursor.fetchone()

        if db_user:
            login_user(User(user_id=db_user.id, login=db_user.login), remember=remember_me)
            flash('Вы успешно прошли процедуру аутентификации.', 'success')
            return redirect(url_for('index'))
        flash('Были введены неверные логин и/или пароль.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/users')
def users():
    with mysql.connection.cursor(named_tuple=True) as cursor:
        cursor.execute('SELECT users.*, roles.name AS role_name FROM users LEFT OUTER JOIN roles ON users.role_id = roles.id;')
        users = cursor.fetchall()
    return render_template('users/index.html', users=users)

@app.route('/users/new')
@login_required
def new():
    return render_template('users/new.html', user={}, roles=load_roles())


@app.route('/users/create', methods=['POST'])
@login_required
def create():
    params = request_params(CREATE_PARAMS)
    pass_err = pass_test(params['password'])
    login_err = login_test(params['login'])
    is_first = False if params['first_name'] else True
    is_last = False if params['last_name'] else True

    if not (pass_err or login_err) and is_first and is_last:
        with mysql.connection.cursor(named_tuple=True) as cursor:
            try:
                cursor.execute('''
                            INSERT INTO users (login, password_hash, first_name, last_name, middle_name, role_id)
                            VALUES (%(login)s, SHA2(%(password)s, 256), %(first_name)s, %(last_name)s, %(middle_name)s, %(role_id)s);
                            ''', params)
                mysql.connection.commit()
            except connector.Error:
                mysql.connection.rollback()
                flash('Введены некоректные данные. Ошибка сохранения', 'danger')
                return render_template('users/new.html', user=params, roles=load_roles())

        flash(f"Пользователь {params.get('login')} был успешно создан!", 'success')
        return redirect(url_for('users'))
    else:
        return render_template('users/new.html', user=params, roles=load_roles(), pass_err=pass_err,
                               login_err=login_err, first_err=is_first, last_err=is_last)

@app.route('/users/<int:user_id>')
@login_required
def show(user_id):
    with mysql.connection.cursor(named_tuple=True) as cursor:
        cursor.execute('SELECT * FROM users WHERE id=%s;', (user_id,))
        user = cursor.fetchone()
    return render_template('users/show.html', user=user)

@app.route('/users/<int:user_id>/edit')
@login_required
def edit(user_id):
    with mysql.connection.cursor(named_tuple=True) as cursor:
        cursor.execute('SELECT * FROM users WHERE id=%s;', (user_id,))
        user = cursor.fetchone()
    return render_template('users/edit.html', user=user, roles=load_roles())


@app.route('/users/<int:user_id>/update', methods=['POST'])
@login_required
def update(user_id):
    params = request_params(UPDATE_PARAMS)
    params['id'] = user_id
    with mysql.connection.cursor(named_tuple=True) as cursor:
        try:
            cursor.execute('''
                            UPDATE users SET first_name=%(first_name)s, last_name=%(last_name)s, middle_name=%(middle_name)s, role_id=%(role_id)s
                            WHERE id=%(id)s;
                            ''', params)
            mysql.connection.commit()
        except connector.Error:
            mysql.connection.rollback()
            flash('Введены некоректные данные. Ошибка сохранения', 'danger')
            return render_template('users/edit.html', user=params, roles=load_roles())

    flash(f"Пользователь был успешно обновлён!", 'success')
    return redirect(url_for('show', user_id=user_id))


@app.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete(user_id):
    with mysql.connection.cursor(named_tuple=True) as cursor:
        try:
            cursor.execute('DELETE FROM users WHERE id=%s;', (user_id,))
            mysql.connection.commit()
        except connector.Error:
            mysql.connection.rollback()
            flash('При удалении пользователя возникла ошибка.', 'danger')
            return redirect(url_for('users'))

    flash(f"Пользователь был успешно удалён!", 'success')
    return redirect(url_for('users'))


@app.route('/new_pass', methods=['GET', 'POST'])
@login_required
def new_pass():
    if request.method == "POST":
        old_pass = request.form.get("old_pass")
        new_pas = request.form.get("new_pass")
        rep_pass = request.form.get("rep_pass")
        old_err = ''
        new_err = pass_test(new_pas)
        rep_err = ''

        if new_pas == rep_pass:
            if not new_err:
                with mysql.connection.cursor(named_tuple=True) as cursor:
                    cursor.execute('SELECT * FROM users WHERE login=%s AND password_hash=SHA2(%s, 256);', (current_user.login, old_pass))
                    user = cursor.fetchone()
                    if user:
                        try:
                            cursor.execute('UPDATE users SET password_hash=SHA2(%s, 256) WHERE id=%s', (new_pas, current_user.id))
                            mysql.connection.commit()
                        except connector.Error:
                            mysql.connection.rollback()
                            flash('При изменении пароля возникла ошибка!', 'danger')
                            return render_template('users/new_pass.html')
                    else:
                        old_err = 'Введен неверный пароль!'
            else:
                return render_template('users/new_pass.html', new_err=new_err)
        else:
            rep_err = 'Пароли не совпадают!'

        if rep_err or old_err:
            return render_template('users/new_pass.html', rep_err=rep_err, old_err=old_err)
        else:
            flash('Пароль успешно изменен!', 'success')
            return redirect(url_for('index'))
    else:
        return render_template('users/new_pass.html')
