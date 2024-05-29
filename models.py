'''
models
defines sql alchemy data models
also contains the definition for the room class used to keep track of socket.io rooms

Just a sidenote, using SQLAlchemy is a pain. If you want to go above and beyond, 
do this whole project in Node.js + Express and use Prisma instead, 
Prisma docs also looks so much better in comparison

or use SQLite, if you're not into fancy ORMs (but be mindful of Injection attacks :) )
'''

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Dict, List

# data models
class Base(DeclarativeBase):
    pass

# model to store user information
class User(Base):
    __tablename__ = "user"
    
    # looks complicated but basically means
    # I want a username column of type string,
    # and I want this column to be my primary key
    # then accessing john.username -> will give me some data of type string
    # in other words we've mapped the username Python object property to an SQL column of type String 
    username: Mapped[str] = mapped_column(String, primary_key=True)
    password: Mapped[str] = mapped_column(String)
    

# stateful counter used to generate the room id
class Counter():
    def __init__(self):
        self.counter = 0
    
    def get(self):
        self.counter += 1
        return self.counter

# Room class, used to keep track of which username is in which room
class Room():
    def __init__(self):
        self.counter = Counter()
        # dictionary that maps the username to the room id
        # for example self.dict["John"] -> gives you the room id of 
        # the room where John is in
        self.dict: Dict[str, int] = {}
        # stores all users (key) and their associated rooms (value)
        self.user_room_history: Dict[str, List[int]] = {}

    # going to try and test creating a room where only the sender is appended to dictionary
    # def create_room(self, sender: str, receiver: str) -> int: - old definition
    def create_room(self, sender: str, receiver: str) -> int:
        previous_room = self.get_previous_room(sender, receiver)
        if previous_room is not None:
            self.dict[sender] = previous_room
            return previous_room
        else:
            room_id = self.counter.get()
            self.dict[sender] = room_id
            self.update_history(sender, room_id)
            return room_id
    
    def join_room(self,  sender: str, room_id: int) -> int:
        self.dict[sender] = room_id
        self.update_history(sender, room_id)

    def leave_room(self, user):
        if user not in self.dict.keys():
            return
        del self.dict[user]

    # gets the room id from a user
    def get_room_id(self, user: str):
        if user not in self.dict.keys():
            return None
        return self.dict[user]
    
    def update_history(self, user: str, room_id: int):
        if user not in self.user_room_history:
            self.user_room_history[user] = [room_id]
        else:
            self.user_room_history[user].append(room_id)
    
    def get_previous_room(self, user1: str, user2: str):
        user1_history = self.user_room_history.get(user1, [])
        user2_history = self.user_room_history.get(user2, [])
        for room_id_1 in user1_history:
            for room_id_2 in user2_history:
                if room_id_1 == room_id_2:
                    return room_id_1

        return None
    
class Friendship(Base):
    __tablename__ = "friendship"

    # user_id is username
    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    friend_id: Mapped[str] = mapped_column(String, primary_key=True)
    status: Mapped[str] = mapped_column(String)  # "pending", "accepted", or "rejected"

class Message(Base):
    __tablename__ = 'messages'
    
    id: Mapped[str] = mapped_column(Integer, primary_key=True, autoincrement="auto")
    room_id: Mapped[int] = mapped_column(Integer)
    storer: Mapped[String] = mapped_column(String)
    encrypted_content: Mapped[str] = mapped_column(String)  
