import json
import gzip
import logging
from functools import lru_cache
from bPlusTree import BplusTree
import csv

logging.basicConfig(filename="db_log.log", level=logging.INFO, 
                    format="%(asctime)s [%(levelname)s] %(message)s", filemode='a')

class Database:
    def __init__(self, order):
        logging.info("Initializing database with B+ Tree of order %s", order)
        self.btree = BplusTree(order)

    def insert(self, key, value):
        """Insert a key-value pair into the database."""
        self.validate_entry(key, value)
        self.btree.insert(key, value)
        logging.info(f"Inserted key: {key}, value: {value}")

    def validate_entry(self, key, value):
        """Validate the key and value for the database."""
        if not isinstance(key, int):
            raise ValueError("Key must be an integer.")
        if not isinstance(value, (str, int, float, dict, list)):
            raise ValueError("Value must be a string, integer, float, dictionary, or list.")

    @lru_cache(maxsize=100)
    def search_cached(self, key):
        """Search for a key using cache."""
        return self.btree.search(key)

    def batch_insert(self, entries):
        """Insert multiple key-value pairs into the database."""
        if not isinstance(entries, list):
            raise ValueError("Entries must be a list of tuples.")
        
        for entry in entries:
            if not isinstance(entry, tuple) or len(entry) != 2:
                raise ValueError("Each entry must be a tuple (key, value).")
            key, value = entry
            self.insert(key, value)

    def range_search(self, lower_bound, upper_bound):
        """Retrieve all key-value pairs within a specified key range."""
        if not isinstance(lower_bound, int) or not isinstance(upper_bound, int):
            raise ValueError("Both bounds must be integers.")
        if lower_bound > upper_bound:
            raise ValueError("Lower bound must not exceed upper bound.")
        
        result = []
        for key in range(lower_bound, upper_bound + 1):
            value = self.btree.search(key)
            if value is not None:
                result.append((key, value))
        return result

    def query(self, query_string):
        """Simple query parser for filtering keys."""
        try:
            if "WHERE" in query_string:
                conditions = query_string.split("WHERE")[1].strip().split("AND")
                lower_bound, upper_bound = [int(cond.split(">=")[1]) for cond in conditions]
                return self.range_search(lower_bound, upper_bound)
        except Exception as e:
            logging.error(f"Query error: {e}")
            return None

    def backup(self, backup_file):
        """Backup the current database to a compressed file."""
        try:
            with gzip.open(backup_file + '.gz', 'wt', encoding="utf-8") as file:
                data = {key: value for key, value in self.btree.get_sorted_data()}
                json.dump(data, file, indent=4)
            logging.info(f"Backup completed successfully to {backup_file}.gz")
        except Exception as e:
            logging.error(f"Backup error: {e}")

    def restore(self, backup_file):
        """Restore the database from a backup file."""
        try:
            with gzip.open(backup_file + '.gz', 'rt', encoding="utf-8") as file:
                data = json.load(file)
                for key, value in data.items():
                    self.validate_entry(int(key), value)
                    self.btree.insert(int(key), value)
            logging.info(f"Restoration completed successfully from {backup_file}.gz")
        except FileNotFoundError:
            logging.error(f"Error: The backup file '{backup_file}' was not found.")
        except json.JSONDecodeError:
            logging.error("Error: Failed to decode JSON from the backup file.")
        except Exception as e:
            logging.error(f"An unexpected error occurred during restore: {e}")

    def export_to_csv(self, file_name="database_export.csv"):
        """Export database entries to a CSV file."""
        try:
            with open(file_name, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Key", "Value"])
                for key, value in self.btree.get_sorted_data():
                    writer.writerow([key, value])
            logging.info(f"Export to CSV completed successfully: {file_name}")
        except Exception as e:
            logging.error(f"Error exporting to CSV: {e}")

    def print_database(self):
        """Print all key-value pairs in the database."""
        print("Current Database Entries:")
        for key, value in self.btree.get_sorted_data():
            print(f"Key: {key}, Value: {value}")
    
    def get_tree_structure(self):
        """Return a JSON representation of the B+ Tree for visualization."""
        return self.btree.to_dict()  # Assuming `to_dict` is a method to convert the B+ Tree structure to a dict
