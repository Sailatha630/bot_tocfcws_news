class article:
    def __init__(self, id, title, url, timestamp):
        self.id = id
        self.title = title
        self.url = (
            url.replace("/en", "https://chelseafc.com/en/")
        )
        self.timestamp = timestamp

    def __repr__(self):
        return repr(self.id, self.title, self.url, self.timestamp)
