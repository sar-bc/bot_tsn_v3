from database.Database import DataBase
from datetime import date
from datetime import datetime
import asyncio
import threading


class Loger:
    def __init__(self):
        self.name_doc = __name__

    def get_name_log(self, name_doc):
        self.name_doc = name_doc

    async def info(self, text: str):
        db = DataBase()
        await db.log_to_db("INFO", text, self.name_doc)
        print(f"{datetime.now()} - {self.name_doc} - INFO - {text}")

    async def error(self, text: str):
        db = DataBase()
        await db.log_to_db("ERROR", text, self.name_doc)
        print(f"{datetime.now()} - {self.name_doc} - ERROR - {text}")

    async def warning(self, text: str):
        db = DataBase()
        await db.log_to_db("WARNING", text, self.name_doc)
        print(f"{datetime.now()} - {self.name_doc} - WARNING - {text}") 
        