import logging
import os
import csv
import json

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler('app.log', mode='a'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def log_action(action, *args, level="INFO"):
    """Log actions performed in the database or B+ Tree"""
    message = action
    if args:
        message += ": " + ", ".join(str(arg) for arg in args)
    getattr(logger, level.lower(), logger.info)(message)

def validate_entry(key, value):
    """Validate key and value format"""
    if not isinstance(key, (int, float)):
        return False, f"Key must be a number, got {type(key).__name__}"
    if value is None:
        return False, "Value cannot be None"
    if not isinstance(value, (str, int, float, bool)):
        return False, f"Value must be a basic type, got {type(value).__name__}"
    return True, "Valid entry"

def get_sorted_data(btree):
    """Return sorted data from the B+ Tree"""
    if hasattr(btree, 'get_all'):
        return btree.get_all()
    
    if btree.root is None or len(btree.root.keys) == 0:
        return []
    
    data = []
    node = btree.root
    while not node.leaf:
        node = node.values[0]
    
    while node:
        data.extend(zip(node.keys, node.values))
        node = node.next
    
    return data

def backup_data(btree, backup_file):
    """Backup the B+ Tree data to a CSV file"""
    try:
        backup_dir = os.path.dirname(backup_file)
        if backup_dir and not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        data = get_sorted_data(btree)
        
        with open(backup_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Key", "Value"])
            writer.writerows(data)
        
        log_action("Backup successful", backup_file, f"{len(data)} entries")
        return True
    except Exception as e:
        log_action("Backup failed", backup_file, str(e), level="ERROR")
        return False

def restore_data(btree, backup_file):
    """Restore the B+ Tree data from a backup CSV file"""
    try:
        if not os.path.exists(backup_file):
            log_action("Restore failed: File not found", backup_file, level="ERROR")
            return False
        
        if hasattr(btree, 'clear'):
            btree.clear()
        else:
            from node import Node
            btree.root = Node(btree.order, leaf=True)
            btree._size = 0
        
        restored_count = 0
        
        with open(backup_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip header
            
            for row in reader:
                if len(row) < 2:
                    continue
                
                try:
                    key = int(row[0]) if '.' not in row[0] else float(row[0])
                except ValueError:
                    continue
                
                is_valid, _ = validate_entry(key, row[1])
                if is_valid:
                    btree.insert(key, row[1])
                    restored_count += 1
        
        log_action("Restore completed", backup_file, f"{restored_count} entries")
        return True
    except Exception as e:
        log_action("Restore failed", backup_file, str(e), level="ERROR")
        return False

def export_to_json(btree, json_file):
    """Export B+ Tree data to JSON format"""
    try:
        data = get_sorted_data(btree)
        json_data = {
            "count": len(data),
            "data": [{"key": k, "value": v} for k, v in data]
        }
        
        with open(json_file, 'w', encoding='utf-8') as file:
            json.dump(json_data, file, indent=2)
        
        log_action("JSON export successful", json_file, f"{len(data)} entries")
        return True
    except Exception as e:
        log_action("JSON export failed", json_file, str(e), level="ERROR")
        return False

def import_from_json(btree, json_file):
    """Import B+ Tree data from JSON format"""
    try:
        if not os.path.exists(json_file):
            log_action("Import failed: File not found", json_file, level="ERROR")
            return False
        
        with open(json_file, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
        
        if hasattr(btree, 'clear'):
            btree.clear()
        else:
            from node import Node
            btree.root = Node(btree.order, leaf=True)
            btree._size = 0
        
        imported_count = 0
        for item in json_data.get("data", []):
            key, value = item.get("key"), item.get("value")
            is_valid, _ = validate_entry(key, value)
            if is_valid:
                btree.insert(key, value)
                imported_count += 1
        
        log_action("JSON import successful", json_file, f"{imported_count} entries")
        return True
    except Exception as e:
        log_action("JSON import failed", json_file, str(e), level="ERROR")
        return False

def get_statistics(btree):
    """Get statistics about the B+ Tree"""
    try:
        return {
            "size": len(btree) if hasattr(btree, '__len__') else 0,
            "order": btree.order if hasattr(btree, 'order') else None,
            "height": _get_tree_height(btree.root) if btree.root else 0,
            "leaf_nodes": _count_leaf_nodes(btree.root) if btree.root else 0,
            "internal_nodes": _count_internal_nodes(btree.root) if btree.root else 0
        }
    except Exception as e:
        log_action("Error calculating statistics", str(e), level="ERROR")
        return {}

def _get_tree_height(node):
    """Calculate the height of the tree"""
    if node is None:
        return 0
    if node.leaf:
        return 1
    return 1 + _get_tree_height(node.values[0])

def _count_leaf_nodes(node):
    """Count the number of leaf nodes"""
    if node is None:
        return 0
    if node.leaf:
        return 1
    return sum(_count_leaf_nodes(child) for child in node.values)

def _count_internal_nodes(node):
    """Count the number of internal nodes"""
    if node is None or node.leaf:
        return 0
    return 1 + sum(_count_internal_nodes(child) for child in node.values)