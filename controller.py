from flask import Flask, request
from news_crawler import similarity_cal, similarity_cal_single

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/recommend", methods=['POST'])
def recommend():
    print(request.json['data'])
    rs = similarity_cal(request.json['data'], request.json['recommendNum'])
    rs_dict = {
        "data": rs
    }
    return rs_dict
    # return rs


@app.route("/recommend/single", methods=['POST'])
def recommend_single():
    print(request.json['data'])
    rs = similarity_cal_single(request.json['data'], request.json['recommendNum'])
    rs_dict = {
        "data": rs
    }
    return rs_dict


if __name__ == '__main__':
    app.run()