from database import Database
from util import get_statistics
import os


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_basic_operations():
    """Test basic insert, search, and delete operations"""
    print_section("TEST 1: Basic Operations")
    
    db = Database(order=4)
    
    # Test insertions
    print("Inserting keys: 10, 20, 5, 15, 25, 30, 35, 40")
    test_data = [(10, "ten"), (20, "twenty"), (5, "five"), (15, "fifteen"),
                 (25, "twenty-five"), (30, "thirty"), (35, "thirty-five"), (40, "forty")]
    
    for key, value in test_data:
        db.insert(key, value)
    
    print(f"✓ Inserted {len(test_data)} entries")
    print(f"Database size: {len(db)}")
    
    # Test search
    print("\nSearching for keys: 15, 25, 100")
    print(f"  Key 15: {db.search(15)}")
    print(f"  Key 25: {db.search(25)}")
    print(f"  Key 100: {db.search(100)}")
    
    # Test contains
    print(f"\nIs 20 in database? {20 in db}")
    print(f"Is 100 in database? {100 in db}")
    
    # Test delete
    print("\nDeleting key 20...")
    db.delete(20)
    print(f"Is 20 still in database? {20 in db}")
    print(f"Database size after deletion: {len(db)}")
    
    return db


def test_dict_interface():
    """Test dictionary-like interface"""
    print_section("TEST 2: Dictionary-like Interface")
    
    db = Database(order=4)
    
    # Test setitem
    print("Using dict-like syntax: db[1] = 'one', db[2] = 'two'")
    db[1] = "one"
    db[2] = "two"
    db[3] = "three"
    
    # Test getitem
    print(f"\nAccessing values:")
    print(f"  db[1] = {db[1]}")
    print(f"  db[2] = {db[2]}")
    
    # Test update
    print(f"\nUpdating: db[2] = 'TWO'")
    db[2] = "TWO"
    print(f"  db[2] = {db[2]}")
    
    # Test delitem
    print(f"\nDeleting: del db[3]")
    del db[3]
    print(f"Is 3 in database? {3 in db}")
    
    return db


def test_batch_operations():
    """Test batch insert operations"""
    print_section("TEST 3: Batch Operations")
    
    db = Database(order=4)
    
    # Batch insert
    entries = [(i, f"value_{i}") for i in range(1, 21)]
    print(f"Batch inserting {len(entries)} entries...")
    success_count = db.batch_insert(entries)
    print(f"✓ Successfully inserted {success_count} entries")
    print(f"Database size: {len(db)}")
    
    # Test with invalid entries
    print("\nTesting with some invalid entries...")
    mixed_entries = [(21, "valid"), ("invalid", "bad_key"), (22, None), (23, "valid")]
    success_count = db.batch_insert(mixed_entries)
    print(f"✓ Inserted {success_count} out of {len(mixed_entries)} entries")
    
    return db


def test_range_queries():
    """Test range query functionality"""
    print_section("TEST 4: Range Queries")
    
    db = Database(order=4)
    
    # Insert test data
    for i in range(1, 21):
        db.insert(i, f"value_{i}")
    
    print("Database contains keys 1-20")
    
    # Test various ranges
    print("\nRange [5, 10]:")
    results = db.range_search(5, 10)
    for key, value in results:
        print(f"  {key}: {value}")
    
    print(f"\nRange [15, 25] (extends beyond data):")
    results = db.range_search(15, 25)
    print(f"  Found {len(results)} entries")
    
    print(f"\nRange [100, 200] (no data):")
    results = db.range_search(100, 200)
    print(f"  Found {len(results)} entries")
    
    return db


def test_backup_restore():
    """Test backup and restore functionality"""
    print_section("TEST 5: Backup & Restore")
    
    # Create and populate database
    db = Database(order=4)
    print("Creating database with 10 entries...")
    for i in range(1, 11):
        db.insert(i * 10, f"value_{i*10}")
    
    print(f"Original database size: {len(db)}")
    original_data = db.get_all()
    print(f"Sample data: {original_data[:3]}")
    
    # Backup to CSV
    backup_file = "test_backup.csv"
    print(f"\nBacking up to {backup_file}...")
    success = db.backup(backup_file)
    print(f"✓ Backup {'successful' if success else 'failed'}")
    
    # Create new database and restore
    print("\nCreating new database and restoring...")
    new_db = Database(order=4)
    success = new_db.restore(backup_file)
    print(f"✓ Restore {'successful' if success else 'failed'}")
    
    restored_data = new_db.get_all()
    print(f"Restored database size: {len(new_db)}")
    print(f"Data matches: {original_data == restored_data}")
    
    # Cleanup
    if os.path.exists(backup_file):
        os.remove(backup_file)
        print(f"\n✓ Cleaned up {backup_file}")
    
    return db


