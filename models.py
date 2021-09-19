from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Chatroom(db.Model):
    chatroom_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(48), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)

    # 1:m relationship between chatroom and message
    chatroom_messages = db.relationship("Message", backref="chatroom_message", cascade="all, delete-orphan", lazy="dynamic")

    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id

    def __repr__(self):
        return "<Chatroom {}>".format(self.name)


class Message(db.Model):
    message_id = db.Column(db.Integer, primary_key=True)
    message_contents = db.Column(db.String(500), nullable=False)
    date_time = db.Column(db.String(19), nullable=False)
    chatroom_id = db.Column(db.Integer, db.ForeignKey("chatroom.chatroom_id"), nullable=False)
    author_username = db.Column(db.String(24), db.ForeignKey("user.username"), nullable=False)
    # I set this as the FK instead of user_id because I include it in the Message's UI

    def __init__(self, message_contents, date_time, chatroom_id, author_username):
        self.message_contents = message_contents
        self.date_time = date_time
        self.chatroom_id = chatroom_id
        self.author_username = author_username

    def __repr__(self):
        return "<Message {}>".format(self.message_contents)


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(24), unique=True, nullable=False)
    password = db.Column(db.String(24), nullable=False)
    pw_hash = db.Column(db.String(64), nullable=False)

    # 1:m relationship between user and chatroom
    user_chatrooms = db.relationship("Chatroom", backref="user_chatroom", lazy="dynamic")

    # 1:m relationship between user and message
    user_messages = db.relationship("Message", backref="user_message", lazy="dynamic")

    def __init__(self, username, password, pw_hash):
        self.username = username
        self.password = password
        self.pw_hash = pw_hash

    def __repr__(self):
        return "<User {}>".format(self.username)
