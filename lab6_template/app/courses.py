from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required

from app import db
from models import Category, Course, User

bp = Blueprint('courses', __name__, url_prefix='/courses')

COURSES_PARAMS = ['name', 'short_desc', 'full_desc', 'author_id', 'category_id']

def params():
    return { p: request.form.get(p) for p in COURSES_PARAMS }


def search_params():
    return {
        'name': request.args.get('name'),
        'category_ids': request.args.getlist('category_ids')
    }

@bp.route('/')
def index():
    courses = Course.query.all()
    categories = Category.query.all()
    return render_template('courses/index.html', courses=courses, categories=categories, search_params=search_params(),
                           pagination={ 'iter_pages': lambda: [] })


@bp.route('/new')
def new():
    categories = Category.query.all()
    users = User.query.all()
    return render_template('courses/new.html', categories=categories, users=users)


@bp.route('/create', methods=['POST'])
def create():
    course = Course(**params())
    db.session.add(course)
    db.session.commit()

    flash(f'Курс {course.name} был успешно создан!', 'success')
    
    return redirect(url_for('courses.index'))


@bp.route('/<int:course_id>')
def show():
    pass
