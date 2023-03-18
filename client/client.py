import flask
import requests
import json
import time

def manage_error_code(res):
    if res.startswith():
        pass

class Document:
    def __init__(self, a):
        self.res = a
        if type(a) == str:
            self.res = json.loads(a)
        elif type(a) == dict:
            self.res = a

    def display(self):
        return self.res

    def get_id(self):
        return self.res.get('id')
    
    def __repr__(self):
        return self.res

class Collection:
    def __init__(self, res):
        self.col = json.loads(res)
        self.name = self.col['name']
        self.values = self.col['values']

    def get_values(self):
        return self.values
    
    def display(self):
        return self.col
    
    def get_document(self, id):
        for value in self.values:
            if value["id"] == id:
                return Document(value)

    def __repr__(self):
        return f"<COLLECTION {self.name}> {self.values}"

class CollectionSnapshot:
    def __init__(self, res):
        self.res = res
        self.time = time.localtime()

    def get(self):
        return Collection(self.res)

    def get_time(self):
        return self.time

    def __repr__(self):
        return f"<COLLECTION SNAPSHOT @ {self.time}>"

class DBApp:
    def __init__(self, clientID, server):
        self.clientId = clientID
        self.server = server
        self.cache = {}

    def get_collection_s(self, col):
        return CollectionSnapshot(requests.get(f"http://{self.server}:5050/{self.clientId}/display/{col}").text)

    def get_collection(self, col):
        return Collection(requests.get(f"http://{self.server}:5050/{self.clientId}/display/{col}").text)

    def get_document(self, col, id):
        return Document(requests.get(f"http://{self.server}:5050/{self.clientId}/display/{col}?id={id}").text)
    
    def create(self, col, document):
        if type(document) == dict:
            requests.get(f"http://{self.server}:5050/{self.clientId}/create/{col}", params=document)

    def remove(self, col, id):
        requests.get(f"http://{self.server}:5050/{self.clientId}/remove/{col}/{id}")

    def update(self, col, id, document):
        requests.get(f"http://{self.server}:5050/{self.clientId}/update/{col}/{id}", params=document)

    def __repr__(self):
        return self