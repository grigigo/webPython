import os

from flask import url_for

from app import db
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
import sqlalchemy as sa


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    parent_id = db.Column(db.INTEGER, db.ForeignKey('categories.id'))

    def __repr__(self):
        return '<Category %r>' % self.name


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.INTEGER, primary_key=True)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    login = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=sa.sql.func.now())

    def __repr__(self):
        return '<User %r>' % self.login

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return ' '.join([self.last_name, self.first_name, self.middle_name or ''])


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_desc = db.Column(db.Text, nullable=False)
    full_desc = db.Column(db.Text, nullable=False)
    rating_sum = db.Column(db.INTEGER, nullable=False, default=0)
    rating_num = db.Column(db.INTEGER, nullable=False, default=0)
    category_id = db.Column(db.INTEGER, db.ForeignKey('categories.id'))
    author_id = db.Column(db.INTEGER, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, nullable=False, server_default=sa.sql.func.now())
    background_image_id = db.Column(db.INTEGER, db.ForeignKey('images.id'))

    author = db.relationship('User')
    category = db.relationship('Category')
    bg_image = db.relationship('Image')

    def __repr__(self):
        return '<Course %r>' % self.name

    @property
    def rating(self):
        if self.rating_num > 0:
            return self.rating_sum / self.rating_num
        return 0

    def reСount(self, number_sum):
        self.rating_sum = self.rating_sum + int(number_sum)
        self.rating_num = self.rating_num + 1


class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.INTEGER, primary_key=True)
    file_name = db.Column(db.String(100), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    md5_hash = db.Column(db.String(200), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=sa.sql.func.now())
    object_type = db.Column(db.String(100))
    object_id = db.Column(db.INTEGER)
    active = db.Column(db.BOOLEAN, nullable=False, default=False)

    def __repr__(self):
        return '<Image %r>' % self.file_name

    @property
    def storage_filename(self):
        _, ext = os.path.splitext(self.file_name)
        return str(self.id) + ext

    @property
    def url(self):
        return url_for('image', image_id=self.id)


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.INTEGER, primary_key=True)
    user_id = db.Column(db.INTEGER, db.ForeignKey('users.id'))
    course_id = db.Column(db.INTEGER, db.ForeignKey('courses.id'))
    review_rating = db.Column(db.INTEGER, nullable=False)
    text_review = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, server_default=sa.sql.func.now())

    course = db.relationship('Course')
    user = db.relationship('User')

    def __repr__(self):
        return '<Review %r>' % self.text_review
