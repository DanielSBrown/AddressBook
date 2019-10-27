from datetime import datetime
from flask import Flask, jsonify, request, abort
from elasticsearch import Elasticsearch
import json
from contact import *
es = Elasticsearch()

app = Flask(__name__)
@app.route('/contact', methods=['GET'])
def getAllContacts():
    doc = {
        'size' : 10000,
        'query': {
            'match_all' : {}
       }
   }
    result = es.search(index='contacts', body=doc)
    return jsonify(result)


@app.route('/contact', methods=['POST'])
def createContact():
    # Begin by formatting the data sent in the request into a JSON object

    my_json = (request.data.decode('utf8').replace("'", '"'))
    d = json.loads(my_json)

    # Get the fields from the body

    fName = d["fName"]
    lName = d["lName"]
    contact = Contact(fName, lName)

    # Check for existing contact
    if doesContactExist(contact, es):
        abort(400, "Contact already exists")

    body = {
        'fName': fName,
        'lName': lName,
        'timestamp': datetime.now()
    }

    result = es.index(index='contacts', doc_type='contact',  body=body)

    return jsonify(result)

@app.route('/contact/<name>', methods=['GET'])
def getContact(name):
    response = getContactFromName(name, es, 1)
    if response["hits"]["total"] == 0:
        abort(400, "User does not exist")
    return jsonify(response)

@app.route('/contact/<name>', methods=['PUT'])
def updateContact(name):
    response = getContactFromName(name, es, 1)
    if response["hits"]["total"] == 0:
        abort(400, "User does not exist")
    my_json = (request.data.decode('utf8').replace("'", '"'))
    d = json.loads(my_json)

    # Get the fields from the body

    fName = d["fName"]
    lName = d["lName"]
    contact = Contact(fName, lName)

    body = {
        'fName': fName,
        'lName': lName,
        'timestamp': datetime.now()
    }
    result = es.index(index='contacts', doc_type='contact', id=response["hits"]["hits"][0]["_id"], body=body)

    return jsonify(result)


@app.route('/contact/<name>', methods=['DELETE'])
def deleteContact(name):
    response = getContactFromName(name, es, 1)
    if response["hits"]["total"] == 0:
        abort(400, "User does not exist")
    result = es.delete(index='contacts', doc_type='contact', id=response["hits"]["hits"][0]["_id"])

    return jsonify(result)
