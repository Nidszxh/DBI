from bPlusTree import BPlusTree
from util import validate_entry, backup_data, restore_data, export_to_json, import_from_json, log_action


class Database:
    """Database wrapper for B+ Tree with additional utilities"""
    
    def __init__(self, order):
        if not isinstance(order, int) or order < 3:
            raise ValueError("Order must be an integer >= 3")
        
        self.btree = BPlusTree(order)
        log_action("Initialized database with order", order)

    def insert(self, key, value):
        """Insert a key-value pair into the database"""
        try:
            is_valid, message = validate_entry(key, value)
            if not is_valid:
                log_action("Invalid entry", key, message, level="WARNING")
                return False
            
            self.btree.insert(key, value)
            return True
        except Exception as e:
            log_action("Insert error", key, str(e), level="ERROR")
            return False

    def search(self, key):
        """Search for a key in the database"""
        try:
            return self.btree.search(key)
        except Exception as e:
            log_action("Search error", key, str(e), level="ERROR")
            return None

    def delete(self, key):
        """Delete a key from the database"""
        try:
            return self.btree.delete(key)
        except Exception as e:
            log_action("Delete error", key, str(e), level="ERROR")
            return False

    def batch_insert(self, entries):
        """Insert multiple key-value pairs at once"""
        if not isinstance(entries, list):
            log_action("Batch insert failed: entries must be a list", level="ERROR")
            return 0
        
        success_count = 0
        for entry in entries:
            if isinstance(entry, tuple) and len(entry) == 2:
                if self.insert(entry[0], entry[1]):
                    success_count += 1
        
        log_action("Batch insert completed", f"{success_count}/{len(entries)} succeeded")
        return success_count

    def range_search(self, lower_bound, upper_bound):
        """Search for all keys in the specified range"""
        try:
            if not (isinstance(lower_bound, (int, float)) and isinstance(upper_bound, (int, float))):
                raise ValueError("Bounds must be numbers")
            if lower_bound > upper_bound:
                raise ValueError("Lower bound must not exceed upper bound")
            
            return self.btree.range_query(lower_bound, upper_bound)
        except Exception as e:
            log_action("Range search error", str(e), level="ERROR")
            return []

    def backup(self, backup_file):
        """Backup database to CSV file"""
        return backup_data(self.btree, backup_file)

    def restore(self, backup_file):
        """Restore database from CSV file"""
        return restore_data(self.btree, backup_file)

    def export_json(self, json_file):
        """Export database to JSON file"""
        return export_to_json(self.btree, json_file)

    def import_json(self, json_file):
        """Import database from JSON file"""
        return import_from_json(self.btree, json_file)

    def get_all(self):
        """Get all key-value pairs in sorted order"""
        return self.btree.get_all()

    def clear(self):
        """Clear all data from the database"""
        self.btree.clear()

    def __len__(self):
        return len(self.btree)

    def __contains__(self, key):
        return key in self.btree

    def __getitem__(self, key):
        return self.btree[key]

    def __setitem__(self, key, value):
        self.insert(key, value)

    def __delitem__(self, key):
        if not self.delete(key):
            raise KeyError(f"Key {key} not found")

    def __repr__(self):
        return f"Database({self.btree})"