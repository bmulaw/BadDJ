from flask import Flask, jsonify, request, Response, render_template, redirect
from flask_cors import CORS, cross_origin
from flask_pymongo import PyMongo
import flask_login

import json
from urllib.parse import quote
import requests
import os
import last_fm_similarity
from dotenv import load_dotenv
from bson import json_util

from user import User

load_dotenv()

app = Flask(__name__)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

app.config["MONGO_URI"] = "mongodb://localhost:27017/BadDJDatabase"
app.config["SECRET_KEY"] = "supersecretkey"
mongo = PyMongo(app)


CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

domain = 'localhost:8080'
AUTH_URL = 'https://accounts.spotify.com/api/token'
REFRESH_URL = 'https://accounts.spotify.com/api/token'
USER_AUTH_URL = 'https://accounts.spotify.com/authorize?client_id=2c8231fad0534937afacccb8a7942d5f&response_type=code&redirect_uri=https://' + domain + '/spotifyAuthCallback&scope=user-read-private user-read-email&state=34fFs29kd09'
USER_ACCESS_URL = 'https://accounts.spotify.com/api/token'


# ========================= OAUTH SETUP ====================================== #

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 8080
REDIRECT_URI = "{}:{}/callback".format(CLIENT_SIDE_URL, PORT)
SCOPE = "playlist-modify-public playlist-modify-private"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()
auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}

stored_auths = {};

# ======================================== TOKENS ===================================== #

def getAccessToken():
    # POST
    auth_response = requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    })

    # convert the response to JSON
    auth_response_data = auth_response.json()
    # save the access token
    access_token = auth_response_data['access_token']
    refresh_token = None
    if 'refresh_token' in auth_response_data.keys():
        refresh_token = auth_response_data['refresh_token']
    return {'access_token': access_token, 'refresh_token': refresh_token}

@app.route('/spotifyAuthCallback', methods=['GET'])
def handleSpotifyAuthCallback():
    # TODO: Implement
    auth_code = request.params['code']
    access_response = requests.post(USER_ACCESS_URL, {
        
    })
    return

def getUserAccessToken():
    # TODO: The user needs to be redirected to the spotify URL to authorize the application...
    # TODO: Get access / refresh tokens from the auth token
    return {'access_token': None, 'refresh_token': None}

def refreshUserToken(tokens):
    return refreshToken(tokens, getUserAccessToken)

def refreshToken(tokens, getNewTokens=getAccessToken):
    # First, check to see if we have a refresh token, if not we'll just get a new one the normal way
    if tokens['refresh_token'] == None:
        return getNewTokens()
    # Request a refresh of the token
    refresh_response = requests.post(REFRESH_URL, {
        'grant_type': 'refresh_token',
        'refresh_token': tokens['refresh_token'],
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    })
    # Parse the data
    refresh_response_data = refresh_response.json()
    access_token = refresh_response_data['access_token']
    refresh_token = None
    if 'refresh_token' in refresh_response_data.keys():
        refresh_token = refresh_response_data['refresh_token']
    # And return it
    return {'access_token':access_token,'refresh_token':refresh_token}

tokens = getAccessToken()
access_token = tokens['access_token']
refresh_token = tokens['refresh_token']
tokens = refreshToken(tokens)


# ================================ FLASK SESSIONS ===================================== #

@login_manager.user_loader
def load_user(user_id):
    print("user loader")
    users = mongo.db.users.find_one({"id":user_id})
    if not users:
        return 
    user = User(user_id, stored_auths[user_id])
    return user

def isUnique(user_id):
    user = mongo.db.users.find_one({"id":user_id})
    if user:
        return False
    return True

