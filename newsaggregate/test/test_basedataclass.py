from dataclasses import dataclass
from typing import Dict, List
from db import BaseDataClass

import json
from test.custom_testcase import CustomTestcase
from datetime import datetime

class TestBaseDataClass(CustomTestcase):

    
    def test_base_dataclass(self):
        @dataclass
        class TestDataclass(BaseDataClass):
            num: int
            a: str
            d: any
            dic: Dict[str, any]
            lis: List[str]
        
        a = TestDataclass(**{"num": 1, "a": "a", "d": datetime(2022, 1, 1), "dic": {"kk": {"tt": datetime(2022, 1, 1)}}, "lis": ["a", "b", 1, None, datetime(2022, 1, 1), {"dd": datetime(2022, 1, 1)}]})
        json_dict = a.to_json()

        self.assertEqual(json_dict["d"], "2022-01-01T00:00:00")
        self.assertEqual(json_dict["num"], 1)
        self.assertEqual(json_dict["a"], "a")

        self.assertIsInstance(json.dumps(json_dict), str)


if __name__ =="__main__":
    TestBaseDataClass().test_base_dataclass()