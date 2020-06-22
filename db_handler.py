import mysql.connector as sql

"""
TODO
 - Convert DB_Handler to ORM
"""
class DB_Handler():
    def __init__(self, user: str, password: str, host: str="127.0.0.1",
                 database: str="prod_monitor", task_table: str="tasks"):
        #SQL config params
        self.user = user
        self.password = password
        self.host = host
        self.db = database
        self.task_table = task_table

        #Setup SQL Connection and DB
        self.sql = self.connect()

    def connect(self):
        """Initiates a SQL database connection"""
        try:
            return sql.connect(user=self.user, password=self.password,
                               host=self.host)
        except sql.Error as err:
            if err.errno == sql.errorcode.ER_ACCESS_DENIED_ERROR:
                print(f"Invalid SQL username or password: {err}")
            else:
                print(err)
            exit(1)

    def __setup_db(self):
        """Creates a database named '{self.db}' if one does not exist already"""
        try:
            cursor = self.sql.cursor()
            cursor.execute(f"CREATE DATABASE {self.db} DEFAULT CHARACTER SET 'utf8'")
            self.__ensure_permissions()
        except sql.Error as err:
            print(f"Database '{self.db}' failed on creation: {err}")

    def __setup_task_table(self):
        """Creates a table named '{self.task_table}' purposed to store task data"""
        try:
            cursor = self.sql.cursor()
            cursor.execute(f"CREATE TABLE {self.db}.{self.task_table} (id varchar(64) NOT NULL, name varchar(64) NOT NULL, category varchar(64) DEFAULT NULL, PRIMARY KEY (`id`))")
        except sql.Error as err:
            if err.errno == sql.errorcode.ER_TABLE_EXISTS_ERROR:
                print(f"Table '{self.task_table}' already exists")
            else:
                print(f"__setup_task_table: {err}")
                exit(1)

    def __ensure_permissions(self):
        """Grants {self.user} all privileges on {self.db}"""
        try:
            cursor = self.sql.cursor()
            cursor.execute(f"GRANT ALL PRIVILEGES ON {self.db}.* TO '{self.user}'@'localhost'")
        except sql.Error as err:
            print(f"Failed to grant {self.user} privileges on '{self.db}': {err}")        

    def store_task(self, task):
        """Writes task data to the SQL DB's task table. 
        
        Creates the necessary DB/table if missing.

        Args:
            task: The task object to be stored 
        """
        try:
            cursor = self.sql.cursor()
            cursor.execute(f"INSERT INTO {self.db}.{self.task_table} (`id`, `name`, `category`) VALUES ('{task.id}', '{task.name}', '{task.category}')");
            self.sql.commit() #Ensure data is committed to DB
        except sql.Error as err:
            if err.errno == sql.errorcode.ER_BAD_DB_ERROR:
                self.__setup_db()
                self.__setup_task_table()
                self.store_task(task)
            if err.errno == sql.errorcode.ER_BAD_TABLE_ERROR or err.errno == 1146:
                self.__setup_task_table()
                self.store_task(task)
            else:
                print(f"store_task: {err}")
                exit(1)
            
    def close(self):
        """Closes an SQL connection"""
        try:
            self.sql.close()
        except sql.Error as err:
            print(f"SQL connection failed to close: {err}")
