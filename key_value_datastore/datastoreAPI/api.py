from flask import Flask, jsonify, request
from pathlib import Path


ID_NO = 0
CLIENTS = {}
FILES_USED = set()


app = Flask(__name__)


@app.route("/")
def index():
    return jsonify({
        "success": True,
        "error": None,
    });


@app.route("/init")
def init():
    global ID_NO, FILES_USED, CLIENTS
    filename = request.args.get("filename")
    
    # FILE NOT SPECIFIED - CREATE FILE
    if filename is None:
        path = Path().cwd() / "key_value_datastore" / "datastoreAPI" / "datafiles"
        
        files = list(path.iterdir())
        path = path / f"{len(files)}.json"

        with path.open("x") as f:
            f.close()
        
        FILES_USED.add(str(path))
        user_id = ID_NO
        ID_NO += 1
        CLIENTS[user_id] = str(path)
        
        return jsonify({
            "success": True,
            "filename": str(path),
            "error": None,
            "client_id": user_id,
        })
    
    #   FILE SPECIFIED
    try:
        path = Path(filename)
    
    # WRONG PATH FORMAT
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Wrong Path Format",
        })
    
    # NO SUCH FILE
    if not path.is_file():
        return jsonify({
            "success": False,
            "error": "No Such File",
        })

    # WRONG FILE
    if path.suffix != ".json":
        return jsonify({
            "success": False,
            "error": "Wrong File Specified",
        })
    
    # FILE EXISTS
    else:

        # FILE ALREADY BEING USED
        if str(path) in FILES_USED:
            return jsonify({
                "success": False,
                "error": "File Already in Use",
            })

        # FILE AVAILABLE
        FILES_USED.add(str(path))
        user_id = ID_NO
        ID_NO += 1
        CLIENTS[user_id] = str(path)

        return jsonify({
            "success": True,
            "error": None,
            "client_id": user_id,
            "filename": str(path), 
        })
        

@app.route("/close")
def close():
    global FILES_USED, CLIENTS
    client_id = int(request.args.get("client_id"))
    if client_id is None:
        return jsonify({
            "success": False,
            "error": "No Client ID specified",
        })

    if client_id not in CLIENTS.keys():
        return jsonify({
            "success": False,
            "error": "No Such Client",
        })
    else:
        file = CLIENTS[client_id]
        CLIENTS.pop(client_id)
        FILES_USED.remove(file)
        return jsonify({
            "success": True,
            "error": None,
        })


app.run(debug=True)