def test_json_export_import():
    """Test JSON export and import functionality"""
    print_section("TEST 6: JSON Export & Import")
    
    # Create and populate database
    db = Database(order=4)
    print("Creating database with 8 entries...")
    data = [(5, "five"), (10, "ten"), (15, "fifteen"), (20, "twenty"),
            (25, "twenty-five"), (30, "thirty"), (35, "thirty-five"), (40, "forty")]
    
    for key, value in data:
        db.insert(key, value)
    
    print(f"Original database size: {len(db)}")
    
    # Export to JSON
    json_file = "test_export.json"
    print(f"\nExporting to {json_file}...")
    success = db.export_json(json_file)
    print(f"✓ Export {'successful' if success else 'failed'}")
    
    # Import to new database
    print("\nImporting to new database...")
    new_db = Database(order=4)
    success = new_db.import_json(json_file)
    print(f"✓ Import {'successful' if success else 'failed'}")
    print(f"Imported database size: {len(new_db)}")
    
    # Verify data
    print("\nVerifying imported data:")
    for key, value in [(5, "five"), (20, "twenty"), (40, "forty")]:
        result = new_db.search(key)
        print(f"  Key {key}: {result} {'✓' if result == value else '✗'}")
    
    # Cleanup
    if os.path.exists(json_file):
        os.remove(json_file)
        print(f"\n✓ Cleaned up {json_file}")
    
    return db


def test_statistics():
    """Test statistics gathering"""
    print_section("TEST 7: Tree Statistics")
    
    db = Database(order=4)
    
    print("Inserting 15 entries...")
    for i in range(1, 16):
        db.insert(i * 5, f"value_{i*5}")
    
    stats = get_statistics(db.btree)
    
    print("\nTree Statistics:")
    print(f"  Size: {stats.get('size', 0)} entries")
    print(f"  Order: {stats.get('order', 'N/A')}")
    print(f"  Height: {stats.get('height', 0)}")
    print(f"  Leaf nodes: {stats.get('leaf_nodes', 0)}")
    print(f"  Internal nodes: {stats.get('internal_nodes', 0)}")
    
    return db


def test_validation():
    """Test tree validation"""
    print_section("TEST 8: Tree Validation")
    
    db = Database(order=4)
    
    # Insert and delete to create a complex tree
    print("Creating complex tree structure...")
    for i in range(1, 26):
        db.insert(i, f"value_{i}")
    
    print(f"Inserted 25 entries")
    
    # Delete some entries
    for i in [5, 10, 15, 20]:
        db.delete(i)
    
    print(f"Deleted 4 entries")
    print(f"Current size: {len(db)}")
    
    # Validate
    print("\nValidating tree structure...")
    is_valid = db.btree.validate()
    print(f"✓ Tree is {'VALID' if is_valid else 'INVALID'}")
    
    return db


def test_edge_cases():
    """Test edge cases and error handling"""
    print_section("TEST 9: Edge Cases & Error Handling")
    
    db = Database(order=4)
    
    # Test empty database operations
    print("Testing operations on empty database:")
    print(f"  Search on empty: {db.search(1)}")
    print(f"  Delete on empty: {db.delete(1)}")
    print(f"  Length of empty: {len(db)}")
    
    # Test invalid entries
    print("\nTesting invalid entries:")
    print(f"  Insert string key: {db.insert('invalid', 'value')}")
    print(f"  Insert None value: {db.insert(1, None)}")
    
    # Test duplicate keys
    print("\nTesting duplicate key handling:")
    db.insert(10, "first")
    print(f"  Inserted (10, 'first')")
    db.insert(10, "second")
    print(f"  Inserted (10, 'second')")
    print(f"  Current value: {db.search(10)}")
    print(f"  Database size: {len(db)}")
    
    # Test clear
    print("\nTesting clear operation:")
    db.insert(20, "value")
    db.insert(30, "value")
    print(f"  Size before clear: {len(db)}")
    db.clear()
    print(f"  Size after clear: {len(db)}")
    
    return db


def display_final_state(db):
    """Display final database state"""
    print_section("Final Database State")
    
    all_data = db.get_all()
    
    print(f"Total entries: {len(db)}")
    print(f"\nAll data (sorted):")
    for key, value in all_data:
        print(f"  {key}: {value}")
    
    print(f"\nDatabase representation: {db}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  B+ tree DB - Test Suite")
    print("="*60)
    
    try:
        # Run all test suites
        test_basic_operations()
        test_dict_interface()
        test_batch_operations()
        test_range_queries()
        test_backup_restore()
        test_json_export_import()
        test_statistics()
        test_validation()
        db = test_edge_cases()
        
        # Show final state
        display_final_state(db)
        
        print_section("ALL TESTS COMPLETED SUCCESSFULLY! ✓")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()