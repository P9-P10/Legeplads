from Applications.DatabaseRepresenations.Table import Table
from Applications.DatabaseRepresenations.Column import Column

class Change:
    def __init__(self, old, new):
        self.old = old
        self.new = new

