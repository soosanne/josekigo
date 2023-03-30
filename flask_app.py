from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re
import database_connection

app = Flask(__name__)
app.config["DEBUG"] = True
items_per_page = 20

#############################
# Database connection stuff #
#############################
app.config["SQLALCHEMY_DATABASE_URI"] = database_connection.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app);

################################
# Define database table models #
################################
class Player(db.Model):
    __tablename__ = "players"
    player_name = db.Column(db.String(255), nullable=False, unique=False)
    player_uuid = db.Column(db.String(255), nullable=False, unique=True, primary_key=True)

    def __repr__(self):
        return f'<Player {self.player_uuid} - {self.player_name}>'

class Game(db.Model):
    __tablename__ = "games"
    game_id = db.Column(db.Integer, primary_key=True)
    game_datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    game_whiteplayer = db.Column(db.String(255), db.ForeignKey('players.player_uuid'), nullable=False)  # Player UUID
    game_blackplayer = db.Column(db.String(255), db.ForeignKey('players.player_uuid'), nullable=False)  # Player UUID
    game_handicap = db.Column(db.Integer, default=0, nullable=False)
    game_boardsize = db.Column(db.Integer, default=19, nullable=False)
    game_komi = db.Column(db.Float, default=0.5, nullable=False)
    game_winner = db.Column(db.String(255), db.ForeignKey('players.player_uuid'), nullable=False)       # Player UUID
    game_score = db.Column(db.String(10), nullable=False)                                               # String showing score or "resign"

    game_whiteplayerdata = db.relationship('Player', foreign_keys='Game.game_whiteplayer')
    game_blackplayerdata = db.relationship('Player', foreign_keys='Game.game_blackplayer')
    game_winnerdata = db.relationship('Player', foreign_keys='Game.game_winner')

    game_sgf = db.Column(db.Text, nullable=True)

#############
# Functions #
#############

# Used on games lists pages to show how old a game is
def time_ago(dt):
    tn = datetime.now()
    difference = tn - dt
    if difference.days > 0:
        if difference.days > 730:
            return(f"{int(difference.days / 365)} years ago")
        elif difference.days > 365:
            return("1 year ago")
        elif difference.days > 60:
            return(f"{int(difference.days / 30)} months ago")
        elif difference.days > 30:
            return("1 month ago")
        elif difference.days > 14:
            return(f"{int(difference.days / 7)} weeks ago")
        elif difference.days > 7:
            return("1 week ago")
        elif difference.days > 1:
            return(f"{difference.days} days ago")
        else:
            return("1 day ago")
    elif difference.seconds > 0:
        if difference.seconds > 7200:
            return(f"{int(difference.seconds / 3600)} hours ago")
        elif difference.seconds > 3600:
            return("1 hour ago")
        elif difference.seconds > 120:
            return(f"{int(difference.seconds / 60)} minutes ago")
        elif difference.seconds > 60:
            return("1 minute ago")
        else:
            return(f"{difference.seconds} seconds ago")
    else:
        return("just now")

# Used by the uploadsgf page to find stuff in an SGF file
def findmatch(needle, haystack):
    match = re.search(needle + r'\[(.*?)\]', haystack)

    if match:
        return match.group(1)
    else:
        return ""


##########################
# Recent games list page #
##########################
@app.route("/", methods=["GET"])
def index():
    global items_per_page
    page = request.args.get('page', 1, type=int)
    boardsize = request.args.get('boardsize', -1, type=int)
    if boardsize == -1:
        games=Game.query.order_by(Game.game_datetime.desc()).paginate(page, per_page=items_per_page)
    else:
        games=Game.query.filter_by(game_boardsize=boardsize).order_by(Game.game_datetime.desc()).paginate(page, per_page=items_per_page)
    return render_template("main_page.html", games=games, time_ago=time_ago, boardsize=boardsize)

##############
# About page #
##############
@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")

#################
# View Game SGF #
#################
@app.route('/game/<int:gameid>', methods=["GET"])
def view_game(gameid):
    return render_template('game_sgf.html', game=Game.query.get(gameid))

####################
# View player page #
####################
@app.route('/player/<string:playeruuid>', methods=["GET"])
def view_player(playeruuid):
    global items_per_page
    page = request.args.get('page', 1, type=int)
    games=Game.query.filter((Game.game_whiteplayer==playeruuid) | (Game.game_blackplayer==playeruuid)).order_by(Game.game_datetime.desc()).paginate(page, per_page=items_per_page)
    return render_template('player.html', player=Player.query.get(playeruuid), games=games, time_ago=time_ago)

#########################
# View all players page #
#########################
@app.route('/players', methods=["GET"])
def all_players():
    return render_template('all_players.html', players=Player.query.all())

###################
# Upload SGF page #
###################

@app.route("/uploadsgf", methods=["POST"])
def uploadsgf():
    global last_inserted_game_id;

    # Get the sgfdata - this is what we will insert into the database
    sgfdata = request.data.decode("utf-8")

    # Get all the important game information from the SGF
    whiteplayername = findmatch("PW", sgfdata)
    blackplayername = findmatch("PB", sgfdata)
    whiteplayeruuid = findmatch("WT", sgfdata)
    blackplayeruuid = findmatch("BT", sgfdata)
    score = findmatch("RE", sgfdata)
    if score[0] == "W":
        winneruuid = whiteplayeruuid
    else:
        winneruuid = blackplayeruuid
    boardsize = int(findmatch("SZ", sgfdata))
    handicap = findmatch("HA", sgfdata)
    if handicap == "":
        handicap = 0
    else:
        handicap = int(handicap)
    komi = float(findmatch("KM", sgfdata))

    # Add 1/2 if komi is given as a round number
    if float(int(komi)) == komi:
        komi = komi + 0.5

    # If player doesn't already exist then create an entry for them in the players table
    # TODO: If player already exists check if their name has changed and if so then update it
    whiteexists = db.session.query(Player.player_uuid).filter_by(player_uuid=whiteplayeruuid).scalar() is not None
    if not whiteexists:
        whiteplayer = Player(player_name=whiteplayername, player_uuid=whiteplayeruuid)
        db.session.add(whiteplayer)
        db.session.commit()

    # Often it is the case that one player controls both sides - mostly for teaching games
    if blackplayeruuid != whiteplayeruuid:
        # TODO: If player already exists check if their name has changed and if so then update it
        blackexists = db.session.query(Player.player_uuid).filter_by(player_uuid=blackplayeruuid).scalar() is not None
        if not blackexists:
            blackplayer = Player(player_name=blackplayername, player_uuid=blackplayeruuid)
            db.session.add(blackplayer)
            db.session.commit()

    # Create game object
    game = Game(game_whiteplayer = whiteplayeruuid,
                game_blackplayer = blackplayeruuid,
                game_boardsize = boardsize,
                game_handicap = handicap,
                game_komi = komi,
                game_winner = winneruuid,
                game_score = score,
                game_sgf = sgfdata)

    # Add game to DB
    db.session.add(game)
    db.session.commit()

    # We don't use this any more when we switch to SGF only uploading
    last_inserted_game_id = -1;

    return f"game/{game.game_id}"