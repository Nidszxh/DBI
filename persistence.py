import pickle
import os
from util import log_action


class PersistentDatabase:
    """Database with automatic persistence to disk"""
    
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
        """Load database from disk"""
        try:
            with open(self.db_file, 'rb') as f:
                self.db = pickle.load(f)
            log_action("Loaded database from", self.db_file)
        except Exception as e:
            log_action("Failed to load database", str(e), level="ERROR")
            from database import Database
            self.db = Database(self.order)
    
    def save(self):
        """Save database to disk"""
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
    
    def batch_insert(self, entries):
        result = self.db.batch_insert(entries)
        self.save()
        return result
    
    def range_search(self, lower_bound, upper_bound):
        return self.db.range_search(lower_bound, upper_bound)
    
    def get_all(self):
        return self.db.get_all()
    
    def clear(self):
        self.db.clear()
        self.save()
    
    def __len__(self):
        return len(self.db)
    
    def __contains__(self, key):
        return key in self.db
    
    def __getitem__(self, key):
        return self.db[key]
    
    def __setitem__(self, key, value):
        self.db[key] = value
        self.save()
    
    def __delitem__(self, key):
        del self.db[key]
        self.save()
    
    def __repr__(self):
        return f"PersistentDatabase(file={self.db_file}, {self.db})"
    
    def __getattr__(self, name):
        """Delegate all other methods to db"""
        return getattr(self.db, name)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()


# Usage example:
# with PersistentDatabase("mydb.dat", order=4) as db:
#     db.insert(1, "value")
#     # Automatically saved on exit