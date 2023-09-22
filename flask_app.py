from flask import Flask, redirect, render_template, request, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
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
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = database_connection.SECRET_KEY

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
    game_tournament = db.Column(db.Integer, db.ForeignKey('tournaments.tournament_id'), nullable=True)

    game_whiteplayerdata = db.relationship('Player', foreign_keys='Game.game_whiteplayer')
    game_blackplayerdata = db.relationship('Player', foreign_keys='Game.game_blackplayer')
    game_winnerdata = db.relationship('Player', foreign_keys='Game.game_winner')
    game_tournamentdata = db.relationship('Tournament', foreign_keys='Game.game_tournament')

    game_sgf = db.Column(db.Text, nullable=True)

class Tournament(db.Model):
    __tablename__ = "tournaments"
    tournament_id = db.Column(db.Integer, primary_key=True)
    tournament_name = db.Column(db.String(255), nullable=False)
    tournament_text = db.Column(db.Text, nullable=True)
    tournament_closed = db.Column(db.Boolean, nullable=True)

class Login(db.Model):
    __tablename__ = "logins"
    login_id = db.Column(db.Integer, primary_key=True)
    login_username = db.Column(db.String(255), nullable=False, unique=True)
    login_password = db.Column(db.String(255), nullable=False)
    login_player_uuid = db.Column(db.String(255), db.ForeignKey('players.player_uuid'), nullable=True)  # Player UUID
    login_admin = db.Column(db.Boolean, default=0, nullable=False)
    login_playerdata = db.relationship('Player', foreign_keys='Login.login_player_uuid')

#############
# Functions #
#############

# Authentication function returns true if user is logged in. For now all users are
# considered admins. In future will add an is_admin column to the database
def verify_logged_in():
    return session.get('username')

# Authentication function returns true if user is logged in and is an admin.
def verify_is_admin():
    return session.get('username') and session.get('is_admin')

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
        elif difference.days > 13:
            return(f"{int(difference.days / 7)} weeks ago")
        elif difference.days > 7:
            return(f"{difference.days} days ago")
        elif difference.days > 2:
            return(f"{difference.days} days ago")
        else:
            return(f"{24 + int(difference.seconds / 3600)} hours ago")
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

# Return the username that is logged in or an empty string
def logged_in_user():
    return session.get('username', "")

