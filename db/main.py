import sqlite3, os
from flask_login import current_user
import json


def create_dict(cursor, row):
    d = {}
    for idx,col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn = sqlite3.connect('main.db')
conn.row_factory = create_dict


class Initialise:
    def __init__(self) -> None:
        self.conn = sqlite3.connect('main.db')
        self.conn.row_factory = create_dict

    def create_all(self) -> None:
        self.conn.execute(''' CREATE TABLE if not exists USERS
                    (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    firstname TEXT,
                    lastname TEXT,
                    username TEXT,
                    email TEXT,
                    age INT,
                    
                    profile_pic IMAGE,
                    date_joined DATE);''')
        
        self.conn.execute(''' CREATE TABLE if not exists CARDS
                     (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                     title TEXT,
                     description TEXT,

                     userID INT,
                     start DATETIME,
                     duration INT,
                     points, INT,
                     picture IMAGE);''') # creates the cards table
        

        self.conn.execute(''' CREATE TABLE if not exists FRIENDS
                     (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                     userID1 INT,
                     userID2 INT);''') # creates the Friends table
        
        self.conn.execute(''' CREATE TABLE if not exists CARD_RESPONSES
                     (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                     comment TEXT,
                     like INT,
                     cardID INT,
                     userID INT);''') # creates the responses table
        
        self.conn.execute(''' CREATE TABLE if not exists FRIEND_REQUESTS
                     (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                     userID1 INT,
                     userID2 INT);''')
        
        self.conn.execute(''' CREATE TABLE if not exists LEADERBOARDS
                        (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        title TEXT,
                        description TEXT,
                        type TEXT,
                        picture IMAGE);''')
        
        self.conn.execute(''' CREATE TABLE if not exists RANKINGS
                        (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        leaderboardID INT,
                        userID INT,
                        position INT,
                        info TEXT,
                        duration INT);''')

        self.conn.commit()



class Users:
    def __init__(self) -> None:
        self.conn = sqlite3.connect('main.db')
        self.conn.row_factory = create_dict

    def get_username_by_id(self, userID):
        username = self.conn.execute("SELECT username FROM Users WHERE ID = ?;", [userID])
        return username.fetchone()['username']
    
    def get_username_by_card_id(self, cardID):
        username = self.conn.execute('''SELECT username FROM Cards
                                INNER JOIN Users ON Users.ID = Cards.userID
                                WHERE Cards.ID = ?''', [cardID])
        return username.fetchone()['username']
    
    def get_id_by_username(self, username):
        username = self.conn.execute("SELECT ID FROM Users WHERE username = ?;", [username])
        return username.fetchone()['ID']
        

class Cards:
    def __init__(self) -> None:
        self.conn = sqlite3.connect('main.db')
        self.conn.row_factory = create_dict

    def add_new_card(self, title, desc, userID, duration, points, pic, start, address): # will add a new card to the table
        self.conn.execute('''INSERT INTO Cards(title, description, userID, start, duration, points, picture, address) 
                          VALUES(?, ?, ?, ?, ?, ?, ?, ?)''', [title, desc, userID, start, duration, points, pic, address])
        self.conn.commit()


    def get_cards_of_frds(self, userID):  # calls function that returns a list of the ids of a user's friends
        total_cards = []                  # then will join up lists of dicts representing cards and return that 
        for i in Friends().get_friends_ids(userID):
            cards = self.conn.execute('''SELECT *, Cards.ID AS IDD, Users.ID AS uID FROM Cards
                                    INNER JOIN Users ON Cards.userID = Users.ID
                                    WHERE Cards.userID = ?;''', [i["ID"]])
                    
            total_cards.extend(cards.fetchall())
        # print(i)
            

        # now I need to add the cards belonging to the current user
        cards = self.conn.execute('''SELECT *, Cards.ID AS IDD, Users.ID AS uID FROM Cards
                                    INNER JOIN Users ON Cards.userID = Users.ID
                                    WHERE Cards.userID = ?;''', [userID])
        total_cards.extend(cards.fetchall())
        
        total_cards = sorted(total_cards, key=lambda x: x["start"], reverse=True) # sorts cards based on reversed date
        
        for i in total_cards:
            i['likes'] = Card_responses().get_likes(i['IDD'])
        # print(total_cards)
        return total_cards
    
    def get_card_by_id(self, cardID):
        card = self.conn.execute('''SELECT * FROM Cards
                                 WHERE ID = ?;''', [cardID])
        data = card.fetchone()
        data['likes'] = Card_responses().get_likes(cardID)
        return data
    
    def get_cards_of_user(self, userID):
        cards = self.conn.execute('''SELECT *, Cards.ID AS IDD, Users.ID AS uID FROM Cards
                                    INNER JOIN Users ON Cards.userID = Users.ID
                                    WHERE Cards.userID = ?;''', [userID]).fetchall()
        for i in cards:
            i['likes'] = Card_responses().get_likes(i['IDD'])

        cards = sorted(cards, key=lambda x: x["start"], reverse=True) # sorts cards based on reversed date

        return cards
    
    def delete_all(self, userID):
        cards = self.conn.execute('''DELETE FROM Cards WHERE userID = ?''', [userID]).fetchall()
        self.conn.commit()
        


