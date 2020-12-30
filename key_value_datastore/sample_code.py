from KeyValueDatastore import KeyValueDataStore

filename = None  # Give filename if already created

datastore = KeyValueDataStore(filename=filename)
# Starts the API if not already running, creates file if not given 

file = datastore.get_filename()
# returns the file used as datastore

print(file)  # D:\key_value_datastore\datastoreAPI\datafiles\0.json

success = datastore.create(key="Key1", value={"msg": "Hello World"}, time_to_live=1000)
# Creates a key value pair with key Key1

print(success)  # True

value = datastore.read(key="Key1")
# Gets the value for the given key as dictionary

print(value)  # {'msg': 'Hello World'}

success = datastore.delete(key="Key1")
# Deletes the Key-Value pair from the datastore for the given Key

print(success)  # True
