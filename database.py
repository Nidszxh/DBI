import logging
from bPlusTree import BplusTree
import csv
from util import validate_entry, backup_data, restore_data, log_action

# Setting up logging for database operations
logging.basicConfig(filename="db_log.log", level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s", filemode='a')

class Database:
    def __init__(self, order):
        if not isinstance(order, int) or order < 2:
            raise ValueError("Order must be an integer greater than or equal to 2.")
        self.btree = BplusTree(order)
        log_action("Initialized database with B+ Tree of order", order)

    def insert(self, key, value):
        try:
            is_valid, message = validate_entry(key, value)
            if is_valid:
                self.btree.insert(key, value)
                log_action("Inserted key", key, value)
            else:
                logging.warning(f"Invalid entry: key={key}, value={value} - {message}")
        except Exception as e:
            logging.error(f"Error during insertion: key={key}, value={value}, error={e}")

    def search(self, key):
        try:
            log_action("Searching for key", key)
            result = self.btree.search(key)
            if result is None:
                logging.info(f"Key {key} not found.")
            else:
                logging.info(f"Found key {key}: {result}")
            return result
        except Exception as e:
            logging.error(f"Error during search for key={key}: {e}")
            return None

    def batch_insert(self, entries):
        if not isinstance(entries, list):
            logging.error("Entries must be a list of tuples.")
            return

        valid_entries = [entry for entry in entries if isinstance(entry, tuple) and len(entry) == 2]
        invalid_entries = [entry for entry in entries if entry not in valid_entries]

        for key, value in valid_entries:
            self.insert(key, value)

        if invalid_entries:
            logging.warning(f"Skipped invalid entries: {invalid_entries}")

    def delete(self, key):
        try:
            log_action("Attempting to delete key", key)
            self.btree.delete(key)
            logging.info(f"Key {key} deleted successfully.")
        except KeyError:
            logging.warning(f"Key {key} not found in the database.")
        except Exception as e:
            logging.error(f"Error during deletion: key={key}, error={e}")

    def range_search(self, lower_bound, upper_bound):
        try:
            if not (isinstance(lower_bound, int) and isinstance(upper_bound, int)):
                raise ValueError("Bounds must be integers.")
            if lower_bound > upper_bound:
                raise ValueError("Lower bound must not exceed upper bound.")

            result = []
            node = self.btree.root

            # Traverse to the first relevant node
            while not node.leaf:
                for i, key in enumerate(node.keys):
                    if lower_bound < key:
                        node = node.children[i]
                        break
                else:
                    node = node.children[-1]

            # Collect entries in the range
            while node:
                for key, value in node.keys:
                    if lower_bound <= key <= upper_bound:
                        result.append((key, value))
                    elif key > upper_bound:
                        return result
                node = node.next

            return result
        except Exception as e:
            logging.error(f"Error during range search: lower_bound={lower_bound}, upper_bound={upper_bound}, error={e}")
            return []

    def backup(self, backup_file):
        try:
            if not backup_file:
                raise ValueError("Backup file path is invalid.")
            backup_data(self.btree, backup_file)
            log_action("Backup successful to", backup_file)
        except Exception as e:
            logging.error(f"Error during backup to file={backup_file}: {e}")

    def restore(self, backup_file):
        try:
            if not backup_file:
                raise ValueError("Backup file path is invalid.")
            restore_data(self.btree, backup_file)
            log_action("Restored data from", backup_file)
        except Exception as e:
            logging.error(f"Error during restore from file={backup_file}: {e}")

    def export_to_csv(self, file_name="database_export.csv"):
        try:
            with open(file_name, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Key", "Value"])
                for key, value in self.btree.get_sorted_data():
                    writer.writerow([key, value])
            log_action("Exported database to CSV", file_name)
        except Exception as e:
            logging.error(f"Error during CSV export: file={file_name}, error={e}")

    def print_database(self):
        try:
            print("Current Database Entries:")
            for key, value in self.btree.get_sorted_data():
                print(f"Key: {key}, Value: {value}")
        except Exception as e:
            logging.error(f"Error during database print: {e}")

    def get_tree_structure(self):
        try:
            return self.btree.get_tree_structure()
        except Exception as e:
            logging.error(f"Error retrieving tree structure: {e}")
            return {}

