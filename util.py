import json
import os
import logging
from datetime import datetime

# Data Validation Utilities
def validate_key(key):
    #To check if the key is a valid integer.
    if not isinstance(key, int):
        raise ValueError("Key must be an integer.")
    return True

def validate_value(value):
    #To check if the values are of acceptable types.
    if not isinstance(value, (str, int, float)):
        raise ValueError("Value must be a string, integer, or float.")
    return True

# Serialization/Deserialization
def serialize(data, filename):
    #Converts data to JSON and writes it to a file.
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Data successfully written to {filename}.")
    except Exception as e:
        print(f"Error while serializing data: {e}")

def deserialize(filename):
    #Reads JSON data from a file and Converts it to back as a Python objects.
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File {filename} not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {filename}.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None

# Key/Range Checks
def withinBounds(key, lower_bound, upper_bound):
    #To check if the key is within the range.
    return lower_bound <= key <= upper_bound

def compareKeys(key1, key2):
    if key1 == key2:
        return 0
    elif key1 < key2:
        return -1
    else:
        return 1

def generate_backup_filename():
    return f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

def print_operation_status(operation, success):
    status = "succeeded" if success else "failed"
    print(f"{operation.capitalize()} {status}.")

# Error Handling
def handle_file_not_found(filepath):
    """Handles file not found error."""
    print(f"Error: The file '{filepath}' does not exist.")

def handle_invalid_data_type(data_type):
    """Handles invalid data type errors."""
    print(f"Error: Invalid data type '{data_type}' provided.")

# Logging Utility
def setup_logging(log_file='app.log'):
    """Sets up logging configuration."""
    logging.basicConfig(filename=log_file,
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def log_operation(message):
    """Logs a message indicating an operation status."""
    logging.info(message)

# Backup and Restore Functions
def create_backup(data, backup_dir='backups'):
    """Creates a backup of the given data."""
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    backup_filename = generate_backup_filename()
    serialize(data, os.path.join(backup_dir, backup_filename))
    log_operation(f"Backup created: {backup_filename}")

def restore_from_backup(backup_filename, backup_dir='backups'):
    """Restores data from a backup file."""
    restored_data = deserialize(os.path.join(backup_dir, backup_filename))
    if restored_data is not None:
        log_operation(f"Data restored from backup: {backup_filename}")
    return restored_data
