from flask import Flask, request, jsonify
from models import db, Location, DistressWord
from graph_algo import find_safest_route
from emergency_queue import EmergencyQueue
from trie_sos import Trie

app = Flask(__name__)

trie = Trie()
with app.app_context():
    distress_words = DistressWord.query.all()
    for word in distress_words:
        trie.insert(word.word)

eq = EmergencyQueue()
eq.load_contacts()

graph = {
    'A': {'B': 2, 'C': 5},
    'B': {'A': 2, 'D': 3, 'E': 1},
    'C': {'A': 5, 'E': 2},
    'D': {'B': 3, 'E': 4, 'F': 1},
    'E': {'B': 1, 'C': 2, 'D': 4, 'F': 3},
    'F': {'D': 1, 'E': 3}
}

@app.route("/find_route")
def find_route():
    start, end = request.args.get("start"), request.args.get("end")
    return jsonify({"route": find_safest_route(graph, start, end)})

@app.route("/detect_sos")
def detect_sos():
    word = request.args.get("word")
    return jsonify({"sos_detected": trie.search(word)})

if __name__ == "__main__":
    app.run(debug=True)
