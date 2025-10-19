import pickle
import os
from util import log_action


class PersistentDatabase:
    # Database with automatic persistence to disk
    
    def __init__(self, db_file, order=4):
        self.db_file = db_file
        self.order = order
        self.db = None
        
        if os.path.exists(db_file):
            self.load()
        else:
            from database import Database
            self.db = Database(order)
            log_action("Created new persistent database", db_file)
    
    def load(self):
        try:
            with open(self.db_file, 'rb') as f:
                self.db = pickle.load(f)
            log_action("Loaded database from", self.db_file)
        except Exception as e:
            log_action("Failed to load database", str(e), level="ERROR")
            from database import Database
            self.db = Database(self.order)
    
    def save(self):
        try:
            with open(self.db_file, 'wb') as f:
                pickle.dump(self.db, f)
            log_action("Saved database to", self.db_file)
        except Exception as e:
            log_action("Failed to save database", str(e), level="ERROR")
    
    def insert(self, key, value):
        result = self.db.insert(key, value)
        self.save()
        return result
    
    def delete(self, key):
        result = self.db.delete(key)
        self.save()
        return result
    
    def search(self, key):
        return self.db.search(key)
    
    def __getattr__(self, name):
        return getattr(self.db, name)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()


# Usage example:
# with PersistentDatabase("mydb.dat", order=4) as db:
#     db.insert(1, "value")
#     # Automatically saved on exit