from app import app
from flask import Flask, redirect, render_template, request, session, flash, abort
import funds
import functions
from all_possible_funds import all_possible_funds
from user_specified_funds import user_specified_funds
from os import getenv
from watchlist_specific_funds import watchlist_specific_funds, watchlist_sums, chosen_watchlist_funds
import secrets

@app.before_request
def before_request():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)

@app.route("/")
def index():
    list = funds.funds()
    watchlist = watchlist_sums()
    return render_template("index.html", funds=list, watchlist=watchlist)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if functions.log_in(username, password):
            return redirect("/")
        else:
            return render_template("error.html", message="Wrong username or password")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if request.form.get("is_admin") == "true":
            if request.form["admin_creds"] == getenv("ADMIN_KEY"):
                admin = True
            else:
                return render_template("error.html", message="Admin key incorrect")
        else:
            admin = False
        if password1 != password2:
            return render_template("error.html", message="Passwords do not match")
        if functions.register(username, password1, admin):
            return redirect("/")
        else:
            return render_template("error.html", message="Registration failed")



## Corrected version:
#@app.route("/deposit", methods=["GET", "POST"])
"""
def deposit():
    if "username" not in session:
        return redirect("/login")
    available_funds = all_possible_funds()
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        amount = request.form["amount"]
        if len(amount)>20:
            flash("Amount must be less then 20 digits", "error")
            return redirect("/deposit")
        try:
            amount = int(amount)
        except ValueError:
            flash("Amount must be an integer", "error")
            return redirect("/deposit")
        if amount <= 0:
            flash("Amount must be greater than 0", "error")
            return redirect("/deposit")
        fund = request.form["fund"]
        success = functions.deposit(session["username"], amount, fund)
        if success:
            flash("Deposit successful", "success")
            return redirect("/")
        else:
            flash("Deposit failed", "error")
    return render_template("deposit.html", funds=available_funds)
"""


### This currently is faulty in the try amount int part. if deposit is a large number like:
### 999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
## It crashes the server. Poor architecture.
@app.route("/deposit", methods=["GET", "POST"])
def deposit():
    if "username" not in session:
        return redirect("/login")
    available_funds = all_possible_funds()
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        amount = request.form["amount"]
        try:
            amount = int(amount)
        except ValueError:
            flash("Amount must be an integer", "error")
            return redirect("/deposit")
        if amount <= 0:
            flash("Amount must be greater than 0", "error")
            return redirect("/deposit")
        fund = request.form["fund"]
        success = functions.deposit(session["username"], amount, fund)
        if success:
            flash("Deposit successful", "success")
            return redirect("/")
        else:
            flash("Deposit failed", "error")
    return render_template("deposit.html", funds=available_funds)

# Correct version with CSRF token.
"""
@app.route("/withdraw", methods=["GET", "POST"])
def withdraw():
    if "username" not in session:
        return redirect("/login")
    available_funds_for_account = user_specified_funds() or []
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        amount = request.form["amount"]
        try:
            amount = int(amount)
        except ValueError:
            flash("Amount must be an integer", "error")
            return redirect("/withdraw")
        fund = request.form["fund"]
        success = functions.withdraw(session["username"], amount, fund)
        if success:
            flash("Withdrawal successful", "success")
            return redirect("/")
        else:
            flash("Withdrawal failed", "error")
    return render_template("withdraw.html", funds=available_funds_for_account)

"""
# CSRF PROTECTION REMOVED
@app.route("/withdraw", methods=["GET", "POST"])
def withdraw():
    if "username" not in session:
        return redirect("/login")
    available_funds_for_account = user_specified_funds() or []
    if request.method == "POST":
        # CSRF protection removed
        amount = request.form["amount"]
        try:
            amount = int(amount)
        except ValueError:
            flash("Amount must be an integer", "error")
            return redirect("/withdraw")
        fund = request.form["fund"]
        success = functions.withdraw(session["username"], amount, fund)
        if success:
            flash("Withdrawal successful", "success")
            return redirect("/")
        else:
            flash("Withdrawal failed", "error")
    return render_template("withdraw.html", funds=available_funds_for_account)





@app.route("/create_fund", methods=["GET", "POST"])
def create_fund():
    if "username" not in session:
        return redirect("/login")
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        fund_name = request.form["fund_name"]
        intrest = request.form["intrest"]
        username = session["username"]
        if not fund_name or fund_name.strip() == "":
            flash("Fund must have a name", "error")
            return redirect("/create_fund")
        try:
            intrest = float(intrest)
        except ValueError:
            flash("Intrest must be a number", "error")
            return redirect("/create_fund")
        admin = functions.admin_check(username)
        if admin:
            success = functions.create_fund(fund_name, intrest, username)
            if success:
                flash("Fund created", "success")
                return redirect("/")
            else:
                flash("Fund creation failed", "error")
        else:
            flash("You do not have permission to create funds", "error")
    return render_template("create_fund.html")

@app.route("/watchlist", methods=["GET", "POST"])
def watchlist():
    if "username" not in session:
        return redirect("/login")
    available_funds = watchlist_specific_funds() or []
    watchlist_funds = chosen_watchlist_funds() or []
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)
        fund = request.form["fund"]
        success = functions.add_to_watchlist(session["username"], fund)
        if success:
            flash("Fund added to watchlist", "success")
            return redirect("/watchlist")
        else:
            flash("Failed to add fund to watchlist", "error")
    return render_template("watchlist.html", available_funds=available_funds, watchlist_funds=watchlist_funds)

@app.route("/remove_from_watchlist", methods=["POST"])
def remove_from_watchlist():
    if "username" not in session:
        return redirect("/login")
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
    fund = request.form["fund"]
    success = functions.remove_from_watchlist(session["username"], fund)
    if success:
        flash("Fund removed from watchlist", "success")
    else:
        flash("Failed to remove fund from watchlist", "error")
    return redirect("/watchlist")

@app.route("/logout")
def logout():
    functions.logout()
    return redirect("/")

@app.route("/error")
def error():
    return render_template("error.html")