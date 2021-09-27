# -*- coding:UTF-8 -*-

from PIL import Image
import os
import sqlite3
import sys
from operator import and_
from flask import jsonify, request, session, render_template, redirect, current_app
from database import app, db, Admin, Message, Comment, User, Praise, Images, New_Msg
from datetime import *
# reload(sys)
# sys.setdefaultencoding('utf8')


# 获得数据
class GetMessages:
    def __init__(self):
        self.payload_all = []  # 所有留言和信息
        self.payload_personal = []  # 个人留言和信息
        self.payload_admin = []  # 所有留言和信息
        self.comment_dic = {}
        self.payload_com = []
        self.pic_dic = {}
        self.payload_pic = []

    def GetOthMsg(self, message):
        user = User.query.filter(User.id == message.user_id).first()
        content = message.content
        tag = message.tag
        create_time = message.create_time.strftime("%Y年%m月%d日 %H:%M")
        user_name = user.username
        user_id = message.user_id
        message_id = message.id
        dianzan = message.dianzan
        return content, tag, create_time, user_name, message_id, user_id, dianzan

    def GetImgCom(self, message):
        payload_com = []
        payload_pic = []
        images = message.image
        comments = message.comments
        for image in images:
            pic_dic = {}
            pic_dic['msg_pic_id'] = message.id  # 图片对应的留言id
            pic_dic['path'] = image.path  # 图片路径
            payload_pic.append(pic_dic)
        for comment in comments:
            comment_dic = {}
            comment_user = User.query.get(comment.user_id)
            comment_dic['commenter_id'] = comment.user_id
            comment_dic['msg_com_id'] = message.id
            comment_dic['commenter'] = comment_user.username
            comment_dic['contain'] = comment.contain
            comment_dic['comment_id'] = comment.id
            comment_dic['to_commenter'] = comment.to_commenter
            comment_dic['create_time'] = comment.create_time.strftime("%Y年%m月%d日 %H:%M")
            payload_com.append(comment_dic)
        return payload_pic, payload_com

    def AllGetMessages(self):  # 用户默认界面获取内容
        messages = Message.query.all()
        for message in messages:
            if message.flag == 0:
                content, tag, create_time, user_name, message_id, user_id, dianzan = GetMessages.GetOthMsg(self, message)
                payload_pic, payload_com = GetMessages.GetImgCom(self, message)

                data = [content, tag, create_time, user_name, message_id, user_id, dianzan, payload_pic, payload_com]
                self.payload_all.append(data)
        self.payload_all.reverse()
        return self.payload_all

    def PersonGetMessages(self):  # 个人中心界面获取内容
        user_id = session.get("user_id")
        user = User.query.get(user_id)
        messages = user.messages
        for message in messages:
            content, tag, create_time, user_name, message_id, user_id, dianzan = GetMessages.GetOthMsg(self, message)
            payload_pic, payload_com = GetMessages.GetImgCom(self, message)

            data = [content, tag, create_time, user_name, message_id, user_id, dianzan, payload_pic, payload_com]
            self.payload_personal.append(data)
        self.payload_personal.reverse()
        return self.payload_personal

    def AdminGetMessages(self):  # 管理员界面获取内容
        messages = Message.query.all()
        for message in messages:
            content, tag, create_time, user_name, message_id, user_id, dianzan = GetMessages.GetOthMsg(self, message)
            payload_pic, payload_com = GetMessages.GetImgCom(self, message)

            data = [content, tag, create_time, user_name, message_id, user_id, dianzan, payload_pic, payload_com]
            self.payload_admin.append(data)
        self.payload_admin.reverse()
        return self.payload_admin


# 压缩图片
def compress_image(file):
    pic_style = file.split('.')[2]
    size = os.path.getsize(file)/1024
    if size > 200 and pic_style != 'gif':
        im = Image.open(file)
        im.save(file, quality=50)
    # elif size > 200 and pic_style == 'gif':
    #     im = Image.open(file)
    #     im.save(file, quality=80)

# @app.route('/favicon.ico')
# def get_fav():
#     return current_app.send_static_file('/static/favicon.ico')


# 显示用户注册界面
@app.route('/register_html')
def register_html():
    return render_template('register_html.html')


