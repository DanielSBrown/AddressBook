# AddressBook

Simple Flask and ElasticSearch application for storing contact details

## Assumptions Made
* Names used in URLs for getting are in the "First Last" format. This means that for using it as a path variable, it will be "/first%20last" because of URL String Encoding
* Phone Numbers are 10 characters only
* Zip codes are 5 characters only

## Possible Future Features
* Stronger validation on values entered. For example, be able to handle various phone number input types. Right now it is just 10 numbers (e.g. include ways to handle numbers input in the (###)###-#### format) 
* Add validations to the other types of fields, after clarifying with client on what the needs are
* Add a web interface

## Installation Instructions
Create and enter a virutalenvironment

<code>$ pip install -r requirements.txt</code><br>
<code>$ export FLASK_APP=main.py</code><br>
<code>$ flask run</code>
