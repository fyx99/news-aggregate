import traceback
import json
from boto3 import Session
import traceback


secret = {
    "access_key_id": "AKIAQT4HBU75VQSE6IET",
    "bucket": "hcp-1a9ec634-dfdf-40cd-8a08-d40904f2d00e",
    "host": "s3-eu-central-1.amazonaws.com",
    "region": "eu-central-1",
    "secret_access_key": "Gv60dgVPFwsJb7sycb2DaOqMASK+3K26BzrPq/3k",
    "uri": "s3://AKIAQT4HBU75VQSE6IET:Gv60dgVPFwsJb7sycb2DaOqMASK%2B3K26BzrPq%2F3k@s3-eu-central-1.amazonaws.com/hcp-1a9ec634-dfdf-40cd-8a08-d40904f2d00e",
    "username": "hcp-s3-d0043d7c-fdf5-40de-894c-a8987ae03d4f"
}

class Datalake:
    connection = None
    bucket = ""


    def __init__(self):
        self.connect()


    def __enter__(self):
        return self


    def __exit__(self, type, value, traceback):
        """Close Postgres Connection
        """
        pass


    def connect(self):
        """Connect to S3
        """
        try:
                
            # with open("../../config/s3.json") as file:
            #     s3key = json.load(file)
            s3key = secret

            session = Session(
                aws_access_key_id=s3key["access_key_id"],
                aws_secret_access_key=s3key["secret_access_key"],
            )
            self.connection = session.client("s3")
            self.bucket = s3key["bucket"]
            print(f"S3 CONNECTION UP {self.connection}")

            
        except Exception as e:
            print("*** Connection Problem " + repr(e), flush=True)


    def put_json(self, path, json_data=()):
        # query db with reconnect error handling
        try:
            self.connection.put_object(Body=json.dumps(json_data), Bucket=self.bucket, Key=path)
        except Exception as e:
            print(repr(e))
            print(traceback.print_exc(), flush=True)

    def get_json(self, path):
        obj = self.connection.get_object(Bucket=self.bucket, Key=path)
        try:
            return json.loads(obj['Body'].read())
        except:
            print(traceback.print_exc(), flush=True)
        return {}

        
