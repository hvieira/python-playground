import os


configuration_mapping = {
    'SECRET_KEY': os.getenv('FLASK_SECRET_KEY'),
    'DATABASE_URL': os.getenv('DATABASE_URL')
}
