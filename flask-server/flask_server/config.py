import os

class Configuration():
    
    def __init__(self, secret_key: str, db_uri: str, testing = False, sql_logging = False):
        self.testing = testing
        self.secret_key = secret_key
        self.db_uri = db_uri
        self.sql_logging = sql_logging

    @property
    def TESTING(self):
        return self.testing

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return self.db_uri
    
    @property
    def SQLALCHEMY_ECHO(self):
        return self.sql_logging
    
    @property
    def SECRET_KEY(self):
        return self.secret_key
    
    @property
    def oauth_clients():
        return {
            'id': 'secret'
        }


# default here only for simplicity - there should be no default
db_uri = os.getenv('FLASK_SERVER_DB_URI', 'postgresql://root:root@localhost:5432/mydb')

configuration = Configuration(
    secret_key='dev',
    db_uri=db_uri, 
    sql_logging=True)