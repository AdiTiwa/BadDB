import secrets
import string
from pathlib import Path
import os
import keyboard
import re
import requests

def get_hash(size):
    return ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase + "0123456789") for _ in range(size))

def tsp(list):
    s = ""
    for idx, i in enumerate(list):
        if idx < len(list) - 1:
            s += i + "\t"
        else:
            s += i
    return s

def collection_exists(col):
    return Path("./data/" + col + ".store").is_file()

while True:
    inp = input("? ")
    if inp == "cid":
        ccode = get_hash(15)
        with open("./data.store", "a") as f:
            f.write(ccode + "\n")
        print('client code is ' + ccode)
    if inp == "del cid":
        with open("./data.store", "w") as f:
            f.write("")
        print('client codes are wiped')
    if inp == "del":
        col = input("? col: ")
        if collection_exists(col):
            os.remove("./data/" + col + ".store")
            print("removed successfully")
        else:
            print("collection doesn't exist")
    if inp == "create":
        col = input("? col: ")

        if not collection_exists(col):
            keys = []
            while True:
                inp = input("? keys: ")
                if inp == "":
                    print("---")
                    break
                keys.append(inp)

            data = []
            for key in keys:
                data.append(input(f"? new {key}: "))

            with open("./data/" + col + ".store", "w") as f:
                f.write("id\t" + tsp(keys) + "\n")
                f.write(get_hash(9) + "\t" + tsp(data) + "\n")
            print("---")
            print("written successfully")
            print("---")
        else:
            keys = []
            with open(f"./data/{col}.store", "r") as f:
                content = f.readlines()[0]
                keys = re.split(r'\t+', content.strip())[1:]

            data = []
            for key in keys:
                data.append(input(f"? new {key}: "))

            with open("./data/" + col + ".store", "a") as f:
                f.write(get_hash(9) + "\t" + tsp(data) + "\n")
    if inp == "fix":
        if not Path("analytics.store").is_file():
            with open("analytics.store", "w") as f:
                f.write("W:\t0\nR:\t0\n")
            print("created analytics file")
        if not Path("data.store").is_file():
            with open("data.store", "w") as f:
                f.write()
            print("created data file")
        print("---")
        print("all fixed!")
    if inp == "wipe":
        if Path("data.store").is_file():
            os.remove("data.store")
            print("wiped client ids")
        if Path("analytics.store").is_file():
            os.remove("analytics.store")
            print("wiped analytics")

        for filename in os.listdir("data"):
            f = os.path.join("data", filename)
            # checking if it is a file
            if os.path.isfile(f):
                os.remove(f)
        print("---")
        print("wiped server")
    if inp == "resecure":
        if Path("data.store").is_file():
            os.remove("data.store")
            print("wiped client ids")
        print('server is secure')
    if inp == "new":
        with open("main.py", "r") as f:
            f.write(requests.get("https://raw.githubusercontent.com/AdiTiwa/baddb/master/server/main.py").text)
        if not Path("analytics.store").is_file():
            with open("analytics.store", "w") as f:
                f.write("W:\t0\nR:\t0\n")
        if not Path("data.store").is_file():
            with open("data.store", "w") as f:
                f.write()
        print("server is now downloaded!")
        print("simply run:")
        print()
        print("python main.py")
        print()
        print("to begin server")
        print("now download the client file:")
        print("run the command")
        print()
        print("? client")
        print()
        print("to mirror the client file")
    if inp == "client":
        with open("baddb.py", "r") as f:
            f.write(requests.get("https://raw.githubusercontent.com/AdiTiwa/baddb/master/client/client.py").text)
    if inp == "exit":
        break
