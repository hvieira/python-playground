import os

class Configuration():
    
    def __init__(self, 
                 secret_key: str, 
                 db_uri: str, 
                 oauth_client_id: str,
                 oauth_client_secret: str,
                 testing = False, 
                 sql_logging = False
                ):
        self.secret_key = secret_key
        self.db_uri = db_uri
        self.oauth_client_id = oauth_client_id
        self.oauth_client_secret = oauth_client_secret
        self.testing = testing
        self.sql_logging = sql_logging

    @property
    def SECRET_KEY(self):
        return self.secret_key
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return self.db_uri

    @property
    def TESTING(self):
        return self.testing
    
    @property
    def SQLALCHEMY_ECHO(self):
        return self.sql_logging
    
    @property
    def OAUTH_CLIENT_ID(self):
        return self.oauth_client_id
    
    @property
    def OAUTH_CLIENT_SECRET(self):
        return self.oauth_client_secret


# defaults here only for simplicity - there should be no defaults in a real scenario
db_uri = os.getenv('FLASK_SERVER_DB_URI', 'postgresql://root:root@localhost:5432/mydb')
client_id = os.getenv('OAUTH_CLIENT_ID', 'flask_server')
client_secret = os.getenv('OAUTH_CLIENT_SECRET', 'dummy_secretz')

configuration = Configuration(
    secret_key='dev',
    db_uri=db_uri, 
    oauth_client_id=client_id,
    oauth_client_secret=client_secret,
    sql_logging=True
)