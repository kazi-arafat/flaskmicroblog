import pyodbc
import configparser
import os
import pandas as pd

configurationFile = os.path.dirname(__file__) + "\\config\\app.config"
parser = configparser.ConfigParser()
parser.read(configurationFile)

server = parser.get("db_config","server")
database = parser.get("db_config","database")
conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=' + server + ';'
                      'Database=' + database + ';'
                      'Trusted_Connection=yes;')

def SelectRecordsFromDatabase(query):
    """
    It will return query result as list of dictionary

    """
    dataframe = pd.read_sql(query,conn)
    return list(dataframe.T.to_dict().values())

def InsertRecords(query):
    """
    Used to insert Records
    """
    with conn.cursor() as curr:
        curr.execute(query)

def DeleteRecords(query):
    """
    Used to delete Records
    """
    with conn.cursor() as curr:
        result = curr.execute(query)
    return result.rowcount