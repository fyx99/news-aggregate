import psycopg2
from psycopg2 import sql, InterfaceError
import traceback
from newsaggregate.db.config import CONNECTION_DETAILS
from psycopg2.errors import UniqueViolation, AdminShutdown, OperationalError

class Database:
    connection = None
    
    def __init__(self):
        self.connect()


    def __enter__(self):
        return self


    def __exit__(self, type, value, traceback):
        """Close Postgres Connection
        """
        if self.connection is not None and self.connection is not None:
            self.connection.close()


    def connect(self):
        """Connect to Postgres
        """
        self.connection = psycopg2.connect(**CONNECTION_DETAILS)
        self.connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = self.connection.cursor()
        cursor.execute("select 1;")
        rows = cursor.fetchall()
        cursor.close()
        assert str(rows) == "[(1,)]"
        print(f"POSTGRES CONNECTION UP {self.connection}")
        
        #print("*** Connection Problem " + repr(e), flush=True)

    def query(self, sql, data=(), result=False):
        # query db with reconnect error handling
        #print("Query: " + str(sql)[0:100] + " ... " + str(len(str(sql))), flush=True)
        rows = []
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, data)
            if result:
                rows = cursor.fetchall()
            cursor.close()
        except (InterfaceError, AdminShutdown, OperationalError) as e:
            print(sql, data)
            print(traceback.print_exc(), flush=True)
            print(e.pgcode)
            if self.closed != 0:
                self.connect()
                print("*** RECONNECT ***", flush=True)
        except Exception as e:
            print(repr(e))
            print(traceback.print_exc(), flush=True)
        finally:
            if result:
                return rows
            return "Saved"


    