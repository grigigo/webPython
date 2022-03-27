from flask import Flask, render_template
from faker import Faker
import random

fake = Faker()

app = Flask(__name__)
application = app

images = ['7d4e9175-95ea-4c5f-8be5-92a6b708bb3c',
          '2d2ab7df-cdbc-48a8-a936-35bba702def5',
          '6e12f3de-d5fd-4ebb-855b-8cbc485278b7',
          'afc2cfe7-5cac-4b80-9b9a-d5c65ef0c728',
          'cab5b7f2-774e-4884-a200-0c0180fa777f']


def generate_comments(replies=True):
    comments = []
    for i in range(random.randint(1, 3)):
        comment = { 'author': fake.name(), 'text': fake.text() }
        if replies:
            comment['replies'] = generate_comments(replies=False)
        comments.append(comment)
    return comments


def generate_post(i):
    return {
        'title': 'Заголовок поста',
        'author': fake.name(),
        'text': fake.paragraph(nb_sentences=100),
        'date': fake.date_time_between(start_date='-2y', end_date='now'),
        'image_id': f'{images[i]}.jpg',
        'comments': generate_comments()
    }


posts_list = sorted([generate_post(i) for i in range(5)], key=lambda x: x['date'], reverse=True)


@app.route('/')
def index():
    title = 'Главная!'
    return render_template('index.html', title=title)


@app.route('/posts')
def posts():
    title = 'Посты!'
    return render_template('posts.html', title=title, posts=posts_list)


@app.route('/post/<int:i>')
def post(i):
    p = posts_list[i]
    return render_template('post.html', title=p['title'], post=p)


@app.route('/about')
def about():
    title = 'Обо мне!'
    return render_template('about.html', message=title)
