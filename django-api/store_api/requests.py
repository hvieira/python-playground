from dataclasses import dataclass


@dataclass
class CreateUserRequest():
    first_name: str
    last_name: str
    username: str
    email: str
    password: str