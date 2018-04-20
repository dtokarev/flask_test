import feedparser
from flask import Flask, render_template, request

app = Flask(__name__)

media_dict = {
    'default': "http://feeds.bbci.co.uk/news/rss.xml",
    'bbc': "http://feeds.bbci.co.uk/news/rss.xml",
}


@app.route('/')
def index():
    media_name = request.args.get('media', 'default')
    feeds = feedparser.parse(media_dict.get(media_name))

    model = []
    for feed in feeds.get('entries', []):
        model.append({
            'title': feed.get('title'),
            'summary': feed.get('summary'),
        })
    return render_template('home/index.html', model=model)

if __name__ == '__main__':
    app.run(port=8001, debug=True)
