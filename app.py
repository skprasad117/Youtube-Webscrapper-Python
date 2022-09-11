from flask import Flask, render_template, request
from flask_cors import cross_origin
import custompakage
import channels

app = Flask(__name__)


@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homepage():
    return render_template("index.html")


@app.route('/review', methods=['POST', 'GET'])  # route to show the review comments in a web UI
@cross_origin()
def index():
    try:
        if request.method == "POST":
            url = request.form['content']
            length = request.form['length']
            print(url, type(url), length, type(length))
            if custompakage.fetch_content_db(url):
                print("data present in db")
                fetched = custompakage.fetch_db(url)
                print("fetched data", fetched)
                fetched["status"] = "Data fetched from db"
                fetched["askedfor"] = length
                msg = render_template("results.html", reviews=fetched)
            else:
                print("data not found. start scrapping.....")
                scrap(url, length)
                fetched = custompakage.fetch_db(url)
                fetched["status"] = "Data scrapped from youtube and successfully saved into db"
                msg = render_template("results.html", reviews=fetched)
            return msg
        else:
            return render_template("index.html")
    except Exception as e:
        print("error occurring at app.py index", e)
        return render_template("index.html")


def scrap(url, length):
    url = url
    length = length
    try:
        print(url, type(url), length, type(length))
        bucket1 = channels.begin(url, length)
        a = custompakage.push_channel_info(bucket1)
        print(a)
        print("successfully scrapped")
    except Exception as e:
        print("error occurring at app.py index", e)
        return render_template("index.html")


@app.route('/comments', methods=['POST', 'GET'])  # route to show the review comments in a web UI
@cross_origin()
def comments():
    try:
        if request.method == "POST":
            videoid = request.form['videoid']
            channel = request.form['channel']
            comments_list = custompakage.comments_fetch_db(videoid, channel)
            msg = render_template("comments.html", reviews=comments_list)

        else:
            msg = render_template("index.html")
        return msg

    except Exception as e:
        print("error occurring at app.py index", e)
        return render_template("index.html")


@app.route('/scrapagain', methods=['POST', 'GET'])
@cross_origin()
def scrapagain():
    try:
        if request.method == "POST":
            print("scrap again request made")

            url = request.form['link']
            length = request.form['length']

            print(url, type(url))
            print(length, type(length))

            scrap(url, length)
            fetched = custompakage.fetch_db(url)
            fetched["status"] = "Data scrapped from channel and successfully updated into db"
            msg = render_template("results.html", reviews=fetched)
            print("successfully")
            return msg
        else:
            return render_template("index.html")

    except Exception as e:
        print("error occurring at app.py index", e)
        return render_template("index.html")


if __name__ == "__main__":
    # app.run(host='127.0.0.1', port=8001, debug=True)
    app.run(debug=False)
