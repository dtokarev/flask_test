from src import app


@app.route("/add", methods=["POST", "GET"])
def add_torrent():
    return "OK"