# 显示用户登录界面
@app.route('/', methods=['GET', 'POST'])
def login():
    if session.get('user_num') is None and session.get("user_id") is None:  # 判断session中是否还有内容
        return render_template('login.html')
    else:
        return redirect('/user/message/board')


# 显示用户默认界面
@app.route('/user/message/board')
def user_index_route():
    # get_new_msg()
    user_id = session.get("user_id")
    if user_id is None:
        return render_template("error.html")
    else:
        return render_template("index.html")


# 显示个人中心界面
@app.route('/user_center')
def user_center_route():
    user_id = session.get("user_id")
    if user_id is None:
        return render_template("error.html")
    else:
        return render_template("user_center.html")


# 显示管理员默认界面
@app.route('/admin_index')
def admin_index_route():
    admin_id = session.get("admin_id")
    if admin_id is None:
        return render_template("error.html")
    else:
        return render_template("admin_index.html")


# 显示管理员登录界面
@app.route('/admin')
def admin_login_route():
    return render_template("admin.html")


# 显示消息界面
@app.route('/my_msg')
def my_msg():
    return render_template('my_msg.html')


# 显示查看原文界面
@app.route('/look/original/article')
def look_original():
    return render_template('original_art.html')


# 显示发送留言界面
@app.route('/user/send/message')
def user_send_message():
    user_id = session.get("user_id")
    if user_id is None:
        return render_template("error.html")
    else:
        return render_template('send_message.html')


# 显示修改密码界面
@app.route('/change_pasw')
def changepasw():
    user_id = session.get("user_id")
    if user_id is None:
        return render_template("error.html")
    else:
        return render_template('change_pasw.html')


# 显示修改昵称界面
@app.route('/change_name')
def changename():
    user_id = session.get("user_id")
    if user_id is None:
        return render_template("error.html")
    else:
        return render_template('change_name.html')


# 显示管理员修改密码界面
@app.route('/admin/change_pasw')
def admin_changepasw():
    admin_id = session.get("admin_id")
    if admin_id is None:
        return render_template("error.html")
    else:
        return render_template('admin_change_pasw.html')


# 管理员登录
@app.route('/admin/login', methods=['POST'])
def admin_login():
    num = request.form['num']
    password = request.form['password']
    admin = Admin.query.filter(Admin.num == num).first()
    if not all([num, password]):
        return jsonify(status='-1', msg='未输入账号或密码！')
    if admin is None or password != admin.password:
        return jsonify(status='0', msg='用户名或密码错误！')

    session["admin_num"] = num
    session["admin_id"] = admin.id
    return jsonify(status='1', msg='登录成功！')


# 管理员修改密码
@app.route('/admin/change/pasw', methods=["POST"])
def admin_change_pasw():
    data = request.form
    old_pasw = data.get("old_pasw")
    new_pasw = data.get("new_pasw")
    admin_id = session.get("admin_id")
    admin = Admin.query.filter(Admin.id == admin_id).first()
    password = admin.password

    if old_pasw != password:
        return jsonify(status='0', msg="旧密码错误!")
    else:
        admin.password = new_pasw
        db.session.add(admin)
        db.session.commit()
        return jsonify(status='1', msg="修改成功!")


# 管理员拉黑留言
@app.route('/admin/disshow/message', methods=['POST'])
def admin_disshow_mesg():
    admin_num = session.get("admin_num")
    data = request.form
    msg_id = data.get('msg_id')
    message = Message.query.filter(Message.id == msg_id).first()
    new_msgs = New_Msg.query.filter(New_Msg.message_id == msg_id).all()
    flag = message.flag
    if admin_num is None:
        return jsonify(status='0', msg="你还未登录!")
    else:
        if message.flag == 0:
            message.flag = 1
            for new_msg in new_msgs:
                new_msg.is_black = 1
                db.session.add(new_msg)
        else:
            message.flag = 0
            for new_msg in new_msgs:
                new_msg.is_black = 0
                db.session.add(new_msg)
        db.session.add(message)
        db.session.commit()

        return jsonify(status='1', flag=flag)


# 显示是否被拉黑
@app.route('/load/disshow_flag')
def load_disshow_flag():
    messages = Message.query.all()
    flag_list = []
    for message in messages:
        if message.flag == 1:
            flag_list.append(message.id)
    return jsonify(status='1', pdata=flag_list)


