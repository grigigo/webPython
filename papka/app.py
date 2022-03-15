from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    name = 'env'
    return f"Hello, {name}!"
