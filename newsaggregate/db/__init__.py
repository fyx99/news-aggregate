from dataclasses import dataclass, asdict
from datetime import datetime
import json


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        
        return json.JSONEncoder.default(self, obj)

@dataclass
class BaseDataClass: 
    def to_json(self):
        return asdict(self)
    def to_json_string(self):
        return json.dumps(asdict(self), cls=ComplexEncoder)

