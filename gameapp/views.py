from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from gameapp.mongo import users_col, words_col, games_col, guesses_col
import datetime
import re
from bson import ObjectId
from django.contrib import messages


def register(request):
    username = request.session.get('username')
    if username:
        return redirect("home")
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user_type = request.POST.get('user_type','player')
        if len(username) < 5:
            return render(request, "register.html", {"error": "Username must be at least 5 characters long."})
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])[A-Za-z0-9]{5,}$', username):
            return render(request, "register.html", {"error": "Username must contain at least 1 uppercase and 1 lowercase letter, and only include letters or numbers"})
        if len(password) < 5:
            return render(request, "register.html", {"error": "Password must be at least 5 characters long."})
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[$%@*]).{5,}$', password):
            return render(request, "register.html", {"error": "Password must have alpha, numeric, and one of $, %, *, @."})
        if users_col.find_one({"username": username}):
            return render(request, "register.html", {"error": "Username already exists."})
        users_col.insert_one({
            "username": username,
            "password": make_password(password),
            "user_type": user_type
        })
        return redirect("login")

    return render(request, "register.html")


def login(request):
    username = request.session.get('username')
    if username:
        return redirect("home")
    if request.method=="POST":
        username = request.POST['username']
        password = request.POST['password']
        selected_type = request.POST.get('user_type', 'player')
        user = users_col.find_one({
            "username": username,
            "user_type": selected_type
        })
        if (not user) or (not check_password(password,user['password'])):
            return render(request, "login.html", {"error": "Invalid username, password, or user type."})
        request.session['username'] = username
        request.session['user_type'] = user['user_type']
        return redirect("home")
    return render(request, "login.html")


def home(request):
    username = request.session.get("username")
    if not username:
        return redirect("login")
    user = users_col.find_one({"username": username})
    limit_reached = request.session.pop('limit_reached', False)
    today = datetime.datetime.now().date()
    games_played_today = games_col.count_documents({
        "user_id": ObjectId(user['_id']),
        "start_date": {"$gte": datetime.datetime(today.year, today.month, today.day)}
    })
    players = []
    if user["user_type"] == "admin":
        players = list(users_col.find({"user_type": "player"}, {"username": 1, "_id": 0}).sort("username", 1).collation({"locale": "en", "strength": 2}))
    return render(request, "home.html", {
        "username": username,
        "limit_reached": limit_reached,
        "games_played_today": games_played_today,
        "players": players,
    })



def start_game(request):
    if request.session.get('user_type') == 'admin':
        messages.error(request, "Admins cannot play.")
        return redirect("home")
    username = request.session.get('username')
    if not username:
        return redirect("login")
    user = users_col.find_one({"username": username})
    today = datetime.datetime.now().date()
    games_played_today = games_col.count_documents({
        "user_id": ObjectId(user['_id']),
        "start_date": {"$gte": datetime.datetime(today.year, today.month, today.day)}
    })
    if games_played_today >= 3:
        request.session['limit_reached'] = True
        return redirect("home")
    word_doc = list(words_col.aggregate([{"$sample": {"size": 1}}]))[0]
    game_id = games_col.insert_one({
        "user_id": user['_id'],
        "word_id": word_doc['_id'],
        "target_word": word_doc['word'].upper(),
        "start_date": datetime.datetime.now(),
        "completed": False,
        "won": False,
        "guesses_used": 0
    }).inserted_id
    request.session['game_id'] = str(game_id)
    return redirect("game_view")


def game_view(request):
    username = request.session.get("username")
    if not username:
        return redirect('login')
    if request.session.get("user_type") == "admin":
        messages.error(request, "Admins cannot play.")
        return redirect("home")
    game_id = request.session.get("game_id")
    if not game_id:
        return redirect("start_game")
    game = games_col.find_one({"_id": ObjectId(game_id)})
    if not game:
        return redirect("start_game")
    guesses = []
    for g in guesses_col.find({"game_id": game['_id']}).sort("created_at", 1):
        letters = [{"char": c, "color": col} for c, col in zip(g["guess_word"], g["feedback"])]
        guesses.append({"letters": letters})
    status = request.session.pop('game_status', {"congrats": False, "fail": False, "target_word": None})
    return render(request, "game.html", {
        "username": username,
        "guesses": guesses,
        **status
    })