#######################
# Register a new user #
#######################
@app.route("/register", methods=["GET", "POST"])
def register():
    # Only admins can access this page
    if verify_is_admin():
        if request.method == "GET":
            return render_template("register.html", user=logged_in_user())
        else:
            username = request.form['username']
            password = request.form['password']

            if Login.query.filter_by(login_username=username).first():
                return render_template('register.html', error='Username already exists', user=logged_in_user())

            # Hash the password before storing it in the database.
            new_user = Login(login_username=username, login_password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()

            # Once the new user is created redirect to the login page
            return redirect(url_for('login'))
    else:
        # We aren't logged in as admin. Redirect to login.
        return redirect(url_for('login'))

###################
# Change password #
###################
@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if request.method == "GET":
        return render_template('change_password.html', user=logged_in_user())
    else:
        # Only do this if we're logged in
        if verify_logged_in():
            old_password = request.form['old_password']
            new_password = request.form['new_password']

            # Ensure that the username we're logged in with still exists in the database
            login = Login.query.filter_by(login_username=session['username']).first()
            if login and check_password_hash(login.password, old_password):
                # Change the hashed password and save it to the database
                login.password = generate_password_hash(new_password)
                db.session.commit()
            else:
                # Redirect to /
                return redirect('/')
        else:
            # Can't change password if not logged in. Redirect to /
            return redirect('/')

#########
# Login #
#########
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # This is a post request therefore the login form has been submitted
        username = request.form['username']
        password = request.form['password']

        # Get the login entry with the given username from the database and check the password
        login = Login.query.filter_by(login_username=username).first()
        if login and check_password_hash(login.login_password, password):
            # Store session variables to indicate that we're logged in and whether we're an admin
            session['username'] = username
            if login.login_admin:
                session['is_admin'] = True

            # Redirect to the homepage
            return redirect('/')
        else:
            # Render the login page with an error
            return render_template('login.html', error='Invalid username or password', user=logged_in_user())
    else:
        # Render the login page
        return render_template("login.html", user=logged_in_user())

##########
# Logout #
##########
@app.route("/logout")
def logout():
    session.pop('username', None)
    session.pop('is_admin', None)
    return redirect('/')

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
    return render_template("main_page.html", games=games, time_ago=time_ago, boardsize=boardsize, user=logged_in_user())

##############
# About page #
##############
@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html", user=logged_in_user())

#############
# View Game #
#############
@app.route('/game/<int:gameid>', methods=["GET"])
def view_game(gameid):
    return render_template('game_sgf.html', game=Game.query.get(gameid), user=logged_in_user())

#########################
# View all players page #
#########################
@app.route('/players', methods=["GET"])
def all_players():
    return render_template('all_players.html', players=Player.query.order_by(Player.player_name).all(), user=logged_in_user())

####################
# View player page #
####################
@app.route('/player/<string:playeruuid>', methods=["GET"])
def view_player(playeruuid):
    global items_per_page
    page = request.args.get('page', 1, type=int)
    games=Game.query.filter((Game.game_whiteplayer==playeruuid) | (Game.game_blackplayer==playeruuid)).order_by(Game.game_datetime.desc()).paginate(page, per_page=items_per_page)
    return render_template('player.html', player=Player.query.get(playeruuid), games=games, time_ago=time_ago, user=logged_in_user())

#############################
# View all tournaments page #
#############################
@app.route('/tournaments', methods=["GET"])
def all_tournaments():
    return render_template('tournaments.html', tournaments=Tournament.query.all(), user=logged_in_user())

########################
# View tournament page #
########################
@app.route('/tournament/<string:tournament_id>', methods=["GET"])
def view_tournament(tournament_id):
    global items_per_page
    page = request.args.get('page', 1, type=int)
    games=Game.query.filter(Game.game_tournament == tournament_id).order_by(Game.game_datetime.desc()).paginate(page, per_page=items_per_page)
    return render_template('tournament.html', tournament=Tournament.query.get(tournament_id), games=games, time_ago=time_ago, user=logged_in_user(), admin=verify_is_admin())

########################
# Edit tournament text #
########################
@app.route('/edit_tournament_text/<string:tournament_id>', methods=["GET", "POST"])
def edit_tournament_text(tournament_id):
    # First - check we're logged in
    if verify_logged_in():
        if request.method == "GET":
            # If this is a GET then display the tournament text editing page
            return render_template('edit_tournament_text.html', tournament=Tournament.query.get(tournament_id), user=logged_in_user(), admin=verify_is_admin())
        else:
            # If this is a POST then take the html text. Convert links into pretty links and save it to the database
            tournament = Tournament.query.get(tournament_id)
            htmltext = re.sub(r'<a href="\.\.\/game\/(\d+)">view game</a>', r'<span class="badge bg-primary rounded-pill mb-1"><a class="link-light text-decoration-none" href="../game/\1">view game</a></span>', request.form["htmltext"])
            tournament.tournament_text = htmltext
            db.session.commit()

            # Redirect back to the tournament page we just updated
            return redirect(url_for('view_tournament', tournament_id=tournament_id))
    else:
        return redirect(url_for("login"))

###################
# Upload SGF page #
###################
@app.route("/uploadsgf", methods=["POST"])
def uploadsgf():
    # Get the sgfdata - this is what we will insert into the database
    sgfdata = request.data.decode("utf-8")

    # Get the event ID - if there is one
    # If the event is given AND is numeric AND exists in the DB
    # then set the tournamentid to be used when we create the game record
    event = findmatch("EV", sgfdata)
    if event != "" and event.isnumeric() and db.session.query(Tournament.tournament_id).filter_by(tournament_id=int(event)).scalar() is not None and not db.session.query(Tournament.tournament_closed).filter_by(tournament_id=int(event)).first().tournament_closed:
        tournamentid = int(event)
    else:
        tournamentid = None

#    if event != "" and event.isnumeric() and db.session.query(Tournament.tournament_id).filter_by(tournament_id=int(event)).scalar() is not None:
#        tournamentid = int(event)

        # Check if the given tournament is closed. If so then still upload the SGF but don't add it to the tournament
#        tournament = db.session.query(Tournament.tournament_closed).filter_by(tournament_id=tournamentid).first()
#        if tournament.tournament_closed == 1:
#            tournamentid = None

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
    # If player already exists check if their name has changed and if so then update it
    whiteexists = db.session.query(Player.player_uuid).filter_by(player_uuid=whiteplayeruuid).scalar() is not None
    if whiteexists:
        whiteplayer = db.session.query(Player).filter_by(player_uuid=whiteplayeruuid).first()
        if whiteplayer.player_name != whiteplayername:
            whiteplayer.player_name = whiteplayername
            db.session.commit()
    else:
        whiteplayer = Player(player_name=whiteplayername, player_uuid=whiteplayeruuid)
        db.session.add(whiteplayer)
        db.session.commit()

    # Often it is the case that one player controls both sides - mostly for teaching games
    if blackplayeruuid != whiteplayeruuid:
        # If player already exists check if their name has changed and if so then update it
        blackexists = db.session.query(Player.player_uuid).filter_by(player_uuid=blackplayeruuid).scalar() is not None
        if blackexists:
            blackplayer = db.session.query(Player).filter_by(player_uuid=blackplayeruuid).first()
            if blackplayer.player_name != blackplayername:
                blackplayer.player_name = blackplayername
                db.session.commit()
        else:
            blackplayer = Player(player_name=blackplayername, player_uuid=blackplayeruuid)
            db.session.add(blackplayer)
            db.session.commit()

    # Create game object
    if tournamentid != None:
        game = Game(game_whiteplayer = whiteplayeruuid,
                    game_blackplayer = blackplayeruuid,
                    game_boardsize = boardsize,
                    game_handicap = handicap,
                    game_komi = komi,
                    game_winner = winneruuid,
                    game_score = score,
                    game_tournament = tournamentid,
                    game_sgf = sgfdata)
    else:
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

    return f"game/{game.game_id}"