
from flask import Flask
from flask import escape, url_for, render_template, redirect, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import click
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'dev'

# 创建数据库连接地址
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) # 加载配置(app.config)
login_manager = LoginManager(app) # 实例化扩展类
login_manager.login_view = 'login'

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

@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """ Create user. """
    db.create_all()

    user = User.query.first() # 获取user实例(下面创建的User类)
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)
        db.session.add(user)
    db.session.commit()
    click.echo('Done.')

@login_manager.user_loader
def load_user(user_id): # 以id作为参照, 载入用户信息
    user = User.query.get(int(user_id))
    return user # 返回用户对象



"""
    1. 创建模型类(继承db.Model)
    2. 声明内容(包括主键)
"""
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128)) # 以哈希加密的方式存储密码

    def set_password(self, password):
        """ 生成加密密码 """
        self.password_hash = generate_password_hash(password)
    
    def validate_password(self, password):
        """ 验证密码 """
        return check_password_hash(self.password_hash, password)

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

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('405.html'), 405

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST': # 判断传入方法是否为POST
        
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        
        # 获取表单数据
        title = request.form.get('title')
        year = request.form.get('year')
        # 验证数据是否合法(在服务器端的额外验证)
        if not title or not year or len(year) > 4:
            flash('Invalid input.') # 显示错误提示
            return redirect(url_for('index')) # 重定向回主页
        # 保存表单数据到数据库
        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('index'))

    # 如果传入方法为get则直接返回静态页面
    movies = Movie.query.all()
    return render_template('index.html', movies=movies)
    # return render_template('index.html', name=name, movies=movies)
    # return 'hello, world!'

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        current_user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('settings.html')



@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # 这里需要使用方括号(callable)
        username = request.form['username']
        password = request.form['password']

        # 输入合法性验证(未输入完全)
        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))
        
        user = User.query.first() # 目前只有一个用户
        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('index'))
        
        flash('Invalid username or password.') # 如果验证失败(账号/密码错误)
        return redirect(url_for('login')) # 重定向到登陆页面
    return render_template('login.html') # 只访问网页时候的处理方式

@app.route('/logout')
@login_required # 装饰器, 要求登录状态才会生效
def logout():
    logout_user()
    flash("Goodbye.")
    return redirect(url_for('index'))

@app.route('/movie/edit/<int:movie_id>', methods=['POST', 'GET'])
@login_required
def edit(movie_id):
    """ 根据电影的编号对内容进行修改 """
    movie = Movie.query.get_or_404(movie_id) # 如果找到则则返回记录, 否则返回404
    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) > 4:
            flash('Invalid input')
            return redirect(url_for('edit', movie_id=movie_id))

        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('edit', movie_id=movie_id))

    return render_template('index.html', movie=movie)

@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))

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





