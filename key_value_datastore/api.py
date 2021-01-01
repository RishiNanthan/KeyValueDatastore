from flask import Flask, jsonify, request
from pathlib import Path
from datastoreAPI.client import Client
import json

ID_NO = 0
CLIENTS = {}
FILES_USED = set()
app = Flask(__name__)


@app.route("/")
def index():
    return jsonify({
        "success": True,
        "error": None,
    })


# GET /init?filename="filepath" & datastore="large"/"small" -> GIVES CLIENT TOKEN AND LOCKS THE DATASTORE FILE 
# returning json-format {"success": True, "error": None, "token": token}
# if error returns {"success": False, "error": error}
@app.route("/init")
def init():
    global ID_NO, FILES_USED, CLIENTS
    filename = request.args.get("filename")
    datastore_type = request.args.get("datastore")
    path = None
    datastore_type = datastore_type.strip() if datastore_type is not None else "small"
    # CHECK IF VALID DATASTORE TYPE GIVEN
    if not (datastore_type != "large" or datastore_type != "small"):
        return jsonify({
            "success": False,
            "error": " datastore can either be 'large' or 'small' ",
        })
    # FILE NOT SPECIFIED - CREATE NEW FILE PATH TO CREATE DATASTORE FILE
    if filename is None:
        path = Path().cwd() / "datastoreAPI" / "datafiles"
        files = list(path.iterdir())

        if datastore_type == "small":
            path = path / f"{len(files)}.json"
        else:
            path = path / f"{ len(files) }.datastore"
    # FILE SPECIFIED - OPEN THE EXISTING DATASTORE FILE
    else:
        try:
            path = Path(filename)
            # NO SUCH FILE
            if not path.is_file():
                return jsonify({
                    "success": False,
                    "error": "No Such File",
                })
        # WRONG PATH FORMAT
        except Exception:
            return jsonify({
                "success": False,
                "error": "Wrong Path Format",
            })        
    # CREATE NEW CLIENT AND DELIVER TOKKEN TO USE FOR ACCESSING DATASTORE FILE
    try:
        new_client = Client(ID_NO, path, datastore_type)
        ID_NO += 1
        FILES_USED.add(str(path))
        token = new_client.get_token()
        CLIENTS[token] = new_client

        return jsonify({
            "success": True,
            "filename": str(new_client.filename),
            "token": token,
            "error": None,
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
        })


# GET /read?key=key&token=token -> GIVES VALUE IN JSON FOR THE GIVEN KEY
# json-format {"success": True, "error": None, "value": valuejson}
# if error returns {"success": False, "error": error}
@app.route("/read")
def read():
    global CLIENTS
    try:
        key = request.args.get("key")
        token = request.args.get("token")
        # VALID CLIENT TOKEN
        if token in CLIENTS.keys():
            # KEY AVAILABLE
            try:
                data = CLIENTS[token].read_value(key)
                return jsonify({
                    "success": True,
                    "error": None,
                    "value": data,
                })
            # KEY NOT AVAILABLE OR TIME TO LIVE EXPIRED
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e),
                })
        # CLIENT TOKEN NOT FOUND
        else:
            return jsonify({
                "success": False,
                "error": "No such Token found",
            })
    # OTHER EXCEPTIONS
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


# GET /write?key=key&value={json:json}&token=token -> WRITES THE KEY-VALUE IN DATASTORE
# json-format {"success": True, "error": None}
# if error returns {"success": False, "error": error}
@app.route("/write")
def create():
    global CLIENTS
    try:
        key = request.args.get("key")
        token = request.args.get("token")
        value = request.args.get("value")
        value = json.loads(value)
        time_to_live = request.args.get("time_to_live")
        time_to_live = int(time_to_live) if time_to_live is not None else None
        # CLIENT TOKEN FOUND
        if token in CLIENTS.keys():
            try:
                CLIENTS[token].create_key_value(key, value, time_to_live)
                return jsonify({
                    "success": True,
                    "error": None,
                })
            # KEY ALREADY PRESENT
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                })
        # CLIENT TOKEN NOT FOUND
        else:
            return jsonify({
                "success": False,
                "error": "No such Token found",
            })
    # OTHER EXCEPTION
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


# GET /delete?key=key&token=token -> DELETES THE KEY-VALUE FROM DATASTORE
# json-format {"success": True, "error": None}
# if error returns {"success": False, "error": error}
@app.route("/delete")
def delete():
    global CLIENTS
    try:
        key = request.args.get("key")
        token = request.args.get("token")
        # CLIENT TOKEN AVAILABLE
        if token in CLIENTS.keys():
            # KEY AVAILABLE
            try:
                CLIENTS[token].delete_key(key)
                return jsonify({
                    "success": True,
                    "error": None,
                })
            # KEY NOT AVAILABLE
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                })
        # CLIENT TOKEN NOT FOUND
        else:
            return jsonify({
                "success": False,
                "error": "No such Token found",
            })
    # OTHER EXCEPTION
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


# GET /close?token=token -> CLOSES THE CLIENT AND UNLOCKS FILE FOR OTHER CLIENTS
# json-format {"success": True, "error": None}
# if error returns {"success": False, "error": error}
@app.route("/close")
def close():
    global FILES_USED, CLIENTS
    try:
        token = request.args.get("token")
        # NO SUCH CLIENT TOKEN
        if token not in CLIENTS.keys():
            return jsonify({
                "success": False,
                "error": "No Such Token found",
            })
        # CLIENT TOKEN FOUND
        else:
            client = CLIENTS[token]
            CLIENTS.pop(token)
            FILES_USED.remove(str(client.filename))
            return jsonify({
                "success": True,
                "error": None,
            })
    # OTHER EXCEPTION
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


app.run()
