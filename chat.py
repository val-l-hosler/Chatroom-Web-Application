import os
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, json
from werkzeug.security import check_password_hash, generate_password_hash

from models import db, Chatroom, Message, User

app = Flask(__name__)

DEBUG = True
SECRET_KEY = os.urandom(12)

SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(app.root_path, "chat.db")

app.config.from_object(__name__)
app.config.from_envvar("CHAT_SETTINGS", silent=True)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


if __name__ == '__main__':
    app.run()


# I initialized the database locally before uploading it to pythonanywhere.com
@app.cli.command("initdb")
def initdb_command():
    db.create_all()
    print("Initialized the database.")


def get_chatroom_id(name):
    rv = Chatroom.query.filter_by(name=name).first()
    return rv.chatroom_id if rv else None


def get_chatroom_name(chatroom_id):
    rv = Chatroom.query.filter_by(chatroom_id=chatroom_id).first()
    return rv.name if rv else None


def get_user_id(username):
    rv = User.query.filter_by(username=username).first()
    return rv.user_id if rv else None


def get_username(user_id):
    rv = User.query.filter_by(user_id=user_id).first()
    return rv.username if rv else None


@app.before_request
def before_request():
    g.user = None
    if "user_id" in session:
        g.user = User.query.filter_by(user_id=session["user_id"]).first()


@app.route("/", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("chatrooms"))
    else:
        error_username = ""
        error_password = ""
        if request.method == "POST":
            user = User.query.filter_by(username=request.form["username"]).first()
            if user is None:
                error_username = "The username is invalid"
            elif not check_password_hash(user.pw_hash, request.form["password"]):
                error_password = "The password does not match the provided username"
            else:
                session["user_id"] = user.user_id
                return redirect(url_for("login"))

    return render_template("login.html", error_username=error_username, error_password=error_password)


@app.route("/chatrooms", methods=["GET", "POST"])
def chatrooms():
    if g.user:
        session[
            "poller_count"] = 0  # This counter is used to keep track of if the existing messages should be loaded (see update_messages)
        session["current_chatroom"] = 0
        session["viewed_message_ids"] = []  # This list keeps track of the user's viewed messages in a chatroom

        error_chatroom_name = ""
        if request.method == "POST":
            if not request.form["chatroom-name"]:
                error_chatroom_name = "You have to enter a chatroom name"
            elif request.form["chatroom-name"].__len__() > 48:
                error_chatroom_name = "The chatroom name is too long. Chatroom names can only be up to 48 characters in length."
            elif get_chatroom_id(request.form["chatroom-name"]) is not None:
                error_chatroom_name = "The chatroom name is already taken."
            else:
                db.session.add(
                    Chatroom(request.form["chatroom-name"], session["user_id"]))
                db.session.commit()
                flash("You successfully created a chatroom")
                return redirect(url_for("chatrooms"))

        all_chatrooms = Chatroom.query.order_by(Chatroom.name).all()
        user_created_chatrooms = Chatroom.query.filter_by(user_id=session["user_id"]).order_by(Chatroom.name).all()
        return render_template("chatrooms.html", all_chatrooms=all_chatrooms, error_chatroom_name=error_chatroom_name,
                               user_created_chatrooms=user_created_chatrooms)
    else:
        abort(404)


@app.route("/delete_chatroom/<chatroom_id>")
def delete_chatroom(chatroom_id):
    if g.user:
        if chatroom_id is None:
            abort(404)

        db.session.delete(
            Chatroom.query.filter_by(chatroom_id=chatroom_id).first()
        )
        db.session.commit()
        flash("You successfully deleted the chatroom.")
        return redirect(url_for("chatrooms"))
    else:
        abort(404)


@app.route("/enter_chatroom/<chatroom_id>")
def enter_chatroom(chatroom_id):
    if g.user:
        if session.get("current_chatroom") != 0:
            flash("You have been redirected back to your chatroom. Leave the chatroom if you'd like to join another.")
            session["poller_count"] = 0
            session["viewed_message_ids"] = []
            return redirect(url_for("messages", chatroom_id=session.get("current_chatroom")))
        else:
            session["current_chatroom"] = chatroom_id
            return redirect(url_for("messages", chatroom_id=chatroom_id))
    else:
        abort(404)


@app.route("/leave_chatroom")
def leave_chatroom():
    if g.user:
        if session.get("current_chatroom") == 0:
            return redirect(url_for("chatrooms"))
        else:
            session["poller_count"] = 0
            session["current_chatroom"] = 0
            session["viewed_message_ids"] = []
            return redirect(url_for("chatrooms"))
    else:
        abort(404)


@app.route("/logout")
def logout():
    if g.user:
        flash("You were logged out.")
        session.pop("user_id", None)
        session.pop("poller_count", None)
        session.pop("current_chatroom", None)
        session.pop("viewed_messages", None)
        return redirect(url_for("login"))
    else:
        abort(404)


