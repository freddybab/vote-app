import os

from flask import Flask, request, send_from_directory
from werkzeug.utils import safe_join
from flask_restx import Api, Resource, fields

app = Flask(__name__)
static = safe_join(os.path.dirname(__file__), 'static')
app = Flask(__name__)


@app.route('/')
def _home():
    """Serve index.html at the root url"""
    return send_from_directory(static, 'index.html')

@app.route('/<path:path>')
def _static(path):
    """Serve content from the static directory"""
    return send_from_directory(static, path)


api = Api(app, version='1.0', title='TodoMVC API',
    description='A simple TodoMVC API', doc='/documentation'
)

user_ns = api.namespace('users', path='/api/users')

user = api.model('User', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(required=True),
})
    

class UserDAO(object):
    def __init__(self) -> None:
        self.counter = 0
        self.users = []
    
    def get(self, id):
        for user in self.users:
            if user['id'] == id:
                return user

    def create(self, data):
        user = data
        self.counter += 1
        user['id'] = self.counter
        self.users.append(user)
        return user

user_DAO = UserDAO()

user_DAO.create({'name': 'Andreas'})

@user_ns.route('/login')
class Users(Resource):
    def get():
        pass


todo_ns = api.namespace('todos', description='TODO operations', path='/api/todos')

todo = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details'),
    'fav': fields.Boolean(description='Whether the task is very special', default=False),
    'userid': fields.Integer(),
})


class TodoDAO(object):
    def __init__(self):
        self.counter = 0
        self.todos = []

    def get(self, id):
        for todo in self.todos:
            if todo['id'] == id:
                return todo
        api.abort(404, "Todo {} doesn't exist".format(id))

    def create(self, data):
        todo = data
        self.counter += 1
        todo['id'] = self.counter
        self.todos.append(todo)
        return todo

    def update(self, id, data):
        todo = self.get(id)
        todo.update(data)
        return todo

    def delete(self, id):
        todo = self.get(id)
        self.todos.remove(todo)

todo_DAO = TodoDAO()
todo_DAO.create({'task': 'Build an API'})
todo_DAO.create({'task': '?????'})
todo_DAO.create({'task': 'profit!'})


@todo_ns.route('/')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @todo_ns.doc('list_todos')
    @todo_ns.marshal_list_with(todo)
    def get(self):
        '''List all tasks'''
        return todo_DAO.todos

    @todo_ns.doc('create_todo')
    @todo_ns.expect(todo)
    @todo_ns.marshal_with(todo, code=201)
    def post(self):
        '''Create a new task'''
        return todo_DAO.create(api.payload), 201


@todo_ns.route('/<int:id>')
@todo_ns.response(404, 'Todo not found')
@todo_ns.param('id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete them'''
    @todo_ns.doc('get_todo')
    @todo_ns.marshal_with(todo)
    def get(self, id):
        args = request.args
        args['userid']
        '''Fetch a given resource'''
        return todo_DAO.get(id)

    @todo_ns.doc('delete_todo')
    @todo_ns.response(204, 'Todo deleted')
    def delete(self, id):
        '''Delete a task given its identifier'''
        todo_DAO.delete(id)
        return '', 204

    @todo_ns.expect(todo)
    @todo_ns.marshal_with(todo)
    def put(self, id):
        '''Update a task given its identifier'''
        return todo_DAO.update(id, api.payload)


if __name__ == '__main__':
    app.run(debug=True)