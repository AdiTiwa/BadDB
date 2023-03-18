from flask import Flask, request
import os
import re
import requests
from datetime import *
import secrets
import string
from pathlib import Path
import json
import time

app = Flask(__name__)

"""
ERROR CODES AND HANDLING

200 = OK
400 = Bad Request
404 = Not Found
"""

subscriptions = {}

def tsp_read(content):
    return re.split(r'\t+', content.strip())

def collection_exists(col):
    return Path("./data/" + col + ".store").is_file()

def get_hash(size):
    return ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase + "0123456789") for _ in range(size))

def tsp(list): # tab seperated list
    s = ""
    for idx, i in enumerate(list):
        if idx < len(list) - 1:
            s += i + "\t"
        else:
            s += i
    return s

def arr_eq(arr1, arr2):
    for idx, val in enumerate(arr1):
        if val == arr2[idx]:
            return False
    return True

def check_ccode(ccode):
    with open('./data.store', 'r') as f:
        for line in f.readlines():
            if line.startswith(ccode):
                return True
    return False

def uss_request(type, ip): # update server stats request
    if type == "read":
        uss_read()
    elif type == "write":
        uss_write()
    with open("analytics.store", "a") as f:
        f.write(f"IP: {ip}\tType: {type}\Time: {time.localtime()}\n")

def uss_write(): # update server stats writes
    with open("analytics.store", "r") as f: 
        lines = f.readlines()

    content = tsp_read(lines[0])

    lines[0] = f"W\t{str(int(content[1]) + 1)}\n"
    
    with open("analytics.store", "w") as f: 
        f.writelines(lines)

def uss_read(): # update server stats reads
    with open("analytics.store", "r") as f: 
        lines = f.readlines()

    content = tsp_read(lines[1])
    lines[1] = f"R\t{str(int(content[1]) + 1)}\n"
    
    with open("analytics.store", "w") as f: 
        f.writelines(lines)

@app.route('/<ccode>/create/<col>')
def create(ccode, col):
    if not check_ccode(ccode):
        return ''

    if col == None:
        return "400: No collection provided."

    exists = collection_exists(col)

    keys = [i for i in request.args.keys()]
    vals = [i for i in request.args.values()]

    if exists:
        with open("./data/" + col + ".store", "r") as file:
            content = file.readlines()[0]
            if tsp_read(content.strip())[1:] != keys:
                return "400: Key error, invalid keys."
        with open("./data/" + col + ".store", "a") as file:
            file.write(get_hash(9) + "\t" + tsp(vals) + "\n")
    else:
        with open("./data/" + col + ".store", "w") as file:
            file.write("id\t" + tsp(keys) + "\n")
            file.write(get_hash(9) + "\t" + tsp(vals) + "\n")
    
    uss_request("write", request.environ["REMOTE_ADDR"])

    return "200"

@app.route('/<ccode>/remove/<col>/<id>')
def remove(ccode, col, id):
    if not check_ccode(ccode):
        return ''

    if not collection_exists(col):
        return "404"
    
    if id == None:
        return "400"
    
    content = []
    with open("./data/" + col + ".store", "r") as file:
        content = file.readlines()

    with open("./data/" + col + ".store", "w") as file:
        ncontent = []
        for line in content:
            if not line.startswith(id):
                ncontent.append(line)
        
        for line in ncontent:
            file.write("%s" % line)

    uss_request("write", request.environ["REMOTE_ADDR"])

    return "200"

@app.route("/<ccode>/update/<col>/<id>")
def update(ccode, col, id):
    if not check_ccode(ccode):
        return ''

    if not collection_exists(col) or id == None:
        return "404"
    
    keys = [i for i in request.args.keys()]
    vals = [i for i in request.args.values()]

    content = []
    with open("./data/" + col + ".store", "r") as file:
        content = file.readlines()
        header = content[0]
        if tsp_read(header.strip())[1:] != keys:
            return "400: Key error, invalid keys."
    
    ncontent = []
    for line in content:
        if not line.startswith(id):
            ncontent.append(line)
        else:
            ncontent.append(id + "\t" + tsp(vals) + "\n")
    
    with open("./data/" + col + ".store", "w") as file:
        for line in ncontent:
            file.write("%s" % line)

    if col in subscriptions.keys:
        for subscription in subscriptions[col]:
            if type(subscription) == dict:
                ssu(subscription["ip"], col, subscription["id"])
            else:
                ssu(subscription["ip"], col, None)

    uss_request("write", request.environ["REMOTE_ADDR"])

    return "200"

@app.route('/<ccode>/display/<col>')
def display(ccode, col):
    if not check_ccode(ccode):
        return ''

    if not collection_exists(col):
        return "404"

    id = request.args.get('id')

    if not id:
        r = {"name": col, "values": []}

        content = []
        with open('./data/' + col + ".store", "r") as f:
            content = f.readlines()
        
        header = tsp_read(content[0].strip())
        data = content[1:]
        
        for line in data:
            line = tsp_read(line.strip())

            d = {}
            for idx, val in enumerate(line):
                d.update({header[idx]: val})
            r["values"].append(d)

        uss_request("read", request.environ["REMOTE_ADDR"])

        return json.dumps(r)
    else:
        content = []
        with open('./data/' + col + ".store", "r") as f:
            content = f.readlines()
        
        header = tsp_read(content[0].strip())
        data = content[1:]
        d = {}

        for line in data:
            if line.startswith(id):
                line = tsp_read(line.strip())

                for idx, val in enumerate(line):
                    d.update({header[idx]: val})

        uss_request("read", request.environ["REMOTE_ADDR"])
            
        return json.dumps(d)

@app.route('/<ccode>/subscribe/<col>')
def subscribe(ccode, col):
    if not check_ccode(ccode):
        return ''
    
    if not collection_exists(col):
        return '404: no such collection'
    
    id = request.args.get('id')

    if id:
        if col in subscriptions.keys:
            subscriptions[col].append({"ip": request.environ["REMOTE_ADDR"], "id": id})
        else:
            subscriptions.update({col: [{"ip": request.environ["REMOTE_ADDR"], "id": id}]})
    else:
        if col in subscriptions.keys:
            subscriptions[col].append(request.environ["REMOTE_ADDR"])
        else:
            subscriptions.update({col: [request.environ["REMOTE_ADDR"]]})
    
    return '200'

def ssu(ip, col, id): # send subscription update
    content = []
    with open('./data/' + col + ".store", "r") as f:
        content = f.readlines()
    
    header = tsp_read(content[0].strip())
    data = content[1:]

    if id:
        d = {}

        for line in data:
            if line.startswith(id):
                line = tsp_read(line.strip())

                for idx, val in enumerate(line):
                    d.update({header[idx]: val})
        
        requests.post(f"{ip}:5050", d)
    else:
        r = {"name": col, "values": []}

        for line in data:
            line = tsp_read(line.strip())

            d = {}
            for idx, val in enumerate(line):
                d.update({header[idx]: val})
            r["values"].append(d)
        
        requests.post(f"{ip}:5050", r)


port = int(os.environ.get('PORT', 5050))
if __name__ == '__main__':
    app.run(threaded=True, port=port)