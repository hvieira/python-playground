from dataclasses import dataclass, asdict


@dataclass
class InvalidRequest(Exception):
    message:str

    def to_dict(self):
        return asdict(self)