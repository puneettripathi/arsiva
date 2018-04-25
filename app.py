"""
HeadURL:  $HeadURL$
Last changed by:  $Author$
Last changed on:  $Date$

(c)  2018 BlackRock.  All rights reserved.

Description:

description
"""
__version__ = '$Revision$'


import sqlite3
from flask import Flask
from flask import render_template, jsonify, request
import requests
from models import *
from response import *
import random
import json
import pandas as pd

app_key = "FA7LT15XX0KG0BZP"


@app.route('/')
def hello_world():
    """
    Sample hello world
    """
    return render_template('home.html')


get_random_response = lambda intent: random.choice(response[intent])
proxies = {"http": "http://del-webproxy.blackrock.com:8080",
           "https": "https://del-webproxy.blackrock.com:8080"}


def format_entities(entities):
    """
    formats entities to key value pairs
    """
    e = {"day": None, "time": None, "place": None}
    for entity in entities:
        e[entity["entity"]] = entity["value"]
    return e


def get_ticker(name):
    conn = sqlite3.connect('company.db')
    cur = conn.cursor()
    cur.execute("select ticker from ticker_lookup where lower(COMPANY_NAME) like lower('" + name + "%')")
    lookup = [i[0] for i in cur.fetchall()]
    return lookup


def get_stock_information(ticker):
    # conn = sqlite3.connect('company.db')
    # cur = conn.cursor()
    # cur.execute("select ticker from ticker_lookup where lower(COMPANY_NAME) like lower('" + ticker + "%')")
    lookup = get_ticker(ticker)
    # print(lookup)
    if len(lookup) > 0:
        for tckr in lookup:
            url = "https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol="+ tckr +"&apikey=FA7LT15XX0KG0BZP"
            # print("url is =>"+url)
            jsondata = json.loads(requests.get(url, proxies=proxies).text)["Monthly Time Series"]
            df = pd.DataFrame(jsondata).T.sort_index(ascending=False)[0:52]
            newdf = pd.DataFrame()
            newdf['open'] = df["1. open"].astype("float")
            newdf['high'] = df["2. high"].astype("float")
            newdf['low'] = df["3. low"].astype("float")
            newdf['close'] = df["4. close"].astype("float")
            newdf.plot(figsize=(5,4)).figure.savefig("static\\images\\monthly_"+ticker)
            stat1 = "52 weeks stats - \n" + "\n".join(str(newdf.agg({"open": "min", "close": "max", "low": "min", "high": "max"})).split("\n")[0:-1])
            stat1 += """<img src="static/images/monthly_""" + ticker + """.png" height=300 width=400 \>"""

            url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=" + tckr + "&apikey=FA7LT15XX0KG0BZP"
            # print("url is =>" + url)
            # print()
            jsondata = json.loads(requests.get(url, proxies=proxies).text)["Time Series (Daily)"]
            df = pd.DataFrame(jsondata).T.sort_index(ascending=False)[0:90]
            newdf = pd.DataFrame()
            newdf['open'] = df["1. open"].astype("float")
            newdf['high'] = df["2. high"].astype("float")
            newdf['low'] = df["3. low"].astype("float")
            newdf['close'] = df["4. close"].astype("float")
            newdf.plot(figsize=(5,4)).figure.savefig("static\\images\\daily_" + ticker)
            stat1 += "\n" + "*"*15 + "\n90 days stats - \n" + "\n".join(str(newdf.agg({"open": "min", "close": "max", "low": "min", "high": "max"})).split("\n")[0:-1])
            stat1 += """<img src="static/images/daily_""" + ticker + """.png" height=300 width=400 \>"""
    else:
            stat1 = "Could not find that share, why don't you try it's ticker"

    return stat1


def get_full_investment_resp(entity):
    pass


def get_technical_analyis(stockname, analysis_type=None, interval="weekly"):
    lookup = get_ticker(stockname)

    if analysis_type is None:
        analysis_type = "SMA"
    tckr = lookup[0]
    url = "https://www.alphavantage.co/query?function="+analysis_type+"&symbol="+tckr+"&interval="+interval+"&apikey=" + app_key + "&time_period=10&series_type=open"
    jsondata = json.loads(requests.get(url, proxies=proxies).text)["Technical Analysis: " + analysis_type]
    df = pd.DataFrame(jsondata).T.sort_index(ascending=False)[0:90]
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df[0:52].plot(figsize=(5, 4)).figure.savefig("static\\images\\technical_" + tckr +"_" + interval + "_" + analysis_type)
    stat = analysis_type + " Analysis for " + tckr + " for last 52 weeks - \n"
    stat += """<img src="static/images/technical_""" + tckr +"_" + interval + "_" + analysis_type + """.png" height=300 width=400 \>"""
    return stat


@app.route('/chat', methods=["POST"])
def chat():
    """
    chat end point that performs NLU using rasa.ai
    and constructs response from response.py
    """
    try:
        response = requests.get("http://localhost:5000/parse",
                                params={"q": request.form["text"]})
        response = response.json()
        # print(response)
        intent = response["intent"]["name"]
        # print(intent)
        entities = format_entities(response["entities"])
        # print(entities)
        if intent == "investment_search":
            response_text = "No comment yet"
        elif intent == "investment_search_full":
            response_text = "No comment yet"
        elif intent == "technical_analysis":
            resp_text = response["text"]
            tech_analysis = ["SMA", "EMA", "WMA", "DEMA", "TRIMA", "MACD", "STOCH", "RSI", "ADX", "CCI", "AROON"]
            analysis_list = [i for i in resp_text.split() if i.upper() in tech_analysis]
            print(analysis_list)
            if len(analysis_list) > 0:
                response_text = "\n".join([get_technical_analyis(entities['shares'], analysis_type=anlys) for anlys in analysis_list])
            else:
                response_text = "Sorry, couldn't find anything for - " + resp_text
        elif intent == "stock_ideas":
            response_text = get_stock_information(entities['shares'])
        else:
            response_text = get_random_response(intent)
        return jsonify({"status": "success",
                        "response": response_text})
    except Exception as e:
        # print(e)
        return jsonify({"status": "success",
                        "response": "Sorry I couldn't understand that, please try again."})


app.config["DEBUG"] = True
if __name__ == "__main__":
    app.run(port=8000)
