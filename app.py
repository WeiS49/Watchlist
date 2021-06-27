
from flask import Flask
from flask import escape, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
import click
import os

app = Flask(__name__)
# 创建数据库连接地址
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) # 加载配置(app.config)

import click

@app.cli.command() # 使用装饰器将内容注册为命令
@click.option('--drop', is_flag=True, help='Create after drop.') # 添加(布尔类型)参数
def initdb(drop):
    """ Initialize the database. """
    if drop:   # 如果输入drop参数, 意为销毁当前表
        db.drop_all()
    db.create_all()
    click.echo('Initialize database.') # 打印提示内容.

@app.cli.command()
def forge():
    """ Generate fake data. """
    name = 'W S'
    movies = [
    {'title': 'My Neighbor Totoro', 'year': '1988'},
    {'title': 'Dead Poets Society', 'year': '1989'},
    {'title': 'A Perfect World', 'year': '1993'},
    {'title': 'Leon', 'year': '1994'},
    {'title': 'Mahjong', 'year': '1996'},
    {'title': 'Swallowtail Butterfly', 'year': '1996'},
    {'title': 'King of Comedy', 'year': '1999'},
    {'title': 'Devils on the Doorstep', 'year': '1999'},
    {'title': 'WALL-E', 'year': '2008'},
    {'title': 'The Pork of Music', 'year': '2012'},
]
    user = User(name=name)
    db.session.add(user)
    for movie in movies:
        m = Movie(title=movie['title'], year=movie['year'])
        db.session.add(m)

    db.session.commit()
    click.echo('Done.')

"""
    1. 创建模型类(继承db.Model)
    2. 声明内容(包括主键)
"""

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))

"""  
    注册上下文处理函数
    在之后的页面中, 自动传入处理内容(为了效率, 建议传入最小集合)
"""
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)

@app.errorhandler(404)
def page_not_found(e):
    # user = User.query.first()
    return render_template('404.html'), 404

@app.route('/')
def index():
    user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html', movies=movies)
    # return render_template('index.html', name=name, movies=movies)
    # return 'hello, world!'

@app.route('/greeting')
def hello():
    return 'Welcome!'

@app.route('/html')
def html():
    return '<h1>一级标题</h1><img src="http://helloflask.com/totoro.gif">'

@app.route('/user/<name>')
def user_page(name):
    # return f'hello'
    return f'hello, {escape(name)}!'

"""  
    url_for的功能是根据函数名获取内容的相对地址
    如果有多个页面, 则返回最下面的地址
"""
@app.route('/test')
def test_url_for():
    print(f"输出: {url_for('index')}")
    print(f"输出: {url_for('hello')}", type(url_for('hello')))
    print(f"输出: {url_for('html')}")
    # print(f"输出: {url_for('user_page')}") # 参数传入不全 报错
    print(f"输出: {url_for('user_page', name='mike')}")
    print(f"输出: {url_for('test_url_for')}", type(url_for('test_url_for')))
    return 'test page'





