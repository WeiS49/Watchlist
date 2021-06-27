
from flask import Flask
from flask import escape, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return 'hello, world!'

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
@app.route('/test2')
def test_url_for():
    print(f"输出: {url_for('index')}")
    print(f"输出: {url_for('hello')}", type(url_for('hello')))
    print(f"输出: {url_for('html')}")
    # print(f"输出: {url_for('user_page')}") # 参数传入不全 报错
    print(f"输出: {url_for('user_page', name='mike')}")
    print(f"输出: {url_for('test_url_for')}", type(url_for('test_url_for')))
    return 'test page'

