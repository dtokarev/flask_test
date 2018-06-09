from app_parser import app
from app_parser.domain.model import *


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Search': Search,
        'Config': Config,
    }

if __name__ == '__main__':
    app.run(port=8001, debug=True)
