import os

from flask import Flask, request
from flask.helpers import safe_join
from flask_restx import Resource, Api

app = Flask(__name__)
static = safe_join(os.path.dirname(__file__), 'static')
api = Api(app, doc='/doc')

todos = {}

def insert_todo(todo_id, request):
    todos[todo_id] = request.form['data']
    return {todo_id: todos[todo_id]}

@api.route('/todos/<string:todo_id>')
class Todo(Resource):
    def get(self, todo_id):
        return todos[todo_id]
    
    def put(self, todo_id):
        return insert_todo(todo_id, request)

@api.route('/todos/')
class TodoList(Resource):
    def get(self):
        return todos # TODO convert to list
    def post(self):
        todo_id = max(todos.keys()) + 1 # New id is highest key + 1
        return insert_todo(todo_id, request)

