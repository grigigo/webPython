from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user

from app import db
from models import Category, Course, User, Review
from tools import CoursesFilter, ImageSaver

bp = Blueprint('courses', __name__, url_prefix='/courses')

COURSE_PARAMS = ['name', 'short_desc', 'full_desc', 'author_id', 'category_id']

PER_PAGE = 5


def params():
    return {p: request.form.get(p) for p in COURSE_PARAMS}


def search_params():
    return {
        'name': request.args.get('name'),
        'category_ids': request.args.getlist('category_ids')
    }


@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    courses = CoursesFilter(**search_params()).perform()
    pagination = courses.paginate(page, PER_PAGE)
    courses = pagination.items
    categories = Category.query.all()
    return render_template('courses/index.html', courses=courses, categories=categories, search_params=search_params(),
                           pagination=pagination)


@bp.route('/new')
def new():
    categories = Category.query.all()
    users = User.query.all()
    return render_template('courses/new.html', categories=categories, users=users)


@bp.route('/create', methods=['POST'])
def create():
    f = request.files.get('background_img')
    if f and f.filename:
        img = ImageSaver(f).save()

    course = Course(**params(), background_image_id=img.id)
    db.session.add(course)
    db.session.commit()

    flash(f"Курс {course.name} был успешно создан!", 'success')

    return redirect(url_for('courses.index'))


@bp.route('/<int:course_id>')
def show(course_id):
    course = Course.query.get(course_id)
    reviews = Review.query.order_by(Review.created_at.desc()).filter(Review.course_id.ilike(course_id)).limit(5)
    if current_user.is_authenticated:
        user_review = Review.query.filter(Review.user_id.ilike(current_user.id)).first()
    return render_template('courses/show.html', course=course, reviews=reviews, user_review=user_review)


@bp.route('/<int:course_id>/create_review', methods=['POST'])
def create_review(course_id):
    rating = request.form.get("user_rating_radio")
    user_review = request.form.get('user_review')
    par = {"user_id": current_user.id, "course_id": course_id, "review_rating": rating, "text_review": user_review}

    course = Course.query.get(course_id)
    course.reСount(rating)
    db.session.add(course)
    db.session.commit()

    review = Review(**par)
    db.session.add(review)
    db.session.commit()

    flash(f"Отзыв был успешно создан!", 'success')

    return redirect(url_for('courses.show', course_id=course_id))

@bp.route('/<int:course_id>/reviews')
def reviews_show(course_id):
    fil = request.args.get('fil', 0, type=int)
    page = request.args.get('page', 1, type=int)
    pagination = Review.query.paginate(page, PER_PAGE)

    if fil == 0:
        reviews = Review.query.order_by(Review.created_at.desc()).filter(Review.course_id.ilike(course_id)).limit(PER_PAGE).offset((page-1)*PER_PAGE)
    elif fil == 1:
        reviews = Review.query.order_by(Review.created_at.asc()).filter(Review.course_id.ilike(course_id)).limit(PER_PAGE).offset((page-1)*PER_PAGE)
    elif fil == 2:
        reviews = Review.query.order_by(Review.review_rating.desc()).filter(Review.course_id.ilike(course_id)).limit(PER_PAGE).offset((page-1)*PER_PAGE)
    else:
        reviews = Review.query.order_by(Review.review_rating.asc()).filter(Review.course_id.ilike(course_id)).limit(PER_PAGE).offset((page-1)*PER_PAGE)

    return render_template('courses/reviews.html', reviews=reviews, fil=fil, pagination=pagination)
