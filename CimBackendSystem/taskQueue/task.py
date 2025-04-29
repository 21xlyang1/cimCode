from datetime import datetime

class Task:
    def __init__(self, image, Cameraid, location, timestamp=None):
        self.image = image
        self.Cameraid = Cameraid
        self.location = location
        self.timestamp = timestamp or datetime.now()

    def __repr__(self):
        return f"Task(id={self.Cameraid}, location={self.location}, timestamp={self.timestamp})"
