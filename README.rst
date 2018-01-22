A Tiny Cloudant Client Library
==============================

The purpose of ``microcdt`` is to be the smallest practical client
library for accessing Cloudant/CouchDB databases. It’s neither fully
featured, nor complete in its API surface cover (nor is it intended to
be).

It caters for the most basic operations, such as creating and deleting
databases, reading, creating, deleting, and updating documents, and
listing all documents in a database.

It also has rudimentary support for bulk operations.

The Cloudant class subclasses ``requests.Session``, so any API endpoint
not implemented directly can always be called using
``Cloudant.get|put|post|request``.

Examples
--------

.. code:: python

    from microcdt import Cloudant

    db = 'mydatabase'
    cdt = Cloudant('https://account.cloudant.com')
    cdt.auth = (USERNAME, PASSWORD)

    cdt.create_database(db)
    result = cdt.create_doc(db, {'name': 'adam'})

    cdt.delete_database(db)
