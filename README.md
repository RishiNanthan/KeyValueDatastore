# KeyValueDataStore
A file-based key-value data store that supports the basic CRD (create, read, and delete) operations. This data store is meant to be used as a local storage for one single process on one laptop. The data store must be exposed as a library to clients that can instantiate a class and work with the data store.

# The data store will support the following functional requirements.
1. It can be initialized using an optional file path. If one is not provided, it will reliably create itself in a reasonable location on the laptop.
2. A new key-value pair can be added to the data store using the Create operation. The key is always a string - capped at 32chars. The value is always a JSON object - capped at 16KB.
3. If Create is invoked for an existing key, an appropriate error must be returned.
4. A Read operation on a key can be performed by providing the key, and receiving the value in response, as a JSON object.
5. A Delete operation can be performed by providing the key.
6. Every key supports setting a Time-To-Live property when it is created. This property is optional. If provided, it will be evaluated as an integer defining the number of seconds the key must be retained in the data store. Once the Time-To-Live for a key has expired, the key will no longer be available for Read or Delete operations.
7. Appropriate error responses must always be returned to a client if it uses the data store in unexpected ways or breaches any limits.

# The data store will also support the following non-functional requirements.
1. The size of the file storing data must never exceed 1GB.
2. More than one client process cannot be allowed to use the same file as a data store at any given time.
3. A client process is allowed to access the data store using multiple threads, if it desires to. The data store must therefore be thread-safe.
4. The client will bear as little memory costs as possible to use this data store, while deriving maximum performance with respect to response times for accessing the data store.

# Additional Features
1. You can use either large datastore or small datastore
2. Large datastore can be used when the data to be stored must be retrieved fastly, even if the file size grows larger.
3. Small datastore can be used for relatively small needs for storing and retrieving data. It uses JSON files to handle data
4. Once you get a token for accessing a file, No other client process could get token for accessing the same file until you relieve the token by calling close() method.

# Environment Setup
1. Operating system: Any platforms that support Python 3.7
2. Python: Python3.7 or more
3. Install Python dependency packages: `python3 -m pip install -r requirements.txt`
4. Port number 5000 must be free to use. Otherwise,
    1. Edit the api.py file and change the `PORT` number as you desire
    2. Edit the KeyValueDatastore.py and change the port number specified in the `URL` to required port number 
5. Run `api.py` to run the backend server.
    1. To start datastore from default file location, run `python3 api.py`
6. You can either write your own API for getting data from `http:\\localhost:5000\`, or use the KeyValueDataStore class to access the datastore 
 

# API using Class KeyValueDataStore from KeyValueDatastore.py
1. Create an object of the class `KeyValueDataStore` using optional parameters `filename` and `datastore_type`. The filename should be the file previously used by the client to store previous data. If not given the api would create a new file for the client and can be accessed using `get_filename()` method. The datastore_type can either be `large` or `small`. The datastore_type if not specified, assumes it to be small. If filename for small datastore is given to large datastore type or vice versa gives JSON errors.
2. You can use `create()` method for creating a key-value pair in the datastore. It receives a `key` of str type with max limit of 32 characters, `value` of dict type with max limit of 16KB and `time_to_live` of int type. If key already exists, throws error.
3. You can use `read()` method for reading value for a particular key in the datastore. It receives `key` ofstr type with max limit of 32 characters, returns value on success. If key is not found throws error. 
4. You can use `delete()` method for deleting a particular key-value pair in the datastore. It receives `key` of str type with max limit of 32 characters, returns value on success. If key is not found throws error.

# REST API Examples
1. init - `http://localhost:5000/init?filename="1.json" & datastore="small"` `filename` is the file that is used as key-value datastore If left empty, it would create new file. datastore can either be `small` or `large`. It locks the datastore file and gives a Token. If success returns json containing `token` that must be used in CRD operations.
2. write - `http://localhost:5000/write?token=""&key="Key"&value={msg:"val"}` `token` is the token received during init, `key` is string of maximum 32 character long used to identify the value uniquely in the datastore. `value` is JSON data to be stored in the datastore. Returns true on successful write.
3. read - `http://localhost:5000/read?token=""&key="Key"` `token` is the token received during init, `key` is string of maximum 32 character long used to identify the value uniquely in the datastore. Returns value as JSON if found else returns error.
4. delete - `http://localhost:5000/read?token=""&key="Key"` `token` is the token received during init, `key` is string of maximum 32 character long used to identify the value uniquely in the datastore. Returns true on successful delete.
5. close - `http://localhost:5000/read?token=""` `token` is the token received during init, it closes the datastore and allows other processes to access datastore file.
