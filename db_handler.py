from __future__ import annotations

from dataclasses import dataclass

import mysql.connector as sql
from mysql.connector import MySQLConnection

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from monitor import Task


@dataclass
class DatabaseInfo:
    user: str
    password: str
    host: str = "127.0.0.1"
    database: str = "prod_monitor"
    task_table: str = "tasks"


class DatabaseHandler:
    """
    TODO
     - Convert DB_Handler to ORM
     - Swap insert for upsert
    """

    def __init__(self, database_info: DatabaseInfo):
        # SQL config params
        self.user = database_info.user
        self.password = database_info.password
        self.host = database_info.host
        self.db = database_info.database
        self.task_table = database_info.task_table

        # Setup SQL Connection and DB
        self.sql = self.connect()

    def connect(self) -> MySQLConnection:
        """Initiates a SQL database connection"""
        try:
            return sql.connect(user=self.user, password=self.password, host=self.host)
        except sql.Error as err:
            if err.errno == sql.errorcode.ER_ACCESS_DENIED_ERROR:
                print(f"Invalid SQL username or password: {err}")
            else:
                print(err)
            exit(1)
        except:
            print("Another error occurred when connecting to the database.")

    def __setup_db(self) -> None:
        """Creates a database named '{self.db}' if one does not exist already"""
        print("Setting up database...")

        try:
            cursor = self.sql.cursor()
            cursor.execute(f"CREATE DATABASE {self.db} DEFAULT CHARACTER SET 'utf8'")
            self.__ensure_permissions()
        except sql.Error as err:
            print(f"Database '{self.db}' failed on creation: {err}")

        print("Done setting up database.")

    def __setup_task_table(self) -> None:
        """Creates a table named '{self.task_table}' purposed to store task data"""
        print("Setting up task table...")

        try:
            cursor = self.sql.cursor()
            cursor.execute((
                f"CREATE TABLE {self.db}.{self.task_table} "
                f"("
                f"id varchar(64) NOT NULL, "
                f"name varchar(64) NOT NULL, "
                f"category varchar(64) DEFAULT NULL, "
                f"PRIMARY KEY (`id`)"
                f")"
            ))
        except sql.Error as err:
            if err.errno == sql.errorcode.ER_TABLE_EXISTS_ERROR:
                print(f"Table '{self.task_table}' already exists")
            else:
                print(f"__setup_task_table: {err}")
                exit(1)

        print("Done setting up task table.")

    def __ensure_permissions(self) -> None:
        """Grants {self.user} all privileges on {self.db}"""
        try:
            cursor = self.sql.cursor()
            cursor.execute(f"GRANT ALL PRIVILEGES ON {self.db}.* TO '{self.user}'@'localhost'")
        except sql.Error as err:
            print(f"Failed to grant {self.user} privileges on '{self.db}': {err}")

    def store_task(self, task: Task) -> None:
        """Writes task data to the SQL DB's task table. 
        
        Creates the necessary DB/table if missing.

        Args:
            task: The task object to be stored 
        """
        try:
            cursor = self.sql.cursor()
            cursor.execute((
                f"INSERT INTO {self.db}.{self.task_table} "
                f"(`id`, `name`, `category`) VALUES ('{task.id}', '{task.name}', '{task.category}')"
            ))
            self.sql.commit()  # Ensure data is committed to DB
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

    def close(self) -> None:
        """Closes an SQL connection"""

        print("Closing SQL connection...")

        try:
            self.sql.close()
        except sql.Error as err:
            print(f"SQL connection failed to close: {err}")

        print("Done closing SQL connection.")
