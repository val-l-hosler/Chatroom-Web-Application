# Chatroom-Web-Application

This is a project from CS 1520, Programming Languages for Web Applications. I created a chatroom web application where a user can create an account, create/delete chatrooms, and participate in said chatrooms. 

Though the project description did not require extensive styling or responsivity, I tried to make the web application as neat and user-friendly as possible. Though the project description did not require extensive styling or responsivity, I tried to make the web application as neat and user-friendly as possible. **However, it is not 100% responsive, as the web application only needed to be viewable on a desktop browser**.

### :point_right: Visit the [following url](http://valhos.pythonanywhere.com/) to view a live demo.

### :warning: The script is located in [templates/messages.html](https://github.com/val-l-hosler/Chatroom-Web-Application/blob/main/templates/messages.html) because I set the id variable's value to the chatroom_id via Jinja formatting.

### 🧰 Tech Stack 
1. CSS (including Flexbox)
2. Flask
3. HTML
4. JavaScript (ES6) (including the fetch API)
5. JSON
6. Jinja
7. Python
8. SQLAlchemy

### :memo: The project had the following specifications:

1. You must build your website using JavaScript, JSON, `fetch`, Python, Flask,
	SQLAlchemy, and the Flask-SQLAlchemy extension.

2. When visiting the page for the first time, users should be given the chance
	to create an account or login.

3. Once successfully logged in, the user should be given a list of possible
	chat rooms to join, or a message stating that none currently exist.  The
	user should also have the option to create a new chat room.

4. Once in a chat room, the user should be shown the history of messages for
	that chat room, as well as be kept up to date as messages are sent to the
	chat room. The user should also have the option to post a new message to
	the chat room. The user should further be given a way to leave the chat
	room.

	* Users can be in only one chat room at a time.
	* You must use `fetch` to retrieve update the list of messages posted to the
	  chat room (as JSON), and to post new messages to the chat room.
	* All AJAX chat updates should send only *new* messages to the user.  The
	  user should not receive the full list of chat messages with every AJAX
	  update as this could grow quite large over time.
	* You must be sure that your application does not display "phantom"
	  messages to the user.
		* I.e., All users in the same chat room should see the same messages in
		  the same order and new messages should always appear at the end of
		  the chat log, never in the middle of the chat log.
	* You should take a polling approach to ensure that new messages are always
	  available to the user. Your application should have a 1 second time
	  between polls.

5. Once a user leaves the chat room, they should again be shown a list of
	potential chat rooms to join (or a message if none exist).

	* The user should also have the option to delete any chat rooms that they
	  created.
		* Any users still in a room when it is deleted should be shown a
		  message informing them that the room was deleted and be again
		  presented with the list of available chat rooms (or a message if none
		  exist).
		  
6. The user should always (on every page) be presented with away to log out
	while they are logged in.

7. All data for your application should be stored in an SQLite database named
	`chat.db` using SQLAlchemy's ORM and the Flask-SQLAlchemy extension.

<em>Note: The project specifications were written by my professor, Dr. Farnan.</em>