# ============================ OAUTH ================================= #
@app.route("/callback", methods=["POST"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def callbackv2():
    print("Callback was called!")
    access_token = request.get_json().get("token")

    # Auth Step 6: Use the access token to access Spotify API
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}

    # Get profile data
    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
    profile_data = json.loads(profile_response.text)
    stored_auths[profile_data["id"]] = authorization_header

    # Get user playlist data
    playlist_api_endpoint = "{}/playlists".format(profile_data["href"])
    playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
    playlist_data = json.loads(playlists_response.text)

    # Combine profile and playlist data to display
    display_arr = [profile_data] + playlist_data["items"]

    user = User(profile_data["id"], authorization_header)
    flask_login.login_user(user)
    # dont add every time
    if isUnique(profile_data["id"]):
        user_db_id = mongo.db.users.insert(profile_data)
        data = {"id":profile_data["id"], "playlists":playlist_data["items"]}
        mongo.db.playlists.insert(data)
    return jsonify(json.dumps([profile_data]))
# =============================================================== #

@app.route("/getProfile", methods=["GET"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@flask_login.login_required
def getProfile():
    user_id = flask_login.current_user.user_id
    user = mongo.db.users.find_one({"id":user_id})
    playlist = mongo.db.playlists.find_one({"id":user_id})
    print(user, playlist)
    return json.loads(json_util.dumps(user))


@app.route("/notifications", methods=["GET"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@flask_login.login_required
def notifications():
    user_id = flask_login.current_user.user_id
    notifications = [x for x in mongo.db.notifications.aggregate([{"$match": {"user_id": user_id}}, {"$sort": {"timestamp": -1}}])]
    return jsonify(notifications)

@app.route("/friends/recommendations")
@flask_login.login_required
def get_friend_recommendations():
    user_id = flask_login.current_user.user_id
    friend_recommendations = last_fm_similarity.getSimilarUsers(mongo, flask_login.current_user, True)
    friend_recommendations = [{"user_id": user_id, "similarity_score": similarity_score} for (user_id, similarity_score) in friend_recommendations if not user_is_friends_with(user_id, x)]
    return jsonify(friend_recommendations)

@app.route("/friends")
@flask_login.login_required
def get_friends():
    user_id = flask_login.current_user.user_id
    return [x.friend_user_id for x in mongo.db.friends.find({"user_id": user_id}, {"_id":0, "friend_user_id": 1})]

@app.route("/friends/add")
@flask_login.login_required
def add_friend():
    user_id = flask_login.current_user.user_id
    friend_user_id = request.args["friend_user_id"]
    mongo.db.friends.insert({"user_id": user_id, "friend_user_id": friend_user_id})
    return ('', 204)

@app.route("/friends/remove")
@flask_login.login_required
def remove_friend():
    user_id = flask_login.current_user.user_id
    friend_user_id = request.args["friend_user_id"]
    mongo.db.friends.remove({"user_id": user_id, "friend_user_id": friend_user_id})
    return ('', 204)
	
@app.route("/notification_button_pressed")
@flask_login.login_required
def notification_button_pressed():
    # TODO: consider doing something other than just removing the notification here
    user_id = flask_login.current_user.user_id
    notification_id = request.args["notification_id"]
    mongo.db.notifications.remove({"user_id": user_id, "notification_id": notification_id})
    return ('', 204)

@app.route("/test_authme")
def test_authme():
    authorization_header = {"Authorization": "Bearer {}".format("BQCP_dEU0x2SVMFPCZ8RexjBSfjez48CFgwfF3cRLG4mv-zb3bRK6S1ZZHS7AKE_1aMTOdScym2XuL7PA3M84GGAZ2aypZWvNMxXlCxIgn80Rc-_Ki415r3KjI3sNxSlUXXjeBrayD0H5Hu3080vB6JpbryuBva1MEfJNXyCniv6iD480TfnVaQticWow2Y6jIgIEnreXU7rPY4")}
    user = User("f1sh3", authorization_header)
    stored_auths[user.user_id] = authorization_header;
    flask_login.login_user(user)
    return ('', 204)
    
def user_is_friends_with(user_id, friend_user_id):
    return mongo.db.friends.find({"user_id": user_id, "friend_user_id": friend_user_id}).length > 0

def send_notification(user_id, text, type):
    timestamp = time.time_ns() // 1_000_000
    mongo.db.notifications.insert({"user_id": user_id, "text": text, "type": type, "timestamp": timestamp})
    return ('', 204)

@app.route("/test")
def test():
    return "{\"test\":1}"

if __name__ == "__main__":
    app.run(port=PORT, debug=True)
