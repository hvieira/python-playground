class Configuration():
    TESTING = False

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return 'sqlite:///flaskr.sqlite'
    
    @property
    def SQLALCHEMY_ECHO(self):
        return True
    
    @property
    def SECRET_KEY(self):
        return 'dev'

config = Configuration()