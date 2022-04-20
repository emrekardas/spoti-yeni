from ssl import SSLSocket
from xml.etree.ElementTree import TreeBuilder
from flask import Flask, render_template, redirect, request, session, make_response, session, redirect
from importlib_metadata import method_cache
import spotipy
import spotipy.util as util
import time
import json

app = Flask(__name__)

app.secret_key = "xjFXOlpiWg"

API_BASE = 'https://accounts.spotify.com'

REDIRECT_URI = "http://127.0.0.1:5000/index.html/"
CLIENT_ID = "9a109132005f4401a3264ff8fd79eee5"
CLIENT_SECRET = "68f551b40e06445eb326e2e78e457a7e"
# Spotify Developer Docs Authorization Scopes
SCOPE = 'user-read-recently-played,user-read-playback-position,playlist-read-collaborative,user-library-read,user-read-currently-playing'

# TEST
SHOW_DIALOG = True

# authorization-code-flow Adım 1. Authorization için Request adımı
# Kullanıcı girişi ve Authorization yetkisi
@app.route("/")
def verify():
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = CLIENT_ID , client_secret = CLIENT_SECRET, redirect_uri = REDIRECT_URI, scope = SCOPE)
    auth_url = sp_oauth.get_authorize_url()
    print(auth_url)
    return redirect(auth_url)

@app.route("/index")
def index():
    return render_template("index.html")

# authorization-code-flow Adım 2.
# Refresh ve Access tokenları çağırma
@app.route("/callback")
def callback():
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = CLIENT_ID , client_secret = CLIENT_SECRET, redirect_uri = REDIRECT_URI, scope = SCOPE)
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)

    session["token_info"] = token_info
    return redirect("index")

# authorization-code-flow Adım 3.
# Spotify Web API'sine erişim.
@app.route("/go", methods = ['POST'])
def go():
    session['token_info'], authorized = get_token(session)
    session.modified = True
    if not authorized:
        return redirect ('/')
    data = request.form
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    response = sp.current_user_top_tracks(limit=data['num_tracks'], time_range=data['time_range'])
    #response = sp.current_user_top_artist(limit=data['num_artist'], time_range=data['time_range'])
    #print(json.dumps(response))

    return render_template("result.html",data=data)

# Token check 
def get_token(session):
    token_valid = False
    token_info = session.get("token_info", {})

    # Oturum açık devam ediyorsa Token saklanır
    if not(session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid
    
    # Oturum kapandıysa veya token süresi dolmuşsa
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    # Süresi dolan tokeni yenileme
    if (is_token_expired):
        sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = CLIENT_ID , client_secret = CLIENT_SECRET, redirect_uri = REDIRECT_URI, scope = SCOPE)
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid

if __name__ == "__main__":
    app.run(debug=True)