class Contact:

    def __init__(self, fName, lName):
        self.fName = fName
        self.lName = lName







fields = {
    "phoneNumber",
    "streetAddress",
    "suite",
    "state",
    "zip"
}

def assign_additional_fields_from_request(requestDict):
    additional_fields = {}
    for field in fields:
        if field in requestDict:
            additional_fields[field] = requestDict[field]
    return additional_fields

def validate_additional_fields(additional_fields):
    validation_list = []
    for field in fields:
        if field in additional_fields:
            validation_list.append(validate_field(field, additional_fields[field]))
    return validation_list

def validate_field(field, value):
    if field == "phoneNumber":
        if len(value) != 10:
            return "Phone Numbers must be 10 characters"
    elif field == "zip":
        if len(value) != 5:
            return "Zip Codes must be 5 characters"
    else:
        return None
    # TODO: ADD MORE VALIDATIONS BASED ON USER NEEDS


def search_cluster_for_contact(contact, es, size, index):
    # Queries the ES cluster, and returns if there are any hits
    if contact.fName is None or contact.lName is None:
        return None
    doc = {
        "query": {
            "bool": {
                "must": [
                    {
                    "term": {
                        "fName": contact.fName
                    }},
                    {
                    "term": {
                        "lName": contact.lName
                    }
                    }
                ]
            }
        },
        "size": size

    }
    return es.search(index=index, body=doc)

def does_contact_exist(contact, es, index):
    response = search_cluster_for_contact(contact, es, 1, index)
    if response is None:
        return False
    return response["hits"]["total"] > 0

def get_names_from_name(name):
    try:
        names = name.split()
        if len(names) < 2:
            return None, None
        return name.split()[0], name.split()[1]
    except:
        return None, None

def get_contact_from_name(name, es, size, index):
    fName, lName = get_names_from_name(name)
    contact = Contact(fName, lName)
    return search_cluster_for_contact(contact, es, size, index)
