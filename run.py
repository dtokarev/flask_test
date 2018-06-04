from app import app, db
from app.domain.model import *


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Search': Search,
        'Config': Config,
    }

if __name__ == '__main__':
    app.run(port=8001, debug=True)
