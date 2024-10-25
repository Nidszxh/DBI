from flask import Flask, render_template, request, jsonify
from database import Database

app = Flask(__name__, template_folder='Template')
db = Database(3)

@app.route('/')
def index():
    return render_template('Index.html')

@app.route('/insert', methods=['POST'])
def insert():
    key = request.form.get('key')
    value = request.form.get('value')
    if key.isdigit() and value:
        db.insert(int(key), value)
        return jsonify(success=True)
    return jsonify(success=False, error="Invalid input")

@app.route('/delete', methods=['POST'])
def delete():
    key = request.form.get('key')
    if key.isdigit():
        db.btree.delete(int(key))  # Ensure the delete function exists in the B+ Tree
        return jsonify(success=True)
    return jsonify(success=False, error="Invalid input")

@app.route('/get_tree', methods=['GET'])
def get_tree():
    tree_structure = db.get_tree_structure()  # Return tree structure as JSON
    return jsonify(tree_structure)

if __name__ == '__main__':
    app.run(debug=True)
