from enum import unique
import re
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    login_required,
    current_user,
    logout_user,
)
from numpy import info
import yfinance as yf
from flask_sqlalchemy import SQLAlchemy
import requests
from yfinance.ticker import Ticker


app = Flask(__name__)
app.config["SECRET_KEY"] = "SECRET GOES HERE"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/test1"
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# transaction table    ###################################################
class Transaction(db.Model):
    __tablename__ = "Transaction"
    sno = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(80), unique=True, nullable=True)
    Symbol = db.Column(db.String(80), unique=True, nullable=True)
    buy_price = db.Column(db.Integer, nullable=True)
    quantity = db.Column(db.Integer, nullable=True)
    sell_price = db.Column(db.Integer, nullable=True)
    profit = db.Column(db.Integer, nullable=True)
    email = db.Column(db.String(80), nullable=True)


# Portfolio table   ###################################################
class Portfolio(db.Model):
    __tablename__ = "Portfolio"
    sno = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(80), unique=True, nullable=True)
    Symbol = db.Column(db.String(80), unique=True, nullable=True)
    buy_price = db.Column(db.Integer, nullable=True)
    quantity = db.Column(db.Integer, nullable=True)
    sell_price = db.Column(db.Integer, nullable=True)
    profit = db.Column(db.Integer, nullable=True)
    email = db.Column(db.String(80), nullable=True)


class User(UserMixin, db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(80), nullable=True)
    phone = db.Column(db.Integer, nullable=True)
    email = db.Column(db.String(80), nullable=True)
    password = db.Column(db.String(80), nullable=True)


# first page code is here   ######################################################


@app.route("/")
def home_page():
    return render_template("index.html")


# login page code is here  ##################################################


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/valid", methods=["GET", "POST"])
def valid():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email, password=password).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That Email or Password is incorrect, please try again.")
            return redirect(url_for("login"))

        else:
            login_user(user)
            return redirect(url_for("home"))
    return render_template("login.html")


# Signup page code is here  ###################################################
@app.route("/Signup")
def Signup():
    return render_template("signup.html")


@app.route("/regi", methods=["GET", "POST"])
def regi():
    if request.method == "POST":
        if User.query.filter_by(email=request.form.get("email")).first():
            # print(User.query.filter_by(email=request.form.get("email")).first())
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for("login"))
        name = request.form.get("name")
        phone = request.form.get("phone")
        email = request.form.get("email")
        password = request.form.get("password")
        entry_user = User(name=name, phone=phone, email=email, password=password)
        db.session.add(entry_user)
        db.session.commit()
        login_user(entry_user)
        flash("You are successfully registered,Please Login")

        # return render_template("signup.html")
        return redirect("login")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home_page"))


# home page code is here  #########################################################
@app.route("/home.html", methods=["GET", "POST"])
@login_required
def home():
    name = current_user.name
    return render_template("home.html", name=name)


# buy page code is here   ##########################################################
list = []
list1 = []


@app.route("/stocksdata", methods=["GET", "POST"])
def stocksdata():
    Stock_name = request.form.get("Stock_name")
    list1.append(Stock_name)
    name = str(Stock_name) + str(".NS")
    try:
        stock_info = yf.Ticker(name).info
        market_price = stock_info["regularMarketPrice"]

        company_name = stock_info["longName"]
        list.append(company_name)
        change_in_price = round(
            market_price - stock_info["regularMarketPreviousClose"], 2
        )
        open = stock_info["regularMarketOpen"]
        high = stock_info["dayHigh"]
        low = stock_info["dayLow"]
        debt = stock_info["totalDebt"]
        dividend = stock_info["dividendRate"]
        gross_profit = stock_info["grossProfits"]
        recomm = stock_info["recommendationKey"]
        cashpershare = stock_info["totalCashPerShare"]
        business_summary = stock_info["longBusinessSummary"]
        return render_template(
            "stocksdata.html",
            Stock_name=Stock_name,
            market_price=market_price,
            company_name=company_name,
            change_in_price=change_in_price,
            open=open,
            high=high,
            low=low,
            debt=debt,
            cashpershare=cashpershare,
            dividend=dividend,
            gross_profit=gross_profit,
            recomm=recomm,
            business_summary=business_summary,
        )
    except:
        flash("Please Enter Correct Stock Symbol ")
        return redirect(url_for("home"))


# portfolio page code is here  ##############################################


@app.route("/Portfolio.html")
@login_required
def portfolio():
    Stocks = Portfolio.query.filter_by(email=current_user.email)
    return render_template(
        "Portfolio.html",
        yf=yf,
        Ticker=Ticker,
        info=info,
        holding=Stocks,
        str=str,
        round=round,
    )


# portfolio page code is here  ##############################################


@app.route("/report.html")
@login_required
def report():
    Stocks = Transaction.query.filter_by(email=current_user.email)
    return render_template("report.html", Stocks=Stocks)


#########################################################################


@app.route("/thanks", methods=["GET", "POST"])
@login_required
def thanks():
    if request.method == "POST":
        buy_price = request.form.get("buy_price")
        quantity = request.form.get("quantity")
        company_name = list.pop()
        Symbol = list1.pop()
        entry1 = Portfolio(
            buy_price=buy_price,
            quantity=quantity,
            company_name=company_name,
            Symbol=Symbol,
            email=current_user.email,
        )
        db.session.add(entry1)
        db.session.commit()
        return render_template("thanks.html")


###################################################################################


@app.route("/sell")
@login_required
def sell():
    Stock_id = request.args.get("sno")
    stock_to_sell = Portfolio.query.get(Stock_id)
    Symbol = stock_to_sell.Symbol
    stock_to_sell.sell_price = yf.Ticker(str(Symbol) + ".NS").info["regularMarketPrice"]
    stock_to_sell.profit = round(
        (float(stock_to_sell.sell_price) - float(stock_to_sell.buy_price))
        * int(stock_to_sell.quantity),
        2,
    )

    db.session.commit()
    entry = Transaction(
        buy_price=stock_to_sell.buy_price,
        quantity=stock_to_sell.quantity,
        company_name=stock_to_sell.company_name,
        sell_price=stock_to_sell.sell_price,
        profit=stock_to_sell.profit,
        Symbol=stock_to_sell.Symbol,
        email=stock_to_sell.email,
    )
    db.session.add(entry)
    db.session.commit()
    db.session.delete(stock_to_sell)
    db.session.commit()

    return redirect(url_for("portfolio"))


###################################################################################

if __name__ == "__main__":
    app.run(debug=True)
