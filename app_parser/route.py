from app_parser import app


@app.route('/')
def test():
    return 'OK'