class Friends:
    def __init__(self) -> None:
        self.conn = sqlite3.connect('main.db')
        self.conn.row_factory = create_dict # defines the format of fetchall() statements

    def add_new_friend(self, userID, userID2):
        self.conn.execute("INSERT INTO Friends(userID1, userID2) VALUES(?, ?)", [userID, userID2])
        self.conn.commit() # adds a new row into the table

    def get_friends_ids(self, userID): # returns the ids of friends of a given user
        ids = self.conn.execute('''SELECT Users.ID FROM Friends
                    INNER JOIN Users ON Users.ID = Friends.userID2
                    WHERE Friends.userID1 = ?;''', [userID])
        # print(ids.fetchall())
        return ids.fetchall()
    
    def get_friends_of_friends(self, userID):
        frds = self.conn.execute('''SELECT Users.ID, username, firstname, lastname FROM Friends
                    INNER JOIN Users ON Users.ID = Friends.userID2
                    WHERE Friends.userID1 = ?;''', [userID]) # generates a list of friends
        
        total = []

        temp = []
        f = frds.fetchall()
        for i in f:
            temp = self.conn.execute('''SELECT Users.ID, username, firstname, lastname FROM Friends
                    INNER JOIN Users ON Users.ID = Friends.userID2
                    WHERE Friends.userID1 = ?;''', [i['ID']]).fetchall()
            # add users from temp into total where they don't conflict with the requirements for a 
            # suggested friend i.e. a current friend, already in the list, the user themself
            total.extend([x for x in temp if not x in total and x['ID'] != userID and x not in f])

        # print(total)
        return total
    
    def get_friends(self, userID):
        frds = self.conn.execute('''SELECT Users.ID, username, firstname, lastname FROM Friends
                    INNER JOIN Users ON Users.ID = Friends.userID2
                    WHERE Friends.userID1 = ?;''', [userID])
        
        f = frds.fetchall()
        return f
    
    def remove_friend(self, userID, friendID):
        x = self.conn.execute('''DELETE FROM Friends WHERE Friends.userID1 = ? AND Friends.userID2 = ?''', [userID, friendID])
        self.conn.commit()

    
    def get_friend_by_username(self, username):
        friends = self.conn.execute('''SELECT ID, username, firstname, lastname FROM Users
                    WHERE username = ?;''', [username.lower()]).fetchall()
        
        pre_existing = self.get_friends(current_user.id)
        return [x for x in friends if not x in pre_existing]
    
    def get_friend_by_id(self, frdID):
        friend = self.conn.execute('''SELECT ID, username, firstname, lastname FROM Users
                    WHERE ID = ?;''', [frdID]).fetchone()
        
        
        return friend

class Card_responses:
    def __init__(self) -> None:
        self.conn = sqlite3.connect('main.db')
        self.conn.row_factory = create_dict

    def get_chats(self, cardID): # checks if there is actually a comment before returning it
        chats = self.conn.execute('''SELECT comment, username, Users.ID FROM Card_responses
                        INNER JOIN Users ON Users.ID = Card_responses.userID
                        WHERE Card_responses.comment is not NULL
                        AND Card_responses.cardID = ?''', [cardID])
        return chats.fetchall()[::-1] # sorts the chats from the oldest to newest
        

    def add_new_chat(self, chat, cardID, userID):
        if chat and cardID and userID:
            self.conn.execute("INSERT INTO Card_responses(comment, cardID, userID) VALUES(?, ?, ?)", [chat, cardID, userID])
            self.conn.commit()


    def get_likes(self, cardID):
        likes = self.conn.execute('''SELECT username, Users.ID FROM Card_responses
                        INNER JOIN Users ON Users.ID = Card_responses.userID
                        WHERE Card_responses.comment is NULL
                        AND Card_responses.cardID = ?''', [cardID]).fetchall()
        
        return len(likes)

    def get_likes_from_user(self, cardID, userID):
        likes = self.conn.execute('''SELECT username, Users.ID FROM Card_responses
                        INNER JOIN Users ON Users.ID = Card_responses.userID
                        WHERE Card_responses.comment is NULL
                        AND Card_responses.cardID = ?
                        AND Users.ID = ?''', [cardID, userID]).fetchall()
        return likes
        

    
    def add_like(self, cardID, userID):
        if not len(self.get_likes_from_user(cardID, userID)): # checks if the user has already liked the card
            self.conn.execute("INSERT INTO Card_responses(like, cardID, userID) VALUES(?, ?, ?)", [1, cardID, userID])
        
        else: # if the user has liked the card, then this will delete that like
            self.conn.execute('''DELETE FROM Card_responses WHERE Card_responses.comment is NULL
                              AND cardID = ?
                              AND userID = ?''', [cardID, userID])
        
        self.conn.commit()



