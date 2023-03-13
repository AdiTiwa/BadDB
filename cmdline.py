import secrets
import string
from pathlib import Path
import os
import keyboard
import re

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
    if inp == "exit":
        break
