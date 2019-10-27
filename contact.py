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

def assignAdditionalFieldsFromRequest(d):
    additionalFields = {}
    for field in fields:
        if field in d:
            additionalFields[field] = d[field]
    return additionalFields

def validateAdditionalFields(additionalFields):
    validationList = []
    for field in fields:
        if field in additionalFields:
            validationList.append(validateField(field, additionalFields[field]))
    return validationList

def validateField(field, value):
    if field == "phoneNumber":
        if len(value) != 10:
            return "Phone Numbers must be 10 characters"
    elif field == "zip":
        if len(value) != 5:
            return "Zip Codes must be 5 characters"
    else:
        return None
    # TODO: ADD MORE VALIDATIONS BASED ON USER NEEDS


def searchClusterForContact(contact, es, size):
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
    return es.search(index='contacts', body=doc)

def doesContactExist(contact, es):
    response = searchClusterForContact(contact, es, 1)
    return response["hits"]["total"] > 0

def getNamesFromName(name):
    try:
        names = name.split()
        if len(names) < 2:
            return None, None
        return name.split()[0], name.split()[1]
    except:
        return None, None

def getContactFromName(name, es, size):
    fName, lName = getNamesFromName(name)
    contact = Contact(fName, lName)
    return searchClusterForContact(contact, es, size)
