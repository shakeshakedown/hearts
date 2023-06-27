### Pseudocode
# get how many players there are (3 or 4)
# retrieve player names
# show current scoreboard with scores associated with player names
# show passing direction
# allow input for new scores
# check that new scores add up to the correct value
# check if there's a winner
# show new scoreboard with inputs for new points

### Libraries
from flask import Flask, request, render_template, redirect, url_for, session, flash
import secrets

### App, Variables & Routes
app = Flask(__name__)
app.secret_key = secrets.token_bytes(24)
passing_rules = {
    3: ("left", "right", "hold"),
    4: ("left", "right", "across", "hold")
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # assigns either '3' or '4' based on how many players were selected
            num_players = int(request.form.get("num_players"))
            if num_players not in passing_rules:
                raise ValueError()
            session["num_players"] = num_players
            session["passing"] = passing_rules[num_players]
            session["current_pass"] = session["passing"][session["passing"].index(request.form.get("start_passing"))]
            # adds one to total players so it counts from 1, not 0
            session["num_players"] += 1
            session["three_player_select"] = False if session["num_players"] == 5 else True
        except:
            flash('Error with number of players.  Please refresh and try again.')
            return redirect(url_for("index"))

        # dictionary for the player id, name & scores
        session["game"] = {f"p{x}": [request.form.get(f"p{x}"), [0]] for x in range(1, session["num_players"])}

        # list of names for validation
        session["names"] = [session["game"][f"p{x}"][0] for x in range(1, session["num_players"])]

        # check if the points is filled in and a number and more than 26
        session["max_points"] = request.form.get("max_points")  

        # name validation
        for name in session["names"]:
            if name == "":
                session["validation"] = True
                flash("At least one of the names is blank, please fill in all names.")
                return redirect(url_for("index"))
            
        # score validation
        if session["max_points"].isdigit() and int(session["max_points"]) >= 26 and session["max_points"].isdigit():
            return redirect(url_for("scoreboard"))
        else:
            session["validation"] = True
            flash("'Max Points' must be a number larger than 26.")
            return redirect(url_for("index"))
        
    template_data = {
        "three_player_select": session.get("three_player_select", True),
        "validation": session.get("validation", False),
        "max_points_temp": session.get("max_points", ""),
        "p1_name_temp": session.get("game", {}).get("p1", [""])[0],
        "p2_name_temp": session.get("game", {}).get("p2", [""])[0],
        "p3_name_temp": session.get("game", {}).get("p3", [""])[0],
        "p4_name_temp": session.get("game", {}).get("p4", [""])[0]
    }
 
    return render_template("index.html", **template_data)

@app.route("/scoreboard", methods=["GET", "POST"])
def scoreboard():
    if request.method == "POST":
        session["validation"] = False
        points = [request.form.get(f"p{player}s", "").strip() for player in range(1, session["num_players"])]

        # storing user input as temp_scores for validation
        for player, score in zip(range(1, session["num_players"]), points):
            session[f"p{player}"] = score
        session["temp_scores"] = {}
        for player in range(1, session["num_players"] + 1):
            key = f"p{player}"
            session["temp_scores"][key] = session.get(key, "")
 
        # check if all fields were filled in
        if not all(points):
            session["validation"] = True
            flash("One or more of the score fields is blank.")
            return redirect(url_for("scoreboard"))

        # check if the point values are integers
        try:
            points = [int(x) for x in points]
        except ValueError:
            session["validation"] = True
            flash("Score input needs to be an integer and nothing else.")
            return redirect(url_for("scoreboard"))

        # check if the points add up to 26
        if sum(points) != 26:
            session["validation"] = True
            flash(f"Total points possible per hand is 26.  What you've entered totals to {sum(points)}.")
            return redirect(url_for("scoreboard"))

        moon_shot_index = points.index(26) + 1 if 26 in points else None

        # shooting the moon (or not)
        if moon_shot_index:
            for player in range(1,session["num_players"]):
                if player != moon_shot_index:
                    last_score = session["game"][f"p{player}"][1][-1]
                    new_score = last_score + 26
                    session["game"][f"p{player}"][1].append(new_score)
        else:
            for player in range(1,session["num_players"]):
                recent_input = (int(request.form.get(f"p{player}s").strip()))
                last_score = session["game"][f"p{player}"][1][-1]
                new_score = recent_input + last_score
                session["game"][f"p{player}"][1].append(new_score)

        # move on to the next item in the passing tuple
        session["current_pass"] = session["passing"][(session["passing"].index(session["current_pass"]) + 1) % len(session["passing"])]
        return redirect(url_for("winner"))

    template_data = {
        "scores": session["game"],
        "names": session["names"],
        "max_points": session["max_points"],
        "passing": session["passing"],
        "validation": session.get("validation", False),
        "current_pass": session["current_pass"],
        "temp_scores": session.get("temp_scores", {})
    }
    return render_template("scoreboard.html", **template_data)
    
@app.route("/winner", methods=["POST", "GET"])
def winner():
    try:
        scores = [session["game"][f"p{player}"][1][-1] for player in range(1, session["num_players"])]
        if any(score >= int(session["max_points"]) for score in scores):
            lowest_score = [score for score in scores if score < int(session["max_points"])]
            winners = [session["game"][f"p{player}"][0] for player in range(1, session["num_players"]) if session["game"][f"p{player}"][1][-1] == min(lowest_score)]
            return render_template("winner.html", winners=winners)
        else:
            return redirect(url_for("scoreboard"))
    except:
        return "winner error"

if __name__ == "__main__":
    app.run(debug=True)