### Pseudocode
# get how many players there are (3 or 4)
# retrieve player names
# show current scoreboard with scores associated with player names
# show passing direction
# allow input for new scores
# check that new scores add up to the correct value
# check if there's a winner
# show new scoreboard with inputs for new points


### Things I Still Want to Add
# 1) If player names are input correctly but the max points is not, keep
#    player names through the error

### Libraries
from flask import Flask, request, render_template, redirect, url_for, session, flash
import secrets

### App, Variables & Routes
app = Flask(__name__)
app.secret_key = secrets.token_bytes(24)
three_player_passing = ("left", "right", "hold")
four_player_passing = ("left", "right", "across", "hold")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # pulls the number of players from radio input
        try:
            session["num_players"] = int(request.form.get("num_players"))
            # sets which passing rules the game will follow
            session["passing"] = three_player_passing if session["num_players"] == 3 else four_player_passing
            session["current_pass"] = session["passing"][session["passing"].index(request.form.get("start_passing"))]
            # add one for range purposes (this works better with the html)
            session["num_players"] += 1
        except:
            flash('Error with number of players.  Please refresh and try again.')
            return redirect(url_for("index"))
        # creates a dictionary with p1: [name, 0]
        session["main_dic"] = {f"p{x}": [request.form.get(f"p{x}"), [0]] for x in range(1,session["num_players"])}
        # test to see if user left any blanks in the player name inputs
        for x in range(1, session["num_players"]):
            if session["main_dic"][f"p{x}"][0] == "":
                flash('One of the names is blank.  Please enter all fields.')
                return redirect(url_for("index"))
            else:
                # creates a list of user-inputted names
                session["names"] = [session["main_dic"][f"p{x}"][0] for x in range(1,session["num_players"])]
        # creates variable for maximum amount of points per game (usually 100)
        session["max_points"] = request.form.get("max_points")
        # checks to make sure that the input is a number
        if not session["max_points"].isdigit():
            flash("Max Points needs to be a number.")
            return redirect(url_for("index"))
        if int(session["max_points"]) < 26:
            flash("Max points must be at least 26 points.")
            return redirect(url_for("index"))
        return redirect(url_for("scoreboard"))
    return render_template("index.html")

@app.route("/scoreboard", methods=["GET", "POST"])
def scoreboard():
    return render_template("scoreboard.html", 
                           scores=session["main_dic"],
                           names=session["names"],
                           max_points=session["max_points"],
                           passing=session["passing"],
                           current_pass=session["current_pass"])
    
@app.route("/addpoints", methods=["POST"])
def add_points():
    if request.method == "POST":
        # retrieve the user inputed scores
        recent_input_validation = [request.form.get(f"p{player}s").strip() for player in range(1,session["num_players"])]
        if all(recent_input_validation):
            try:
                # try to convert input to integer
                recent_input_validation = [int(x) for x in recent_input_validation]
                try:
                    # check to see if values add up to 26
                    total_value_26 = sum([x for x in recent_input_validation])
                    if total_value_26 == 26:
                        # passes validation and continues on to add most recent score to previous score
                        if 26 in recent_input_validation:
                            moon_shot_index = recent_input_validation.index(26) + 1
                            for player in range(1, session["num_players"]):
                                if player == moon_shot_index:
                                    continue
                                else:
                                    last_score = session["main_dic"][f"p{player}"][1][-1]
                                    new_score = last_score + 26
                                    session["main_dic"][f"p{player}"][1].append(new_score)
                            session["current_pass"] = session["passing"][(session["passing"].index(session["current_pass"]) + 1) % len(session["passing"])]
                            session.modified = True
                            return redirect(url_for("winner"))
                        else:
                            for player in range(1,session["num_players"]):
                                recent_input = (int(request.form.get(f"p{player}s").strip()))
                                # finds the last item in the score list
                                last_score = session["main_dic"][f"p{player}"][1][-1]
                                # combines the last score in the list and the most recent input
                                new_score = recent_input + last_score
                                # adds the two variables together to create the new score
                                session["main_dic"][f"p{player}"][1].append(new_score)
                            session["current_pass"] = session["passing"][(session["passing"].index(session["current_pass"]) + 1) % len(session["passing"])]
                            session.modified = True
                            return redirect(url_for("winner"))
                    else:
                        # scores did not add up to 26, return to /scoreboard with error message
                        flash('Points did not add up to 26.  Please re-check the math.')
                        return redirect(url_for('scoreboard'))
                except:
                    pass
            except:
                # scores were not able to be converted to int, return to /scoreboard with error message
                flash("Score input needs to be an integer and nothing else.")
                return redirect(url_for('scoreboard'))
        else:
            flash("One or more of the score fields is blank.")
            return redirect(url_for('scoreboard'))
    
@app.route("/winner", methods=["POST", "GET"])
def winner():
    try:
        scores = [session["main_dic"][f"p{player}"][1][-1] for player in range(1, session["num_players"])]
        if any(score >= int(session["max_points"]) for score in scores):
            lowest_score = [score for score in scores if score < int(session["max_points"])]
            winners = [session["main_dic"][f"p{player}"][0] for player in range(1, session["num_players"]) if session["main_dic"][f"p{player}"][1][-1] == min(lowest_score)]
            return render_template("winner.html", winners=winners)
            # if len(winners) == 1:
            #     return render_template("winner.html", winners=winners)
            # else:
            #     return f"it was a tie! the winners were {' & '.join(winners)}"
        else:
            return redirect(url_for("scoreboard"))
    except:
        return "winner error"

# if __name__ == "__main__":
#     app.run(debug=True)

application = app