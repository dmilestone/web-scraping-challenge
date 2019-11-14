from flask import Flask, render_template, redirect, jsonify
from flask_pymongo import PyMongo
import scrape_mars
import sys

app = Flask(__name__)

mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_db")

@app.route("/")
def index():
    mars_data = mongo.db.mars.find_one()
    # print(mars)
    return render_template("index.html", data=mars_data)

@app.route("/scrape")
def scrape():  
    mars_scrape = scrape_mars.scrape()
    print(mars_scrape)
    mongo.db.mars.update({}, mars_scrape, upsert=True)
    return redirect("http://localhost:5000/", code=302)

if __name__ == "__main__":
    app.run(debug=True)