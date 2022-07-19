import json

from flask import Flask, request
from news_crawler import similarity_cal, similarity_cal_single, crawl_by_url

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/recommend", methods=['POST'])
def recommend():
    print(request.json['data'])
    rs = similarity_cal(request.json['data'], request.json['recommendNum'], request.json['historyNum'])
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



@app.route("/crawl", methods=['POST'])
def crawl():
    # rs = similarity_cal_single(request.json['data'], request.json['recommendNum'])
    # rs_dict = {
    #     "data": rs
    # }
    # return rs_dict
    # data =
    if 'topicLv3' in request.json and request.json['topicLv3'] is not None:
        rs = crawl_by_url(request.json['url'], request.json['topicLv1'], request.json['topicLv2'], request.json['topicLv3'])
    elif 'topicLv2' in request.json and request.json['topicLv2'] is not None:
        rs = crawl_by_url(request.json['url'], request.json['topicLv1'], request.json['topicLv2'], None)
    else:
        rs = crawl_by_url(request.json['url'], request.json['topicLv1'], None, None)
    # rs = crawl_by_url(request.json['url'], request.json['topicLv1'], request.json['topicLv2'], request.json['topicLv3'])
    return rs


if __name__ == '__main__':
    app.run()