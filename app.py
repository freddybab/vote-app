import contextlib
import os
from pydoc import describe
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

api = Api(app, version='1.0', title='VoteMVC API',
    description='A simple VoteMVC API', doc='/documentation'
)

vote_ns = api.namespace('votes', description='Vote operations', path='/api/votes')

vote = api.model('Vote', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'candidateId': fields.Integer(required=True, description='Candidate to vote for'),
})

candidate_ns = api.namespace('candidates', description='Candidate operations', path='/api/candidates')

candidate = api.model('Candidate', {
    'id': fields.Integer(readonly=True, description='Unique identifier'),
    'name' : fields.String(required=True, description='Candidate Name')
})

token_ns = api.namespace('tokens', description='Token operations', path='/api/tokens')

token = api.model('Token', {
    'id': fields.Integer(readonly=True, description='Unique identifier'),
    'value' : fields.String(required=True, description='Token secret value'),
    'used' : fields.boolean(readonly=True, default=False, description='Whether this token has been used for voting')
})

class VoteDAO(object):    
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


    def _map_vote(self, vote_row):
        return {
                'id': vote_row[0],
                'candidateId': vote_row[1],
            }
    def _map_candidate(self, candidate_row):
        return {
            'id': candidate_row[0],
            'name': candidate_row[1]
        }

    """
    Opprett tabeller i databasen om database-filen ikke finnes fra før.
    """
    def setup_database(self):
        if not os.path.exists(DATABASE_FILE):
                self._execute_sql(
                '''
                CREATE TABLE votes(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidateId INTEGER
                );
                ''', {})

                self._execute_sql(
                '''
                CREATE TABLE candidates(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT
                ); 
                ''', {})

                self._execute_sql(
                '''
                CREATE TABLE token(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    value TEXT,
                    used INTEGER DEFAULT 0
                );
                ''', {})
    
    def get_all_votes(self):
        return_list = []
        votes = self._execute_sql_fetchall('''
        SELECT * FROM votes
        ''', {})
        for vote in votes:
            return_list.append(self._map_vote(vote))
        return return_list
    
    def get_vote(self, id):
        vote = self._execute_sql('''
        SELECT * FROM votes WHERE id = :id''', {'id': id})
        return self._map_vote(vote)

    def insert_vote(self, data):
        vote = data
        vote_id = self._execute_sql_lastrowid('''
        INSERT INTO votes (candidateId) VALUES (:candidateId)
        ''', data)

        vote['id'] = vote_id
        return vote

    def get_all_candidates(self):
        return_list = []
        candidates = self._execute_sql_fetchall('''
        SELECT * FROM candidates
        ''', {})
        for candidate in candidates:
            return_list.append(self._map_candidate(candidate))
        return return_list
    
    def get_candidate(self, id):
        candidate = self._execute_sql('''
        SELECT * FROM candidates WHERE id = :id''', {'id': id})
        return self._map_candidate(candidate)

    def insert_candidate(self, data):
        candidate = data
        candidate_id = self._execute_sql_lastrowid('''
        INSERT INTO candidate (name) VALUES (:name)
        ''', data)

        candidate['id'] = candidate_id
        return candidate
    
    def insert_token(self, data):
        candidate = data
        candidate_id = self._execute_sql_lastrowid('''
        INSERT INTO tokens (value) VALUES (:candidateId)
        ''', data)

        candidate['id'] = candidate_id
        return candidate

DAO = VoteDAO()

DAO.insert_vote({'id': 1, 'candidateId': 1})


@vote_ns.route('/')
class VoteList(Resource):
    '''Shows a list of all votes, and lets you POST to add new tasks'''
    @vote_ns.doc('list_votes')
    @vote_ns.marshal_list_with(vote)
    def get(self):
        '''List all tasks'''
        return DAO.get_all_votes()


    @vote_ns.doc('insert_vote')
    @vote_ns.expect(vote)
    @vote_ns.marshal_with(vote, code=201)
    def post(self):
        '''Create a new task'''
        marshalled = marshal(api.payload, vote)
        return DAO.insert_vote(marshalled), 201


@vote_ns.route('/<int:id>')
@vote_ns.response(404, 'Vote not found')
@vote_ns.param('id', 'The vote identifier')
class Vote(Resource):
    '''Show a single vote'''
    @vote_ns.doc('get_vote')
    @vote_ns.marshal_with(vote)
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get_vote(id)


@candidate_ns.route('/')
class CandidateList(Resource):
    '''Shows a list of all candidates, and lets you POST to add new candidates'''
    @candidate_ns.doc('list_candidates')
    @candidate_ns.marshal_list_with(candidate)
    def get(self):
        '''List all candidates'''
        return DAO.get_all_candidates()


    @candidate_ns.doc('insert_candidate')
    @candidate_ns.expect(candidate)
    @candidate_ns.marshal_with(candidate, code=201)
    def post(self):
        '''Create a new candidate'''
        marshalled = marshal(api.payload, candidate)
        return DAO.insert_candidate(marshalled), 201

@candidate_ns.route('/<int:id>')
@candidate_ns.response(404, 'Candidate not found')
@candidate_ns.param('id', 'The candidate identifier')
class Candidate(Resource):
    '''Show a single candidate'''
    @candidate_ns.doc('get_candidate')
    @candidate_ns.marshal_with(candidate)
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get_candidate(id)

@token_ns.route('/')
class TokenList(Resource):
    @token_ns.doc('insert_token')
    @token_ns.expect(token)
    @token_ns.marshal_with(token, code=201)
    def post(self):
        '''Create a new token'''
        marshalled = marshal(api.payload, token)
        return DAO.insert_token(marshalled), 201

if __name__ == '__main__':
    app.run(debug=True)