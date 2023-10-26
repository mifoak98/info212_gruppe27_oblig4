import json
from flask import Flask, jsonify, request
from neo4j import GraphDatabase

app = Flask(__name__)

class Neo4jDriver:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

neo4j_driver = Neo4jDriver("neo4j+s://a0f6f9eb.databases.neo4j.io", "neo4j", "3hCqDbvBlbR_vFBCPgnp1JgwIj_NVyMUwOM6ybNVLsM")

@app.route('/')
def index():
    with neo4j_driver._driver.session() as session:
        result = session.run("MATCH (n) RETURN n LIMIT 25")
        nodes = [record['n']['name'] for record in result]
        
    response_data = {
        "data": nodes,
        "message": "Hello INFO212"
    }
    
    return jsonify(response_data)

if __name__ == '__main__':
    app.run()
