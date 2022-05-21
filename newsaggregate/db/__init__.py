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

    # conversion limited to dict and list childs

    def to_json(self):
        return BaseDataClass.convert_json_format(asdict(self))

    def convert_json_format(d):
        if isinstance(d, dict):
            for k, v in d.items():
                d[k] = BaseDataClass.convert_json_format(v)
        elif isinstance(d, list):
            for i, v in enumerate(d):
                d[i] = BaseDataClass.convert_json_format(v) 
        elif isinstance(d, datetime):
            d = d.strftime("%Y-%m-%d %H:%M:%S")
        return d
    
    def to_json_string(self):
        return json.dumps(asdict(self), cls=ComplexEncoder)

