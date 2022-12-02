from Utilities import db


class Building:
    buildings = db.buildings
    name = ''

    def __int__(self, name):
        self.name = name
