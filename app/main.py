from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
import db.main
import json

main = Blueprint('main', __name__)

def get_cards(id):
    cards = db.main.Cards().get_cards_of_frds(id)
    return cards

# Homepages

@main.route('/')
def index():
    if current_user.is_authenticated:
        # print(current_user.id)
        # print(get_cards(current_user.id))

        a = render_template("mainpages/home.html", cards = get_cards(current_user.id))
        return a
    else:
        return render_template('user/index.html')


@main.route("/home")
@login_required
def homepage():
    # print(current_user.id)
    # print(get_cards(current_user.id))
    a = render_template("mainpages/home.html", cards = get_cards(current_user.id))
    return a


@main.route("/home", methods=['POST'])
@main.route('/', methods=['POST'])
@login_required
def home_post():
    title = request.form.get('title')
    description = request.form.get('description')
    time = request.form.get('time')
    duration = request.form.get('duration')
    address = request.form.get('address')
    difficulty = request.form.get('difficulty')

    db.main.Cards().add_new_card(title, description, current_user.id, duration, difficulty, 0, time, address)
    return redirect(url_for('main.index'))


@main.route("/addLike", methods=['POST'])
@login_required
def add_like():
    data = json.loads(request.data) # loads the data that was posted
    db.main.Card_responses().add_like(data['cardID'], current_user.id) # sends the cardID and userID
    return '' # returns an empty string



# Chat page



@main.route("/chat/<int:cardID>") # whatever int comes after "chat/" gets passed in
@login_required
def card_chat(cardID): 
    # print(db.main.Cards().get_card_by_id(cardID))
    return render_template("chat.html", item = db.main.Cards().get_card_by_id(cardID), 
                           chats=db.main.Card_responses().get_chats(cardID), username=db.main.Users().get_username_by_card_id(cardID))


@main.route("/chat/<int:cardID>", methods=['POST'])
@login_required
def new_chat_post(cardID):
    chat_content = request.form.get('chat') # gets the text entered in the input box
    if chat_content.strip() != '':
        db.main.Card_responses().add_new_chat(chat_content, cardID, current_user.id)
    return redirect(url_for('main.card_chat', cardID=cardID)) # reloads the page



# Friends page



@main.route("/friends")
@login_required
def friends():
    a = render_template("mainpages/friends.html", 
                        suggested = db.main.Friends().get_friends_of_friends(current_user.id),
                        friends= db.main.Friends().get_friends(current_user.id))
    return a


@main.route("/friends", methods=['POST'])
@login_required
def friends_post():
    username = request.form.get('username')
    potential = db.main.Friends().get_friend_by_username(username)
    a = render_template("potentials.html", potentials = potential)
    return a
    

# @main.route("/p")
# def test_p():
#     potential = db.main.Friends().get_friend_by_username('whyhy')
#     a = render_template("potentials.html", potentials = potential)
#     return a


@main.route("/addFriend", methods=['POST'])
@login_required
def add_new_friend():
    data = json.loads(request.data) # loads the data
    friendID = data['friendID'] # checks if the friend the user wants to add is already a friend
    if not friendID in [x['ID'] for x in db.main.Friends().get_friends_ids(current_user.id)]: 
        db.main.Friends().add_new_friend(current_user.id, friendID)

    return redirect(url_for('main.friends'))


@main.route("/removeFriend", methods=['POST'])
@login_required
def remove_friend():
    data = json.loads(request.data) # loads the data
    friendID = data['friendID']
    # ensures that the friendship exists in the first place to aviod errors
    if friendID in [x['ID'] for x in db.main.Friends().get_friends_ids(current_user.id)]: 
        db.main.Friends().remove_friend(current_user.id, friendID)
        
    return redirect(url_for('main.friends'))



# Progress page



@main.route("/progress")
@login_required
def progress():
    a = render_template("mainpages/progress/progress.html", 
                        cards=db.main.Cards().get_cards_of_user(current_user.id))
    return a


@main.route("/api/cards")
@login_required
def get_api_cards():
    cards = db.main.Progress().get_workouts()
    return jsonify(cards)


@main.route("/api/cards/<int:ID>")
@login_required
def api_cards(ID):
    cards = db.main.Progress().get_friends_workouts(ID)
    return jsonify(cards)

@main.route("/api/cardfilter")
@login_required
def api_card_filt():
    cards=db.main.Cards().get_cards_of_user(current_user.id)
    return jsonify(cards)


# Leaderboards page



@main.route("/leaderboards")
@login_required
def leaderboard():
    a = render_template("mainpages/leaderboards.html", leaderboardID = 1)
    return a


@main.route("/leaderboard_frame/<int:leaderboardID>")
@login_required
def table(leaderboardID):
    title = "Total time spent training"
    headers = ['Rank', 'User', 'Time']
    rows = db.main.Leaderboards().generate_leaderboard_time_based(current_user.id)

    return render_template("mainpages/leaderboard_frame.html", leaderboardID = leaderboardID, 
                           headings = headers, rows = rows, title = title)


# Settings page


@main.route("/settings")
@login_required
def settings(): # this ensures the user is logged in, and will return the settings.html page
    a = render_template("mainpages/settings/settings.html")
    return a

@main.route("/manage")
@login_required
def manage():
    return render_template("mainpages/settings/manage.html", account_data = db.main.Settings().get_data(current_user.id))



@main.route("/delete-workouts")
def delete_workouts():
    db.main.Cards().delete_all(current_user.id)
    return ''

@main.route("/confirm")
def confirm_end_of_account():
    print('its deleted')
    db.main.Settings().delete_account(current_user.id)
    return ''



@main.route("/test")
def test():
    return render_template("test.html", account_data = db.main.Settings().get_data(1))



@main.route('/profile/<int:userID>')
@login_required
def profile(userID):
    return render_template('mainpages/profile/profile.html', id=userID, frd=db.main.Friends().get_friend_by_id(userID), 
                           cards=db.main.Cards().get_cards_of_user(userID))


