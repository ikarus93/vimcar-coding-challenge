# dbConfig.py
import sqlite3

def dict_factory(cursor, row):
    '''
    Casts sqllite3 table from tuple to dictionary,
    as everything specified in https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.row_factory
    '''
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_db(database, g):
    ''' 
    Takes parameters: database(type="string") == the path to the relevant sqllite3 database,
    g(type="global object") == global object, needed to pass via function to avoid circular dependencies
    returns database instance
    '''
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(database)
    db.row_factory = dict_factory
    return db

def query_db(query, params, g):
    ''' Executes specified query for specified database
    Takes parameters: 
    query(type="string") == the query to execute,
    params(type="tuple") == parameters for db query,
    g(type="global object") == global object, needed to pass via function to avoid circular dependencies
    returns query result
    '''
    cur = g._database.execute(query, params)
    g._database.commit()
    return cur.fetchall()
    