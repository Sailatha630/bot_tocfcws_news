class article:
    def __init__(self, id, title, url, timestamp):
        self.id = id
        self.title = title
        self.url = (
            url.replace("prod-content-cdn", "www")
            .replace("content/chelseafc/", "")
            .replace(".html", "")
        )
        self.timestamp = timestamp

    def __repr__(self):
        return repr(self.id, self.title, self.url, self.timestamp)