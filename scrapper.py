import requests


class Rutracker:
    USER = "fsdf"
    PASS = "fsdf"
    URL_AUTH = "rutracker.org/fsdf"
    URL_AUTH_POST = "rutracker.org/fsdf"

    def __init__(self):
        self.session = requests.session()

    def authenticate(self):
        #csrf ???
        self.session.post(self.URL_AUTH_POST, {"user": self.USER, "password": self.PASS})

    def is_authenticated(self) -> bool:
        pass

    def search(self, key: str):
        """

        :param key: string to search
        """
        pass

