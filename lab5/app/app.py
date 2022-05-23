from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from mysql_db import MySQL
import mysql.connector as connector
from check import *

app = Flask(__name__)
application = app

app.config.from_pyfile('config.py')

mysql = MySQL(app)

CREATE_PARAMS = ['login', 'password', 'first_name', 'last_name', 'middle_name', 'role_id']
UPDATE_PARAMS = ['first_name', 'last_name', 'middle_name', 'role_id']

from auth import init_login_manager, bp as auth_bp, check_rights
from visits import bp as visits_bp

init_login_manager(app)
app.register_blueprint(auth_bp)
app.register_blueprint(visits_bp)


@app.before_request
def log_visit_info():
    if request.endpoint == 'static':
        return None
    user_id = getattr(current_user, 'id', None)
    with mysql.connection.cursor(named_tuple=True) as cursor:
        try:
            cursor.execute('INSERT INTO visit_logs (user_id, path) VALUES (%s, %s);', (user_id, request.path))
            mysql.connection.commit()
        except:
            pass


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


def get_users():
    return [{'user_id': 1, 'login': 'user', 'password': 'qwerty'}]


@app.route('/')
def index():  # put application's code here
    return render_template('index.html')


@app.route('/users')
def users():
    with mysql.connection.cursor(named_tuple=True) as cursor:
        cursor.execute(
            'SELECT users.*, roles.name AS role_name FROM users LEFT OUTER JOIN roles ON users.role_id = roles.id;')
        users = cursor.fetchall()
    return render_template('users/index.html', users=users)


@app.route('/users/new')
@login_required
@check_rights('create')
def new():
    return render_template('users/new.html', user={}, roles=load_roles())


@app.route('/users/create', methods=['POST'])
@login_required
@check_rights('create')
def create():
    params = request_params(CREATE_PARAMS)
    pass_err = pass_test(params['password'])
    login_err = login_test(params['login'])

    if not (pass_err or login_err):
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
                               login_err=login_err)


@app.route('/users/<int:user_id>')
@login_required
@check_rights('show')
def show(user_id):
    with mysql.connection.cursor(named_tuple=True) as cursor:
        cursor.execute('SELECT * FROM users WHERE id=%s;', (user_id,))
        user = cursor.fetchone()
    return render_template('users/show.html', user=user)


@app.route('/users/<int:user_id>/edit')
@login_required
@check_rights('update')
def edit(user_id):
    with mysql.connection.cursor(named_tuple=True) as cursor:
        cursor.execute('SELECT * FROM users WHERE id=%s;', (user_id,))
        user = cursor.fetchone()
    return render_template('users/edit.html', user=user, roles=load_roles())


@app.route('/users/<int:user_id>/update', methods=['POST'])
@login_required
@check_rights('update')
def update(user_id):
    params = request_params(UPDATE_PARAMS)
    params['id'] = user_id
    if not current_user.can('assign_role'):
        del params['role_id']
    with mysql.connection.cursor(named_tuple=True) as cursor:
        try:
            cursor.execute(f'''
                            UPDATE users SET {','.join(['{0}=%({0})s'.format(k) for k, _ in params.items() if k != 'id'])} WHERE id=%(id)s;
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
@check_rights('delete')
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


@app.route('/pass', methods=['GET', 'POST'])
@login_required
def change_pass():
    if request.method == "POST":
        old_pass = request.form.get("old_pass")
        new_pass = request.form.get("new_pass")
        rep_pass = request.form.get("rep_pass")
        old_err = ''
        new_err = pass_test(new_pass)
        rep_err = ''

        if new_pass == rep_pass:
            if not new_err:
                with mysql.connection.cursor(named_tuple=True) as cursor:
                    cursor.execute('SELECT * FROM users WHERE login=%s AND password_hash=SHA2(%s, 256);',
                                   (current_user.login, old_pass))
                    user = cursor.fetchone()
                    if user:
                        try:
                            cursor.execute('UPDATE users SET password_hash=SHA2(%s, 256) WHERE id=%s',
                                           (new_pass, current_user.id))
                            mysql.connection.commit()
                        except connector.Error:
                            mysql.connection.rollback()
                            flash('При удалении пользователя возникла ошибка.', 'danger')
                            return redirect(url_for('new_pass'))
                    else:
                        old_err = 'Введен неверный пароль!'
            else:
                return render_template('users/change_pass.html', new_err=new_err)
        else:
            rep_err = 'Пароли не совпадают!'

        if rep_err or old_err:
            return render_template('users/change_pass.html', rep_err=rep_err, old_err=old_err)
        else:
            flash('Пароль успешно изменен!', 'success')
            return redirect(url_for('index'))
    return render_template('users/change_pass.html', user=current_user)


if __name__ == '__main__':
    app.run()
