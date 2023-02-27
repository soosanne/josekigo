from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["DEBUG"] = True

#############################
# Database connection stuff #
#############################
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="Soosanne",
    password="soos_mysql",
    hostname="Soosanne.mysql.pythonanywhere-services.com",
    databasename="Soosanne$gogames",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app);
# Keep the last inserted game_id. This is not a long term solution to this problem.
# I want to be able to add an SGF to a game record. I could search for the last inserted
# game. Or I could write a proper loop for sending the game_id back to LSL and have it
# send it back to me when it uploads the SGF. Or I could just have the receipt of an
# SGF create a game record - since it has all the data I need in it - players, handicap,
# komi etc.
# But for now I'll just keep a global value that contains the ID of the last game added.
last_inserted_game_id = -1;

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

##########################
# Recent games list page #
##########################
@app.route("/", methods=["GET"])
def index():
    return render_template("main_page.html", games=Game.query.all())  # db.session.execute(db.select(Game)).all().order_by(Game.game_datetime))

####################
# View player page #
####################
@app.route('/player/<string:playeruuid>')
def view_player(playeruuid):
    player = Player.query.get(playeruuid)
    games = Game.query.filter((Game.game_whiteplayer==playeruuid) | (Game.game_blackplayer==playeruuid)).all()
    return render_template('player.html', player=player, games=games)

################
# Add SGF page #
################
@app.route("/addsgf", methods=["POST"])
def addsgf():
    # Get the sgfdata - this is what we will insert into the database
    sgfdata = request.data

    # Get the gameid if there is one
    gameid = request.args.get("gameid")
    if gameid is None:
        gameid = 0

    # If the gameid is 0 then update the last game without an SGF

    # For now just return the sgfdata
    return sgfdata

########################
# Add game record page #
########################
@app.route("/addgame", methods=["GET", "POST"])
def addgame():
    global last_inserted_game_id;

    # Check inputs - returns 400 bad request if arg is missing
    whiteplayername = request.values["whiteplayername"]
    blackplayername = request.values["blackplayername"]
    whiteplayeruuid = request.values["whiteplayeruuid"]
    blackplayeruuid = request.values["blackplayeruuid"]
    winneruuid = request.values["winneruuid"]
    boardsize = int(request.values["boardsize"])
    handicap = int(request.values["handicap"])
    komi = float(request.values["komi"])
    score = request.values["score"]

    # Add 1/2 if komi is given as a round number
    if float(int(komi)) == komi:
        komi = komi + 0.5

    # Check winner is one of the players
    if(winneruuid != whiteplayeruuid and winneruuid != blackplayeruuid):
        return "Malformed game data: Winner is not one of the players"

    # TODO: If player already exists check if their name has changed and if so then update it

    # If player doesn't already exist then create an entry for them in the players table
    # TODO: If player already exists check if their name has changed and if so then update it
    whiteexists = db.session.query(Player.player_uuid).filter_by(player_uuid=whiteplayeruuid).scalar() is not None
    if not whiteexists:
        whiteplayer = Player(player_name=whiteplayername, player_uuid=whiteplayeruuid)
        db.session.add(whiteplayer)
        db.session.commit()

    # Often it is the case that one player controls both sides - mostly for teaching games
    # TODO: If player already exists check if their name has changed and if so then update it
    if blackplayeruuid != whiteplayeruuid:
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
                game_score = score)

    # Add game to DB
    db.session.add(game)
    db.session.commit()

    # Save the last inserted game_id just in case an SGF arrives for it
    last_inserted_game_id = game.game_id

    return "Game added"         # Or redirect to / with redirect(url_for('index'))