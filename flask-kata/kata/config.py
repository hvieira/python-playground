from typing import Mapping, Any
import os


configuration_mapping: Mapping[str, Any] = {
    'SECRET_KEY': os.getenv('FLASK_SECRET_KEY'),
    'SQLALCHEMY_DATABASE_URI': os.getenv('DATABASE_URL'),
    'SQLALCHEMY_TRACK_MODIFICATIONS': False
}
