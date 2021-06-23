import click
from flask import Flask, render_template, request, make_response, redirect, url_for, jsonify
from models import db, User, NewUser, Address, NoFAddress
from controllers import UsersDao
from flask.cli import AppGroup, with_appcontext
import re
import json
from utils.common import create_token, login_required, verify_token
from sqlalchemy import exists, and_, or_

app = Flask(__name__)
app.config.from_pyfile('config.py')

# 查询时显示原始SQL语句
db.app = app
db.init_app(app)

db_cli = AppGroup('db')
app.cli.add_command(db_cli)


@db_cli.command('init')
@with_appcontext
def db_init():
    print('db_init')
    db.create_all()


@db_cli.command('drop_newusers')
@with_appcontext
def db_drop_newusers():
    print('删除掉 NewUser')
    NewUser.__table__.drop(db.get_engine())


@db_cli.command('drop_all')
@with_appcontext
def db_drop_all():
    print('删除掉所有')
    db.drop_all()


@db_cli.command('mock_user')
@with_appcontext
def db_mock_user():
    new_create_user = UsersDao().create_user(name='hello', pswd='123123')
    print('mock user{}'.format(new_create_user))


@db_cli.command('mock_address')
@click.argument("id")
@with_appcontext
def db_mock_address(id):
    new_address = Address(user_id=id, name="枣强")
    new_address1 = Address(user_id=id, name="大华电子")
    new_nofaddress = NoFAddress(user_id=id, name="回龙观")
    db.session.add(new_address)
    db.session.add(new_address1)
    db.session.add(new_nofaddress)
    db.session.commit()
    print('mock address{}'.format(new_address))


@db_cli.command('just_run')
@with_appcontext
def db_mock_user():
    address = db.session.query(Address).filter_by(name='枣强').update(dict(name='枣强'))
    db.session.commit()
    print(address)
    # 是否存在


# ret = db.session.query(exists().where(Address.name=='枣强')).scalar()

@db_cli.command('just_query')
@with_appcontext
def db_just_query():
    print("db_just_query")
    addresses = Address.query.filter(and_(Address.name == '枣强233')).order_by(Address.id).limit(10).all()
    result = list(map(lambda x: x.to_json(), addresses))
    print(result)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/user/new', methods=['POST'])
def new_user():
    print("开始请求了{}".format(request.json))
    request_data = request.json
    print("new_user 请求了。{}".format(request_data))
    name = request_data['name']
    pswd = request_data['pwd']
    new_user = UsersDao().create_user(name=name, pswd=pswd)
    return json.dumps(new_user, default=userToDic)


@app.route('/api/users')
def get_api_users():
    user_list = User.query.all()
    response = {
        "title": "success",
        "list": user_list
    }
    return json.dumps(response, default=userToDic)


@app.route('/api/address/<address_id>')
def get_address_by_id(address_id):
    address = Address.query.get(address_id)
    response = {
        "title": "success",
        "list": address
    }
    return json.dumps(response, default=addressToDic)


@app.route('/api/nofaddress/<address_id>')
def get_nofaddress_by_id(address_id):
    address = NoFAddress.query.get(address_id)
    response = {
        "id": address.id,
        "name": address.name,
        "user_id": address.user_id,
    }
    return json.dumps(response)


@app.route('/api/user/nofaddress/<address_id>')
def get_user_by_id(address_id):
    user = db.session.query(User).join(NoFAddress, User.id == NoFAddress.user_id).filter(
        NoFAddress.id == address_id).first()
    return json.dumps(user, default=userToDic)


@app.route("/login", methods=["POST"])
def login():
    '''
    用户登录
    :return:token
    '''
    print("开始请求了login {}".format(request.json))
    res_dir = request.json

    if res_dir is None:
        # 这里的code，依然推荐用一个文件管理状态
        return jsonify(code=4103, msg="未接收到参数")

    # 获取前端传过来的参数
    account_name = res_dir.get("name")
    password = res_dir.get("pwd")

    # 校验参数
    if not all([account_name, password]):
        return jsonify(code=4103, msg="请填写手机号或密码")

    # if not re.match(r"1[23456789]\d{9}", account_name):
    #     return jsonify(code=4103, msg="手机号有误")

    try:
        user = UsersDao().get_user(name=account_name)
    except Exception:
        return jsonify(code=4004, msg="获取信息失败")

    # if user is None or not user.check_password(password):
    #     return jsonify(code=4103, msg="手机号或密码错误")

    # 获取用户id，传入生成token的方法，并接收返回的token
    token = create_token(user.id)

    # 把token返回给前端
    return jsonify(code=0, msg="成功", data=token)


@app.route("/user/detail")
@login_required  # 必须登录的装饰器校验
def userInfo():
    '''
    用户信息
    :return:data
    '''
    token = request.headers["z-token"]
    # 拿到token，去换取用户信息
    user = verify_token(token)

    data = {
        "name": user.name,
        "id": user.id
    }

    return jsonify(code=0, msg="成功", data=data)


def userToDic(user):
    return {
        "id": user.id,
        "name": user.name,
        "pswd": user.pswd,
        "like": user.like,
        "state": user.state,
        "dislike": user.dislike
    }


def addressToDic(address):
    return {
        "id": address.id,
        "user_id": address.user_id,
        "user_name": address.user.name,
    }


if __name__ == '__main__':
    app.run()