@app.route("/messages/<chatroom_id>", methods=["GET", "POST"])
def messages(chatroom_id):
    if g.user:
        if session.get("current_chatroom") == 0:  # If the user is not currently in a chatroom
            return redirect(url_for("chatrooms"))
        elif session.get("current_chatroom") != chatroom_id:
            flash("You have been redirected back to your chatroom. Leave the chatroom if you'd like to join another.")
            session["poller_count"] = 0
            session["viewed_message_ids"] = []
            return redirect(url_for("messages", chatroom_id=session.get("current_chatroom")))
        else:
            current_time = datetime.now()
            time_format = "%m/%d/%y %H:%M:%S"
            time = current_time.strftime(time_format)

        return render_template("messages.html", author_username=get_username(session["user_id"]),
                               chatroom_id=chatroom_id,
                               chatroom_name=get_chatroom_name(chatroom_id), date_time=time)
    else:
        abort(404)


@app.route("/new_message", methods=["POST"])
def new_message():
    if g.user:
        db.session.add(
            Message(request.form["message_contents"], request.form["date_time"], request.form["chatroom_id"],
                    request.form["author_username"]))
        db.session.commit()

        message = Message.query.filter((Message.message_contents == request.form["message_contents"]) &
                                       (Message.date_time == request.form["date_time"]) &
                                       (Message.chatroom_id == request.form["chatroom_id"]) &
                                       (Message.author_username == request.form["author_username"])).first()

        d = {}

        if message is not None:
            d = {"message_id": message.message_id, "message_contents": message.message_contents,
                 "date_time": message.date_time, "chatroom_id": message.chatroom_id,
                 "author_username": message.author_username}

        return json.dumps(d)
    else:
        abort(404)


@app.route("/register", methods=["GET", "POST"])
def register():
    if g.user:
        abort(404)
    else:
        error_username = ""
        error_password = ""
        if request.method == "POST":
            if not request.form["register-username"]:
                error_username = "You have to enter a username"
            elif request.form["register-username"].__len__() > 24:
                error_username = "The username is too long. Usernames can only be up to 24 characters in length."
            elif not request.form["register-password"]:
                error_password = "You have to enter a password"
            elif request.form["register-password"].__len__() > 24:
                error_password = "The password is too long. Passwords can only be up to 24 characters in length."
            elif get_user_id(request.form["register-username"]) is not None:
                error_username = "The username is already taken"
            else:
                db.session.add(
                    User(request.form["register-username"], request.form["register-password"],
                         generate_password_hash(request.form["register-password"])))
                db.session.commit()
                flash("You were successfully registered and can login now")
                return redirect(url_for("login"))

        return render_template("register.html", error_username=error_username, error_password=error_password)


@app.route("/update_messages/<chatroom_id>")
def update_messages(chatroom_id):
    if g.user:
        redirect_dict_container = []
        q_chatroom_existing = Chatroom.query.filter_by(chatroom_id=chatroom_id).first()

        if q_chatroom_existing is None:
            redirect_dict_container.append("REDIRECT!")
            return json.dumps(redirect_dict_container)

        session_message_id_list = session["viewed_message_ids"]
        # These are all the messages in the specified chatroom
        messages = Message.query.filter_by(chatroom_id=chatroom_id).order_by(
            Message.date_time).all()

        if session.get("poller_count") == 0:  # This indicates that the page has not been polled yet for new messages
            all_message_dicts = []

            if messages is not None:
                for message in messages:
                    d = {"message_id": message.message_id, "message_contents": message.message_contents,
                         "date_time": message.date_time, "chatroom_id": message.chatroom_id,
                         "author_username": message.author_username}
                    all_message_dicts.append(d)
                    session_message_id_list.append(message.message_id)

            session["viewed_message_ids"] = session_message_id_list
            session["poller_count"] = 1
            return json.dumps(all_message_dicts)
        else:  # Else, the page has begun to poll for new messages
            unviewed_messages = []
            unviewed_messages_dicts = []

            flag = False

            for message in messages:
                for message_id in session.get("viewed_message_ids"):
                    if message.message_id == message_id:  # If the message is already shown in the chatroom
                        flag = True
                        break
                if flag is False:
                    unviewed_messages.append(message)
                flag = False

            for message in unviewed_messages:
                d = {"message_id": message.message_id, "message_contents": message.message_contents,
                     "date_time": message.date_time, "chatroom_id": message.chatroom_id,
                     "author_username": message.author_username}

                unviewed_messages_dicts.append(d)
                session_message_id_list.append(message.message_id)

            session["viewed_message_ids"] = session_message_id_list
            return json.dumps(unviewed_messages_dicts)
    else:
        abort(404)
