# -*- coding:UTF-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:123456@127.0.0.1:3306/TreeHole"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///"+"treehole.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'zxxdsbafdafafafafwafwsfsafs'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_TYPE'] = 'redis'
app.config['JSON_AS_ASCII'] = False

db = SQLAlchemy(app)


# 管理员表格
class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    num = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)


# 用户表格
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    num = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    messages = db.relationship("Message", backref='user')
    praises = db.relationship("Praise", backref='user')
    new_msg = db.relationship("New_Msg", backref='user')


# 评论
class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    contain = db.Column(db.String(40000), nullable=False)
    to_commenter = db.Column(db.String(128), nullable=False)
    to_commenter_id = db.Column(db.Integer, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    # is_know = db.Column(db.Integer, default=0)
    # is_delete = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 关联评论人id
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'))


# 新消息
class New_Msg(db.Model):
    __tablename__ = 'new_msg'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    contain = db.Column(db.String(40000), nullable=False)
    to_commenter = db.Column(db.String(128), nullable=False)
    to_commenter_id = db.Column(db.Integer, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    is_know = db.Column(db.Integer, default=0)
    is_delete = db.Column(db.Integer, default=0)
    is_black = db.Column(db.Integer, default=0)
    ori_com_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 关联评论人id
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'))


# 留言条
class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(40000), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    dianzan = db.Column(db.Integer, nullable=False)
    flag = db.Column(db.Integer, nullable=False)
    tag = db.Column(db.String(32), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 留言条关联一下用户
    comments = db.relationship("Comment", backref='message')
    praises = db.relationship("Praise", backref='message')
    image = db.relationship("Images", backref='message')


# 点赞
class Praise(db.Model):
    __tablename__ = 'praise'
    id = db.Column(db.Integer, primary_key=True)
    flag = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 留言条关联一下用户
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'))


# 图片
class Images(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(256), nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'))


if __name__ == '__main__':
    db.create_all()
    # db.drop_all()