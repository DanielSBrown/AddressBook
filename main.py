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

    # Check for  null first/last name
    if "fName" not in d or "lName" not in d:
        abort(400, "You must specify a first and last name")

    fName = d["fName"]
    lName = d["lName"]

    contact = Contact(fName, lName)

    if doesContactExist(contact, es):
        abort(400, "Contact already exists")


    additionalFields = assignAdditionalFieldsFromRequest(d)

    validationList = validateAdditionalFields(additionalFields)
    cleanedValidationList =  [i for i in validationList if i]
    if len(cleanedValidationList) > 0:
        abort(400, '\n'.join(cleanedValidationList))

    # base fields in the body
    body = {
        'fName': fName,
        'lName': lName,
        'timestamp': datetime.now()
    }
    # additional fields in the body
    for field, value in additionalFields.items():
        body[field] = value

    print(body)
    #result = es.index(index='contacts', doc_type='contact',  body=body)

    #return jsonify(result)



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
    additionalFields = {}
    for field in fields:
        if field in d:
            additionalFields[field] = d[field]
    # if "phoneNumber" in d:
    #     phoneNumber = d["phoneNumber"]
    #     if (len(phoneNumber) > 10):
    #         abort(400, "Phone Number must not exceed 10 digits (e.g. 1234567890)")

    contact = Contact(fName, lName)

    body = {
        'fName': fName,
        'lName': lName,
        'phoneNumber' : phoneNumber,
        'timestamp': datetime.now()
    }
    #result = es.index(index='contacts', doc_type='contact', id=response["hits"]["hits"][0]["_id"], body=body)

    #return jsonify(result)


@app.route('/contact/<name>', methods=['DELETE'])
def deleteContact(name):
    response = getContactFromName(name, es, 1)
    if response["hits"]["total"] == 0:
        abort(400, "User does not exist")
    result = es.delete(index='contacts', doc_type='contact', id=response["hits"]["hits"][0]["_id"])

    return jsonify(result)
