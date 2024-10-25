from database import Database
import time

def test_database():
    print("Initializing database...")
    db = Database(order=3)

    try:
        # Test single insertions
        print("\nTesting single insertions:")
        test_data = [
            (1, "First"),
            (2, "Second"),
            (3, "Third")
        ]
        for key, value in test_data:
            print(f"Inserting key={key}, value={value}")
            db.insert(key, value)
            time.sleep(0.5)  # Small delay to see the progress

        # Print current state
        print("\nCurrent database contents:")
        db.print_database()

        # Test batch insertion
        print("\nTesting batch insertion:")
        batch_data = [
            (4, "Fourth"),
            (5, "Fifth"),
            (6, "Sixth")
        ]
        print("Inserting batch:", batch_data)
        db.batch_insert(batch_data)

        # Print updated state
        print("\nDatabase contents after batch insertion:")
        db.print_database()

        # Test search
        print("\nTesting search functionality:")
        test_keys = [1, 3, 5]
        for key in test_keys:
            result = db.search_cached(key)
            print(f"Searching for key {key}: {result}")

        # Test range search
        print("\nTesting range search (2-5):")
        range_result = db.range_search(2, 5)
        for key, value in range_result:
            print(f"Found in range: key={key}, value={value}")

        # Test backup and restore
        print("\nTesting backup and restore:")
        print("Creating backup...")
        db.backup("test_backup")

        print("Creating new database and restoring from backup...")
        new_db = Database(order=3)
        new_db.restore("test_backup")

        print("\nContents of restored database:")
        new_db.print_database()

        # Test CSV export
        print("\nTesting CSV export:")
        db.export_to_csv("database_export.csv")
        print("CSV export completed. Check database_export.csv")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database()