import tinydb

class User():
    def __init__(self, info):
        self.info = info
        self.lastmatch = None
    
    def save(self):
        db.set(self.info, self.lastmatch)


