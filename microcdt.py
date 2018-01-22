"""
A microscopic Cloudant client library
"""
import requests


class Cloudant(requests.Session):
    """
    The Cloudant class represents an authenticated session to a Cloudant
    database
    """
    def __init__(self, baseurl, **kwargs):
        requests.Session.__init__(self, **kwargs)
        self.baseurl = baseurl + "/{}"

    def create_database(self, dbname):
        """
        Create a new database. Requires account credentials, not API key
        See https://console.bluemix.net/docs/services/Cloudant/api/database.html#create
        """
        response = self.put(self.baseurl.format(dbname))
        response.raise_for_status()

        return response.json()

    def delete_database(self, dbname):
        """
        Delete a database. Requires account credentials, not API key
        See https://console.bluemix.net/docs/services/Cloudant/api/database.html#deleting-a-database        """
        response = self.delete(self.baseurl.format(dbname))
        response.raise_for_status()

        return response.json()

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

    def create_doc(self, dbname, doc):
        """
        Create a new document. Implemented via bulk_docs
        """
        return self.bulk_docs(dbname, [doc])[0]

    def delete_doc(self, dbname, doc_id, rev_id):
        """
        Delete a doc via its id and rev. Implemented via bulk_docs
        """
        return self.bulk_docs(
            dbname,
            [{"_id": doc_id, "_rev": rev_id, "_deleted": True}]
        )[0]

    def update_doc(self, dbname, doc_id, rev_id, new_body):
        """
        Modify a doc via its id and rev. Implemented via bulk_docs
        """
        new_body['_id'] = doc_id
        new_body['_rev'] = rev_id
        return self.bulk_docs(dbname, [new_body])[0]