def submit_guess(request):
    if request.session.get('user_type') == 'admin':
        messages.error(request, "Admins cannot play.")
        return redirect("home")
    username = request.session.get('username')
    if not username:
        return redirect("login")
    game_id = request.session.get('game_id')
    if not game_id:
        return redirect("start_game")
    game = games_col.find_one({"_id": ObjectId(game_id)})
    if not game or game.get("completed"):
        return redirect("home")
    if request.method == "POST":
        guess = request.POST['guess'].upper()
        target_word = game['target_word']
        feedback = []
        temp_target = list(target_word)
        for i in range(5):
            if guess[i] == target_word[i]:
                feedback.append("green")
                temp_target[i] = None
            else:
                feedback.append(None)
        for i in range(5):
            if feedback[i] is None:
                if guess[i] in temp_target:
                    feedback[i] = "orange"
                    temp_target[temp_target.index(guess[i])] = None
                else:
                    feedback[i] = "grey"
        guesses_col.insert_one({
            "game_id": game['_id'],
            "guess_word": guess,
            "target_word": target_word,
            "feedback": feedback,
            "created_at": datetime.datetime.now()
        })
        new_count = game.get('guesses_used', 0) + 1
        games_col.update_one({"_id": game['_id']}, {"$set": {"guesses_used": new_count}})
        if guess == target_word:
            games_col.update_one({"_id": game['_id']}, {"$set": {"completed": True, "won": True}})
            request.session['game_status'] = {"congrats": True, "fail": False, "target_word": None}
        elif new_count >= 5:
            games_col.update_one({"_id": game['_id']}, {"$set": {"completed": True}})
            request.session['game_status'] = {"congrats": False, "fail": True, "target_word": target_word}
        else:
            request.session['game_status'] = {"congrats": False, "fail": False, "target_word": None}
        return redirect("game_view")

    return redirect("start_game")



def daily_report(request):
    if request.session.get('user_type') != 'admin':
        messages.error(request, "Access denied.")
        return redirect("home")
    date_str = request.GET.get('date')
    match_filter = {}
    if date_str:
        try:
            report_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            start_dt = datetime.datetime(report_date.year, report_date.month, report_date.day)
            end_dt = start_dt + datetime.timedelta(days=1)
            match_filter['start_date'] = {"$gte": start_dt, "$lt": end_dt}
        except:
            pass
    pipeline = [
        {"$match": match_filter} if match_filter else {"$match": {}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$start_date"}},
            "users_today": {"$addToSet": "$user_id"},
            "words_tried": {"$addToSet": "$word_id"},
            "total_guesses": {"$sum": "$guesses_used"},
            "correct_guesses": {"$sum": {"$cond": ["$won", 1, 0]}}
        }},
        {"$sort": {"_id": -1}}
    ]
    report_data = []
    for row in games_col.aggregate(pipeline):
        report_data.append({
            "date": row["_id"],
            "num_users": len(row["users_today"]),
            "words_tried": len(row["words_tried"]),
            "total_guesses": row["total_guesses"],
            "correct_guesses": row["correct_guesses"]
        })
    return render(request, "daily_report.html", {
        "report_data": report_data
    })


def user_report(request):
    if request.session.get('user_type') != 'admin':
        messages.error(request, "Access denied.")
        return redirect("home")
    username = request.GET.get('username')
    if not username:
        messages.error(request, "Please provide a username.")
        return redirect("home")
    user = users_col.find_one({"username": username})
    if not user:
        messages.error(request, f"User '{username}' not found.")
        return redirect("home")
    if user["user_type"] == "admin":
        messages.error(request, f"User '{username}' is admin.")
        return redirect("home")
    pipeline = [
        {"$match": {"user_id": user["_id"]}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$start_date"}},
            "words_tried": {"$sum": 1},
            "total_guesses": {"$sum": "$guesses_used"},
            "correct_guesses": {"$sum": {"$cond": ["$won", 1, 0]}}
        }},
        {"$sort": {"_id": 1}}
    ]
    report_data = []
    for row in games_col.aggregate(pipeline):
        report_data.append({
            "date": row["_id"],
            "words_tried": row["words_tried"],
            "total_guesses": row["total_guesses"],
            "correct_guesses": row["correct_guesses"]
        })
    return render(request, "user_report.html", {
        "username": username,
        "report_data": report_data
    })


def logout_view(request):
    request.session.flush()
    return redirect("login")