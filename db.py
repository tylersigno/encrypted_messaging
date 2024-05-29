'''
db
database file, containing all the logic to interface with the sql database
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import *

from pathlib import Path

# creates the database directory
Path("database") \
    .mkdir(exist_ok=True)

# "database/main.db" specifies the database file
# change it if you wish
# turn echo = True to display the sql output
engine = create_engine("sqlite:///database/main.db", echo=False)

# initializes the database
Base.metadata.create_all(engine)

# inserts a user to the database
def insert_user(username: str, password: str):
    with Session(engine) as session:
        user = User(username=username, password=password)
        session.add(user)
        session.commit()

# gets a user from the database
def get_user(username: str):
    with Session(engine) as session:
        return session.get(User, username)
    
# Adds a friend to the user
# def add_friend(user_id: str, friend_id: str, status: str = "pending"):
#     with Session(engine) as session:
#         friendship = Friendship(user_id=user_id, friend_id=friend_id, status=status)
#         session.add(friendship)
#         session.commit()

# Retrieves a list of friends for the user
def get_friends(user_id: str):
    # with Session(engine) as session:
    #     friendships = session.query(Friendship).filter(
    #         (Friendship.user_id == user_id) & (Friendship.status == "accepted")).all()
    #     return [friendship.friend_id for friendship in friendships]
    with Session(engine) as session:
        # Retrieve friendships where the user is either the sender or receiver
        friendships = session.query(Friendship).filter(
            (Friendship.user_id == user_id) | (Friendship.friend_id == user_id)
        ).filter(
            Friendship.status == "accepted"
        ).all()

        # Create a list of friends' usernames
        friends = []
        for friendship in friendships:
            if friendship.user_id == user_id:
                friends.append(friendship.friend_id)
            else:
                friends.append(friendship.user_id)
        
        return friends
    
def is_friend(user_id: str, friend_id: str):
    with Session(engine) as session:
        friendship = session.query(Friendship).filter(
            (Friendship.user_id == user_id) & (Friendship.friend_id == friend_id) | 
            (Friendship.user_id == friend_id) & (Friendship.friend_id == user_id)
        ).first()
        return friendship is not None
    
def send_friend_request(user_id: str, friend_id: str, status: str = "pending"):
    with Session(engine) as session:
        request = Friendship(user_id=user_id, friend_id=friend_id, status=status)
        session.add(request)
        session.commit()

def get_friend_requests(user_id: str):
    with Session(engine) as session:
        requests = session.query(Friendship).filter(
            (Friendship.friend_id == user_id) & (Friendship.status == "pending")
        ).all()
        return requests
    
def get_sent_friend_requests(user_id: str):
    with Session(engine) as session:
        requests = session.query(Friendship).filter(
            (Friendship.user_id == user_id) & (Friendship.status == "pending")
        ).all()
        return requests

def update_friend_request_status(user_id: str, friend_id: str, status: str):
    with Session(engine) as session:
        request = session.query(Friendship).filter(
            (Friendship.user_id == user_id) & (Friendship.friend_id == friend_id)
        ).first()
        if request:
            request.status = status
            session.commit()

def store_encrypted_message(room_id, encrypted_message, username):
    with Session(engine) as session:
        new_message = Message(room_id=room_id, encrypted_content=encrypted_message, storer=username)
        session.add(new_message)
        session.commit()

def retrieve_encrypted_messages(username, room_id):
    with Session(engine) as session:
        
        messages = session.query(Message).filter(
            (Message.storer == username) & (Message.room_id == room_id)
        ).all()
        return [msg.encrypted_content for msg in messages]


