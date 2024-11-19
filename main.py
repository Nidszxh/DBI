import logging
from database import Database
import os
import traceback
from util import log_action
from datetime import datetime

# Set up logging for the main function
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def test_insertions(db):
    test_data = [(1, "First Entry"), (2, "Second Entry"), (3, "Third Entry")]
    for key, value in test_data:
        try:
            db.insert(key, value)
            logging.info(f"Inserted key={key}, value='{value}'")
        except Exception as e:
            logging.error(f"Error inserting key={key}, value='{value}': {e}")

def test_search(db, search_keys):
    for key in search_keys:
        try:
            result = db.search(key)
            print(f"Search for key={key}: {'Found: ' + str(result) if result else 'Not Found'}")
            logging.info(f"Search for key={key}: {'Found' if result else 'Not Found'}")
        except Exception as e:
            logging.error(f"Error searching for key={key}: {e}")

def test_range_search(db, lower, upper):
    try:
        range_results = db.range_search(lower, upper)
        if range_results:
            for key, value in range_results:
                print(f"Found in range: key={key}, value='{value}'")
        else:
            print("No entries found in the specified range.")
        logging.info(f"Range search from {lower} to {upper} returned {len(range_results)} results.")
    except Exception as e:
        logging.error(f"Error performing range search from {lower} to {upper}: {e}")

def test_deletion(db):
    delete_keys = [1, 6]  # Including a key that exists and one that doesn't
    for key in delete_keys:
        try:
            db.delete(key)
            logging.info(f"Deleted key={key}")
        except Exception as e:
            logging.error(f"Error deleting key={key}: {e}")

def test_backup_restore(db, backup_file):
    try:
        if not os.path.exists(backup_file):  # Check if the file already exists before backup
            db.backup(backup_file)
            logging.info(f"Database backed up to file: {backup_file}")
            print(f"Database backed up to file: {backup_file}")
        else:
            logging.warning(f"Backup file {backup_file} already exists.")
        
        # Ensure the backup file exists before restoring
        if os.path.exists(backup_file):
            new_db = Database(order=3)
            new_db.restore(backup_file)
            logging.info(f"Restored database from file: {backup_file}")
            print("\nContents of the restored database:")
            new_db.print_database()
        else:
            logging.error(f"Backup file {backup_file} does not exist for restore.")
            print(f"Error: Backup file {backup_file} does not exist for restore.")

    except Exception as e:
        logging.error(f"Error during backup/restore process: {e}")

def test_csv_export(db, csv_file):
    try:
        db.export_to_csv(csv_file)
        logging.info(f"CSV export completed. File: {csv_file}")
        print(f"CSV export completed. Check the file {csv_file}.")
    except Exception as e:
        logging.error(f"Error during CSV export to {csv_file}: {e}")

def main():
    try:
        db = Database(order=3)

        # Testing single insertions
        print("\nTesting single insertions:")
        test_insertions(db)

        # Display current tree structure after insertions
        print("\nTree structure after single insertions:")
        print(db.get_tree_structure())

        # Display the database contents after insertions
        print("\nCurrent database contents:")
        db.print_database()

        # Test search functionality
        print("\nTesting search functionality:")
        test_search(db, [1, 3, 7])

        # Test range search
        print("\nTesting range search from key 2 to 5:")
        test_range_search(db, 2, 5)

        # Test deletion functionality
        print("\nTesting delete functionality:")
        test_deletion(db)
        print("Tree structure after deletions:")
        print(db.get_tree_structure())

        # Test backup and restore functionality
        backup_file = f"test_backup_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        print("\nTesting backup and restore functionality:")
        test_backup_restore(db, backup_file)

        # Test CSV export functionality
        csv_file = "database_export.csv"
        print(f"\nTesting export to CSV file: {csv_file}")
        test_csv_export(db, csv_file)

        # Cleanup: Delete backup file after restore
        if os.path.exists(backup_file):
            os.remove(backup_file)
            log_action(f"Backup file {backup_file} deleted after restore")

    except Exception as e:
        print(f"An error occurred during testing: {e}")
        logging.error(f"An error occurred during testing: {e}")
        traceback.print_exc()

    print("\nFinal state of the database:")
    db.print_database()

if __name__ == "__main__":
    main()
    