# A Tiny Cloudant Client Library

The purpose of `microcdt` is to be the smallest practical client library
for accessing Cloudant/CouchDB databases. It's neither fully featured, nor
complete in its API surface cover (nor is it intended to be).

It caters for the most basic operations, such as creating and deleting databases,
reading, creating, deleting, and updating documents, and listing all documents
in a database.

It also has rudimentary support for bulk operations.

The Cloudant class subclasses `requests.Session`, so any API endpoint not
implemented directly can always be called using `Cloudant.get|put|post|request`.

## Examples

```python
from microcdt import Cloudant

db = 'mydatabase'
cdt = Cloudant('https://account.cloudant.com')
cdt.auth = (USERNAME, PASSWORD)

cdt.create_database(db)
result = cdt.create_doc(db, {'name': 'adam'})

cdt.delete_database(db)
```

## Install

```
pip install microcdt
```

## Should you use a client library or "roll your own"?

Sometimes, using a client library that someone else wrote to talk to an HTTP service API is overkill. Perhaps you're just writing a one-off script, or perhaps you only need access to a tiny subset of the API. Sometimes you just want the control over how things are done that can only come from "rolling your own".

Glynn Bird wrote an excellent article on the different types of [abstraction levels](https://medium.com/ibm-watson-data-lab/choosing-a-cloudant-library-d14c06f3d714) that client libraries can offer, using Node as the example language.

The aim of this repo is to show how you can create a simple library yourself to access Cloudant's HTTP API, relying only on a library for making HTTP requests.

Cloudant's API is all HTTP(S), and pretty much all programming languages have decent support for making HTTP requests. It's particularly slick in languages such as Python and Node. Python's [requests](http://docs.python-requests.org/en/master/) library kind of started the trend of super-friendly HTTP libraries, and it now has analogues in most other languages, too.

Before embarking on writing your own mini-client-lib, it's worth understanding what aspects of the Cloudant API you will want to use (to ensure that you only implement support for the subset you need), and also a bit about the abstractions that the Cloudant API provides (not many).

A light-weight DIY client library will essentially be a an authenticated HTTP session plus URL constructor. The only "abstraction" is the HTTP request: there are no "database objects" in terms of the API. Some libraries occasionally pile on abstractions that aren't really there in the API.

Starting from the base assumption that the "Cloudant" class is an HTTP session, in Python (using the requests library), a super-minimal Cloudant client library might look something like this:

```python
import requests

class Cloudant(requests.Session):
    """
    The Cloudant class represents an authenticated session to a Cloudant database
    """
    def __init__(self, **kwargs):
        requests.Session.__init__(self, **kwargs)
```

That's actually enough to be useful, and I find myself using that all the time for ad-hoc scripting, and for using in jupyter notebooks. It goes like this:

```python
from microcdt import Cloudant

BASEURL = 'https://skruger.cloudant.com/{0}'
cloudant = Cloudant()
cloudant.auth = ("myapikey", "kasjhfkjsadflksj")

data = cloudant.get(BASEURL.format("database/_all_docs"), params={"include_docs": "true"}).json()["rows"]
```

The `BASEURL` global is a bit unsightly. We can hide that:

```python
class Cloudant(requests.Session):
    """
    The Cloudant class represents an authenticated session to a Cloudant
    database
    """
    def __init__(self, baseurl, **kwargs):
        requests.Session.__init__(self, **kwargs)
        self.baseurl = baseurl + "/{}"
```

What I tend to do is to start using that admittedly a bit clumsy `cloudant.get(...)` incantation, and if I find myself using it twice, rolling that up into a method in the `microcdt` library:

```python
def all_docs(self, dbname):
    """
    Return all docs for the given database
    See https://console.bluemix.net/docs/services/Cloudant/api/database.html#get-documents
    """
    path = "{}/_all_docs".format(dbname)
    response = self.get(
        self.baseurl.format(path),
        params={"include_docs": "true"}
    )
    response.raise_for_status()

    return response.json()["rows"]
```

meaning that we can now use the more appealing

```python
data = cloudant.all_docs(database)
```

Perhaps we should have started with simply looking up a document based on its `_id` and optional `_rev`. Most uses of Cloudant will require this. It looks like this:

```python
def read_doc(self, dbname, doc_id, rev_id=None):
    """
    Read a doc by id, optionally specifying the rev
    See https://console.bluemix.net/docs/services/Cloudant/api/database.html#get-documents
    """
    path = "{0}/{1}".format(dbname, doc_id)
    params = {}
    if rev_id:
        params["rev"] = rev_id

    response = self.get(self.baseurl.format(path), params=params)
    response.raise_for_status()

    return response.json()
```

All API access methods you create will follow a similar pattern:

1. Construct the path to the API endpoint.
1. Construct a `params` dict for any API call parameters.
1. If it's a `PUT` or `POST` you may have to construct the request body.
1. Perform the HTTP request.
1. Parse the JSON, and either return this, or some subset thereof.

Let's look at a slightly more complicated endpoint, like `_bulk_docs`.

```python
def bulk_docs(self, dbname, doc_list):
    """
    Bulk-upload the documents contained in doc_list to the database dbname
    See https://console.bluemix.net/docs/services/Cloudant/api/document.html#bulk-operations
    """
    path = "{}/_bulk_docs".format(dbname)
    body = {"docs": doc_list}
    response = self.post(self.baseurl.format(path), json=body)
    response.raise_for_status()

    return response.json()
```

As it turns out, the `_bulk_docs` endpoint is very useful indeed. Following the pattern used by PouchDB, we can quickly implement a whole raft of useful endpoints by simply calling this, such as delete, update and create single documents.

## Conclusion

Many times it can be useful and pretty straight-forward to write your own client library.

The wins are:

1. You can ensure you only get exactly what you need (no bloat).
1. You know exactly how it works, as you wrote it.
1. You gain understanding of the API you're targeting
