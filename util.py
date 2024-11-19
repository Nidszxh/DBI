import logging
import os
import csv

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", filename='app.log', filemode='a')

def compare_keys(key1, key2):
    # Compare two keys and return a value indicating their relative order
    return (key1 > key2) - (key1 < key2)

def validate_entry(key, value):
    # Validate that key and value are in correct format
    if not isinstance(key, int):
        return False, "Key must be an integer."
    if not isinstance(value, str):
        return False, "Value must be a string."
    return True, "Valid entry."

def log_action(action, *args):
    # Log actions performed in the database or B+ Tree
    message = f"{action}: " + ", ".join(str(arg) for arg in args)
    logging.info(message)

def get_sorted_data(btree):
    # Return sorted data in the form of a list of tuples from the B+ Tree
    if btree.root is None:
        log_action("Tree is empty, no data to sort")
        return []
    data = []
    node = btree.root
    while node:
        for i in range(len(node.keys)):
            data.append((node.keys[i], node.values[i]))
        node = node.next  # Traverse through leaf nodes
    return sorted(data)

def backup_data(btree, backup_file):
    # Backup the B+ Tree data into a file
    try:
        backup_dir = os.path.dirname(backup_file)
        if not os.path.exists(backup_dir) and backup_dir:
            os.makedirs(backup_dir)

        with open(backup_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Key", "Value"])
            for key, value in get_sorted_data(btree):
                writer.writerow([key, value])

        log_action("Backup successful", backup_file)
    except Exception as e:
        log_action("Backup failed", e)

def restore_data(btree, backup_file):
    # Restore the B+ Tree data from a backup file
    try:
        if not os.path.exists(backup_file):
            raise FileNotFoundError(f"Backup file {backup_file} not found.")

        btree.clear()  # Ensure the tree is empty before restoring

        with open(backup_file, 'r', newline='') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                key, value = int(row[0]), row[1]
                is_valid, message = validate_entry(key, value)
                if is_valid:
                    btree.insert(key, value)  # Assuming insert method in B+ Tree
                else:
                    log_action("Invalid entry in restore", key, value, message)
        log_action("Restore successful", backup_file)
    except Exception as e:
        log_action("Restore failed", e)