class Leaderboards:
    def __init__(self) -> None:
        self.conn = sqlite3.connect('main.db')
        self.conn.row_factory = create_dict

    def generate_table(self, leaderboardID):
        headers = self.conn.execute('''SELECT headers, title FROM LEADERBOARDS
                        WHERE ID = ?;''', [leaderboardID]).fetchone()
        # print(headers)
        
        
        
        rows = self.conn.execute('''SELECT position, username, info, duration FROM Rankings 
                        INNER JOIN Users ON Users.ID = Rankings.userID
                        WHERE Rankings.leaderboardID = ?
                        ORDER BY Rankings.position ASC;''', [leaderboardID]).fetchall()
        
        return headers['title'], headers['headers'].split(','), rows
    
    def get_tables_for_form(self, userID):
        tables = self.conn.execute('''SELECT Leaderboards.ID, title, description, type, position FROM Rankings
                        INNER JOIN Users ON Users.ID  = Rankings.userID
                        INNER JOIN Leaderboards ON Leaderboards.ID = Rankings.leaderboardID
                        WHERE Users.ID = ?;''', [userID])
        
        return tables.fetchall()
    

    def generate_leaderboard_time_based(self, userID):

        cards = self.conn.execute('''SELECT 
                        DENSE_RANK() OVER (ORDER BY SUM(CARDS.duration) DESC) AS rank,
                        USERS.username, 
                        SUM(CARDS.duration) AS tTime
                        
                                  
                        FROM CARDS
                        LEFT JOIN USERS ON CARDS.userID = USERS.ID
                        LEFT JOIN FRIENDS ON CARDS.userID = FRIENDS.userID2 AND FRIENDS.userID1 = ?
                        WHERE FRIENDS.userID2 IS NOT NULL OR CARDS.userID = ?
                        GROUP BY CARDS.userID
                        ORDER BY tTime DESC;''', [userID, userID])
        return cards.fetchall()
    
    

class Progress:
    def __init__(self) -> None:
        self.conn = sqlite3.connect('main.db')
        self.conn.row_factory = create_dict

    def get_workouts(self): # generates the array of cards from the database
        cards = self.conn.execute('''SELECT ID, start, duration, points, title FROM Cards
                        WHERE userID = ?''', [current_user.id]).fetchmany(100) 

        # print([x['start'][:10] for x in cards])
        # now I'm going to order them

        cards = sorted(cards, key=lambda x: x["start"])[-8:]
        return cards

    def get_friends_workouts(self, id=0):
        if not id:  return []

        cards = self.conn.execute('''SELECT ID, start, duration, points, title FROM Cards
                        WHERE userID = ?''', [id]).fetchmany(100) 

        # print([x['start'][:10] for x in cards])
        # now I'm going to order them

        cards = sorted(cards, key=lambda x: x["start"])[-8:]
        return cards
    


class Settings:
    def __init__(self) -> None:
        self.conn = sqlite3.connect('main.db') # connects to the database
        self.conn.row_factory = create_dict

    def get_data(self, userID):
        cards = self.conn.execute('''SELECT * FROM Cards
                        WHERE userID = ?''', [userID]).fetchall() # selects the cards
        user = self.conn.execute('''SELECT * FROM Users
                        WHERE ID = ?''', [userID]).fetchone() # the user details
        friends = self.conn.execute('''SELECT * FROM Friends
                        WHERE userID1 = ?''', [userID]).fetchall() # the user's friends
        comments = self.conn.execute('''SELECT * FROM Card_responses
                        Where userID = ?''', [userID]).fetchall() # the responses of the user
        

        account = {'cards': cards, 'user': user, 'friends': friends, 'responses': comments}
        # print(account)

        # a = open('test_dump.txt', 'w')
        # a.write(json.dumps(account, indent=4, ensure_ascii=True))
        # a.close()

        return json.dumps(account, indent=4, ensure_ascii=True)
    

    def delete_account(self, userID):
        command = self.conn.execute('''UPDATE Users
                        SET firstname = '[deleted]', lastname = '[user]', username = '[deleted-user]', email = '',
                        password = '[]'
                        WHERE ID = ?''', [userID])
        
        self.conn.commit()
        


# Initialise().create_all()
# Friends().add_new_card(1, 2)
# Users().add_new_user("yob", "waring", "yowaring", "yo@outlook.com", 18, "no", "nomr")
# print(Friends().get_friends_ids(1))

# print(Cards().get_cards_of_frds(-1))

# print(Cards().get_card_by_id(0))
# Card_responses().add_like(3, 1)
# print(Card_responses().get_chats(1))
# print(Users().get_username_by_card_id(3))
# print(Friends().get_friends_ids(2))

# print(Card_responses().get_likes(23))

# Card_responses().add_new_chat('hello from the other side', 1, 1)

# Friends().get_friend_by_username('whyhy')
# print(Leaderboards().generate_table(1))
# print(Leaderboards().get_tables_for_form(1))
# print(Friends().get_friends(1))
# print(Friends().get_friends_of_friends(1))


# print(Progress().get_workouts())
# Card_responses().get_likes_from_user(11, 4)
# print(Leaderboards().generate_leaderboard_time_based(1))

# Settings().get_data(0)
# Settings().delete_account(16)