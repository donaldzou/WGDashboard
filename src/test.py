from tinydb import TinyDB, Query
conf_db = TinyDB("json/conf.json")

print(conf_db.all())