# 管理员退出登录 √
@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('admin_num')
    session.pop('admin_id')
    if session.get('admin_num') is None and session.get("admin_id") is None:  # 判断session中是否还有内容
        return jsonify(status='1', msg='退出成功!')
    else:
        return jsonify(status='0', msg='退出失败!')


# 用户注册
@app.route('/register', methods=["POST"])
def register():
    data = request.form
    num = data.get("num")
    username = data.get("username")
    password = data.get("password")
    result = User.query.filter(User.num == num).first()
    if result is not None:
        return jsonify(status='-1', msg="该学号已被注册")
    user = User(num=num, username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify(status="1", msg="注册成功!")


# 用户登录 √
@app.route('/user/login', methods=["POST", "GET"])
def user_login():
    num = request.form['num']
    password = request.form['password']
    user = User.query.filter(User.num == num).first()
    if not all([num, password]):
        return jsonify(status='-1', msg='未输入账号或密码！')
    if user is None or password != user.password:
        return jsonify(status='0', msg='用户名或密码错误！')

    session["user_num"] = num
    session["user_id"] = user.id
    return jsonify(status='1', msg='登录成功！')


# 用户退出登录 √
@app.route('/user/logout', methods=['POST'])
def user_logout():
    session.pop('user_num')
    session.pop('user_id')
    if session.get('user_num') is None and session.get("user_id") is None:  # 判断session中是否还有内容
        return jsonify(status='1', msg='退出成功!')
    else:
        return jsonify(status='0', msg='退出失败!')


# 用户修改密码
@app.route('/change/pasw', methods=["POST"])
def change_pasw():
    data = request.form
    old_pasw = data.get("old_pasw")
    new_pasw = data.get("new_pasw")
    user_id = session.get("user_id")
    user = User.query.filter(User.id == user_id).first()
    password = user.password

    if old_pasw != password:
        return jsonify(status='0', msg="旧密码错误!")
    else:
        user.password = new_pasw
        db.session.add(user)
        db.session.commit()
        return jsonify(status='1', msg="修改成功!")


# 用户修改昵称
@app.route('/change/name', methods=["POST"])
def change_name():
    data = request.form
    new_name = data.get("new_name")
    user_id = session.get("user_id")
    user = User.query.filter(User.id == user_id).first()
    comments = Comment.query.filter(Comment.to_commenter == user.username).all()

    for comment in comments:
        comment.to_commenter = new_name
    user.username = new_name
    db.session.add(user)
    db.session.commit()
    return jsonify(status='1', msg="修改成功!")


# 用户默认页面
@app.route('/user/index')
def user_index():
    user_id = session.get("user_id")
    user = User.query.filter(User.id == user_id).first()
    m = GetMessages()
    payload_all = m.AllGetMessages()
    return jsonify(status='1', datas=payload_all, user=user.username)


# 用户中心界面
@app.route('/user/center')
def user_center():
    m = GetMessages()
    payload_personal = m.PersonGetMessages()
    return jsonify(status='1', datas=payload_personal)


# 管理员默认界面
@app.route('/admin/index')
def admin_index():
    m = GetMessages()
    payload_admin = m.AdminGetMessages()
    return jsonify(status='1', datas=payload_admin)


# 展示点赞颜色
@app.route('/load/dianzan')
def load_dianzan():
    user_id = session.get('user_id')
    flags = Praise.query.filter(Praise.user_id == user_id).all()
    data_list = []
    if flags is None:
        return jsonify(status='0')
    else:
        for flag in flags:
            message = Message.query.filter(Message.id == flag.message_id).first()
            if message.flag == 0:
                data_list.append(flag.message_id)
        return jsonify(status='1', pdata=data_list)


# 用户中心界面展示颜色
@app.route('/user/center/load/dianzan')
def user_center_load_dianzan():
    user_id = session.get('user_id')
    flags = Praise.query.filter(Praise.user_id == user_id).all()
    data_list = []
    if flags is None:
        return jsonify(status='0')
    else:
        for flag in flags:
            message = Message.query.filter(Message.id == flag.message_id).first()
            if message.user_id == user_id:
                data_list.append(flag.message_id)
        return jsonify(status='1', pdata=data_list)


# 加载点赞数和点赞
@app.route('/get/dianzan', methods=['POST'])
def get_dianzan():
    data = request.form
    m_id = data.get('m_id')
    user_id = session.get('user_id')
    message = Message.query.filter(Message.id == m_id).first()
    praise = Praise.query.filter(and_(Praise.user_id == user_id, Praise.message_id == m_id)).first()

    dianzan = message.dianzan
    result = Message.query.filter(Message.id == m_id).first()  # 修改数据库中点赞数
    if praise is None:
        dianzan_count = dianzan + 1
        result.dianzan = dianzan_count
        p = Praise(flag=1, user_id=user_id, message_id=m_id)
        db.session.add(p)
        db.session.commit()
        return jsonify(flag='0', dianzan=dianzan_count)
    else:
        dianzan_count = dianzan - 1
        result.dianzan = dianzan_count
        ele = Praise.query.filter(and_(Praise.user_id == user_id, Praise.message_id == m_id)).first()
        db.session.delete(ele)
        db.session.commit()
        return jsonify(flag='1', dianzan=dianzan_count)


# 用户发布留言 √
@app.route('/user/message', methods=["POST"])
def user_post_message():
    data = request.form
    tags = data.get("tags")
    content = data.get("content")
    user_id = session.get("user_id")

    message = Message(content=content, user_id=user_id, tag=tags, flag=0, dianzan=0)
    if request.files.get("file") is not None:
        db.session.add(message)
        db.session.commit()
        message_id = message.id
        images = request.files.getlist("file")
        count = 1
        for image in images:
            now = datetime.now()
            b_image = image.read()
            file_name = str(count) + '-' + str(now.year) + str(now.month) + str(now.day) \
                + str(now.hour) + str(now.minute) + str(now.second) + '.' + image.filename.split('.')[len(image.filename.split("."))-1]
            path = './static/images/' + file_name
            with open(path, 'wb') as f:
                f.write(b_image)
                f.close()
            compress_image(path)  # 进行图片压缩
            img = Images(message_id=message_id, path="/static/images/"+file_name)
            db.session.add(img)
            db.session.commit()
            count = count + 1
        return jsonify(status='1', msg="发送成功!")

    db.session.add(message)
    db.session.commit()
    return jsonify(status='1', msg="发送成功!")


# 用户删除留言
@app.route('/user/delete/message', methods=["POST"])
def user_del_message():
    username = session.get("user_num")
    if username is None:
        return jsonify(status='0', msg="出错了，你还未登录")
    data = request.form
    message_id = data.get("msg_id")
    user_id = session.get("user_id")

    msg = Message.query.filter(Message.id == message_id).first()
    images = msg.image
    if msg is None:
        return jsonify(status='-1', msg="留言不存在")

    if user_id != msg.user.id:
        return jsonify(status='-1', msg="你不是作者不能操作")
    else:
        new_msgs = New_Msg.query.filter(New_Msg.message_id == message_id).all()
        if new_msgs is not None:
            for new_msg in new_msgs:
                new_msg.is_delete = 1
                new_msg.message_id = 0
                db.session.add(new_msg)
                db.session.commit()
        for image in images:
            os.remove("."+image.path)
        Comment.query.filter(Comment.message_id == message_id).delete()
        Images.query.filter(Images.message_id == message_id).delete()
        Praise.query.filter(Praise.message_id == message_id).delete()
        Message.query.filter(Message.id == message_id).delete()
        db.session.commit()
        return jsonify(status='1', msg="删除成功")


# 用户添加评论
@app.route('/add/comment', methods=['POST'])
def add_comment():
    user_id = session.get('user_id')
    if user_id is None:
        return jsonify(status='0', msg="出错了，你还未登录")
    data = request.form
    message_id = data.get('message_id')
    contain = data.get('comment')
    to_commenter = data.get('to_commenter')
    to_commenter_id = data.get('to_commenter_id')
    c = Comment(contain=contain, user_id=user_id, message_id=message_id, to_commenter=to_commenter, to_commenter_id=to_commenter_id)
    db.session.add(c)
    db.session.commit()

    if c.user_id != c.to_commenter_id:
        nc = New_Msg(contain=contain, user_id=user_id, message_id=message_id, to_commenter=to_commenter, to_commenter_id=to_commenter_id, ori_com_id=c.id)
        db.session.add(nc)
        db.session.commit()

    new_comment_id = c.id
    user = User.query.filter(User.id == user_id).first()
    return jsonify(status='1', msg='添加成功', new_comment_id=new_comment_id, username=user.username, user_id=user.id)


# 用户删除评论
@app.route('/user/delete/comment', methods=["POST"])
def user_del_comment():
    username = session.get("user_num")
    if username is None:
        return jsonify(status='0', msg="出错了，你还未登录")
    data = request.form
    com_id = data.get("com_id")
    comment = Comment.query.get(com_id)
    if comment is None:
        return jsonify(status='-1', msg="留言不存在")
    else:
        new_msg = New_Msg.query.filter(and_(New_Msg.ori_com_id == com_id, New_Msg.is_delete == 0)).first()
        if new_msg is not None:
            new_msg.is_delete = 1
            new_msg.message_id = 0
            db.session.add(new_msg)
            db.session.commit()
        Comment.query.filter(Comment.id == com_id).delete()
        db.session.commit()
        return jsonify(status='1', msg="删除成功")


# 获得最新消息
@app.route('/get/new_msg')
def get_new_msg():
    new_data_list = []
    new_msg_num = 0
    user_id = session.get('user_id')
    if user_id is not None:
        comments = New_Msg.query.all()
        for comment in comments:
            if user_id == comment.to_commenter_id and user_id != comment.user_id:
                new_data_dic = {}
                user = User.query.filter(User.id == comment.user_id).first()
                if comment.to_commenter == '':
                    new_data_dic['a_flag'] = 0
                else:
                    new_data_dic['a_flag'] = 1
                new_data_dic['is_know'] = comment.is_know
                new_data_dic['is_delete'] = comment.is_delete | comment.is_black
                new_data_dic['commenter'] = user.username
                new_data_dic['commenter_id'] = comment.user_id
                new_data_dic['contain'] = comment.contain
                new_data_dic['time'] = comment.create_time.strftime("%Y年%m月%d日 %H:%M")
                new_data_dic['belong_msg_id'] = comment.message_id
                new_data_dic['comment_id'] = comment.id
                new_data_list.append(new_data_dic)
                if comment.is_know == 0:
                    new_msg_num = new_msg_num + 1
        new_data_list.reverse()
        return jsonify(status=1, new_data_list=new_data_list, new_msg_num=new_msg_num, msg="操作成功!")
    else:
        return jsonify(status=0, msg="你还未登录!")


# 一键已读
@app.route('/all/new_msg/look')
def all_new_msg_look():
    user_id = session.get('user_id')
    if user_id is not None:
        comments = New_Msg.query.filter(New_Msg.is_know == 0).all()
        for comment in comments:
            if user_id == comment.to_commenter_id:
                comment.is_know = 1
                db.session.add(comment)
        db.session.commit()
        return jsonify(status=1, msg="操作成功!")
    else:
        return jsonify(status=0, msg="你还未登录!")


# 删除我的消息
@app.route('/del/my_msg', methods=["POST"])
def del_my_msg():
    data = request.form
    New_Msg.query.filter(New_Msg.id == data.get('comment_id')).delete()
    db.session.commit()
    return jsonify(status=1, msg="操作成功!")


# 查看原文
@app.route('/get/original/article', methods=['POST', 'GET'])
def get_original():
    global belong_msg_id
    if request.method == 'POST':
        data = request.form
        belong_msg_id = data.get('belong_msg_id')
        comment_id = data.get('comment_id')
        new_c = New_Msg.query.filter(New_Msg.id == comment_id).first()
        if new_c.is_delete or new_c.is_black == 1:
            new_c.is_know = 1
            db.session.add(new_c)
            db.session.commit()
            return jsonify(status=0, msg="该评论已被删除或不可见!")
        else:
            new_c.is_know = 1
            db.session.add(new_c)
            db.session.commit()
            return jsonify(status=1, msg="请求成功!")
    elif request.method == 'GET':
        message = Message.query.filter(Message.id == belong_msg_id).first()
        if message.flag == 0:
            m = GetMessages()
            content, tag, create_time, user_name, message_id, user_id, dianzan = m.GetOthMsg(message)
            payload_pic, payload_com = m.GetImgCom(message)
            data = [content, tag, create_time, user_name, message_id, user_id, dianzan, payload_pic, payload_com]
            return jsonify(status=1, data=data)
        else:
            return jsonify(status=0)


if __name__ == '__main__':
    app.run(debug=True)