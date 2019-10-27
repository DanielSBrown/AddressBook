from datetime import datetime
from flask import Flask, jsonify, request, abort
from elasticsearch import Elasticsearch
import json
from contact import *

es = Elasticsearch()



app = Flask(__name__)
@app.route('/contact', methods=['GET'])
def get_all_contacts():
    # the main GET for all requests, with some header variables
    page_size = request.headers.get("pageSize")
    query_from = request.headers.get("page")
    query_string = request.headers.get("query")
    page_size = page_size if page_size is not None else 10
    query_from = query_from if query_from is not None else 0
    query_string = query_string if query_string is not None else "_exists_ : _id"

    doc = {
        'size' : page_size,
        'from' : query_from,
        "query": {
            "query_string" : {
                "query" : query_string
            }
        }
    }
    result = es.search(index='contacts', body=doc)
    return jsonify(result)


@app.route('/contact', methods=['POST'])
def create_contact():
    # The main POST endpoint for creating a new contact

    # Begin by formatting the data sent in the request into a JSON object

    my_json = (request.data.decode('utf8').replace("'", '"'))
    d = json.loads(my_json)

    # Check for  null first/last name
    if "fName" not in d or "lName" not in d:
        abort(400, "You must specify a first and last name")

    fName = d["fName"]
    lName = d["lName"]

    contact = Contact(fName, lName)

    if does_contact_exist(contact, es, 'contacts'):
        abort(400, "Contact already exists")


    additional_fields = assign_additional_fields_from_request(d)

    validation_list = validate_additional_fields(additional_fields)

    # Cleans out None from the list
    cleaned_validation_list =  [i for i in validation_list if i]
    if len(cleaned_validation_list) > 0:
        abort(400, '\n'.join(cleaned_validation_list))

    # base fields in the body
    body = {
        'fName': fName,
        'lName': lName,
        'timestamp': datetime.now()
    }
    # additional fields in the body
    for field, value in additional_fields.items():
        body[field] = value

    result = es.index(index='contacts', doc_type='contact',  body=body)

    return jsonify(result)



@app.route('/contact/<name>', methods=['GET'])
def get_contact(name):
    # Gets the row of a contact based on name
    response = get_contact_from_name(name, es, 1, 'contacts')
    if response["hits"]["total"] == 0:
        abort(400, "User does not exist")
    return jsonify(response)



@app.route('/contact/<name>', methods=['PUT'])
def update_contact(name):
    # Updates a row of a contact based on name
    response = get_contact_from_name(name, es, 1, 'contacts')
    if response["hits"]["total"] == 0:
        abort(400, "User does not exist")


    my_json = (request.data.decode('utf8').replace("'", '"'))
    d = json.loads(my_json)

    # Check for  null first/last name
    if "fName" not in d or "lName" not in d:
        abort(400, "You must specify a first and last name")

    fName = d["fName"]
    lName = d["lName"]

    existingUserCheck = get_contact_from_name(fName + " " + lName, es, 1, 'contacts')
    if existingUserCheck["hits"]["total"] != 0:
        abort(400, "You cannot change this user's name to the name of another user")

    additional_fields = assign_additional_fields_from_request(d)

    validation_list = validate_additional_fields(additional_fields)

    # Cleans out None from the list
    cleaned_validation_list =  [i for i in validation_list if i]
    if len(cleaned_validation_list) > 0:
        abort(400, '\n'.join(cleaned_validation_list))

    # base fields in the body
    body = {
        'fName': fName,
        'lName': lName,
        'timestamp': datetime.now()
    }
    # additional fields in the body
    for field, value in additional_fields.items():
        body[field] = value


    result = es.index(index='contacts', doc_type='contact', id=response["hits"]["hits"][0]["_id"], body=body)
    return jsonify(result)


@app.route('/contact/<name>', methods=['DELETE'])
def delete_contact(name):
    # Deletes a row of a contact based on a name
    response = get_contact_from_name(name, es, 1, 'contacts')
    if response["hits"]["total"] == 0:
        abort(400, "User does not exist")
    result = es.delete(index='contacts', doc_type='contact', id=response["hits"]["hits"][0]["_id"])

    return jsonify(result)
