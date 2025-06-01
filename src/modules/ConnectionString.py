import configparser
import os

from sqlalchemy_utils import database_exists, create_database

from DashboardConfig import DashboardConfig

def ConnectionString(database) -> str or None:    
    parser = configparser.ConfigParser(strict=False)
    parser.read_file(open('wg-dashboard.ini', "r+"))
    sqlitePath = os.path.join("db")
    if not os.path.isdir(sqlitePath):
        os.mkdir(sqlitePath)
    if parser.get("Database", "type") == "postgresql":
        cn = f'postgresql+psycopg2://{parser.get("Database", "username")}:{parser.get("Database", "password")[1]}@{parser.get("Database", "host")[1]}/{database}'
    elif parser.get("Database", "type")[1] == "mysql":
        cn = f'mysql+mysqldb://{parser.get("Database", "username")[1]}:{parser.get("Database", "password")[1]}@{parser.get("Database", "host")[1]}/{database}'
    else:
        cn = f'sqlite:///{os.path.join(sqlitePath, f"{database}.db")}'
    if not database_exists(cn):
        create_database(cn)
    return cn