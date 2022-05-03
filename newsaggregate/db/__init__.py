from dataclasses import dataclass, asdict

@dataclass
class BaseDataClass: 
    def to_json(self):
        return asdict(self)