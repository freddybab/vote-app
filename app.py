import contextlib
import os
import sqlite3

from flask import Flask, request, send_from_directory
from werkzeug.utils import safe_join
from flask_restx import Api, Resource, fields, marshal

static = safe_join(os.path.dirname(__file__), 'static')

app = Flask(__name__)

DATABASE_FILE = 'database.db'

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

ns = api.namespace('todos', description='TODO operations', path='/api/todos')

todo = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details'),
    'fav': fields.Boolean(description='Whether the task is very special', default=False)
})


class TodoDAO(object):    
    def __init__(self):
        self.setup_database()

    """
    Kjører SQL-spørringen 'statement' med gitte verdi-bindinger 'values'
    """
    def _execute_sql(self, statement, values):
        with contextlib.closing(sqlite3.connect(DATABASE_FILE)) as conn: # auto-closes
            with conn: # auto-commits
                with contextlib.closing(conn.cursor()) as cursor: # auto-closes
                    cursor.execute(statement, values)
                    fetch = cursor.fetchall()
                    lastrow = cursor.lastrowid
                    return fetch, lastrow         

    
    """
    Kjører SQL-spørringen om returnere alt som matcher, bruk til SELECT.
    """
    def _execute_sql_fetchall(self, statement, values):
        fetch, _ = self._execute_sql(statement, values)
        return fetch

    """
    Kjører SQL-spørringen og returnerer iden til siste rad. Bruk til INSERT.
    """
    def _execute_sql_lastrowid(self, statement, values):
        _, lastrow = self._execute_sql(statement, values)
        return lastrow


    def _map_todo(self, todo_row):
        return {
                'id': todo_row[0],
                'task': todo_row[1],
                'fav': todo_row[2]
            }

    """
    Opprett tabeller i databasen om database-filen ikke finnes fra før.
    """
    def setup_database(self):
        if not os.exists(DATABASE_FILE):
            # OPPGAVE: Skriv SQL som oppretter en tabell med feltene i en todo:

                self._execute_sql('''CREATE TABLE ...
            )''', {})
    
    def get_all(self):
        return_list = []
        # OPPGAVE: Skriv SQL som hentesr alle radene i todo tabellen

        todos = self._execute_sql_fetchall('''
        SELECT ...
        ''', {}) # todo convert to json? marshal? ORM?
        for todo in todos:
            return_list.append(self.map_todo(todo))
        return return_list
    
    def get(self, id):

        # OPPGAVE: Skriv SQL som henter todo-raden med den gitte id-en
        todo = self._execute_sql('''
        SELECT ...''', {'id': id})
        return self.map_todo(todo)

    def create(self, data):
        todo = data
        # OPPGAVE: Skriv SQL som setter inn en ny rad i todo tabellen
        todo_id = self._execute_sql_lastrowid('''
        INSERT ...
        ''', data)

        todo['id'] = todo_id
        return todo

    def update(self, id, data):
        # OPPGAVE: Skriv SQL som oppdaterer den gitte raden i tabellen
        self._execute_sql('''
        UPDATE ...
        ''', data)
        return todo

    def delete(self, id):
        # OPPGAVE: Skriv SQL som sletter den gitte raden i tabellen
        self._execute_sql('''
        DELETE ...
        ''', {'id': id})

DAO = TodoDAO()

@ns.route('/')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all tasks'''
        return DAO.get_all()

    @ns.doc('create_todo')
    @ns.expect(todo)
    @ns.marshal_with(todo, code=201)
    def post(self):
        '''Create a new task'''
        marshalled = marshal(api.payload, todo)
        return DAO.create(marshalled), 201


@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete them'''
    @ns.doc('get_todo')
    @ns.marshal_with(todo)
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get(id)

    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    def delete(self, id):
        '''Delete a task given its identifier'''
        DAO.delete(id)
        return '', 204

    @ns.expect(todo)
    @ns.marshal_with(todo)
    def put(self, id):
        '''Update a task given its identifier'''
        return DAO.update(id, api.payload)


if __name__ == '__main__':
    app.run(debug=True)