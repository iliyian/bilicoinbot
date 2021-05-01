import requests
from pyquery import PyQuery as pq

rank_url = 'https://www.bilibili.com/v/popular/rank/all'

def getTop100Videos():
    r = requests.get(rank_url)
    r.encoding='utf8'

    doc = pq(r.text)
    top_videos = []

    videos = doc.find('#app > div.rank-container > div.rank-list-wrap > ul > li').items()
    for video in videos:
        rank = video.attr('data-rank')
        aid = video.attr('data-id')
        top_videos.append({
            'rank': rank,
            'aid': aid,
            'title': video.find('div.content > div.info > a').text(),
        })
    return top_videos
