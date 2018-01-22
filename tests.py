#!/usr/bin/env python

import unittest
import os
import uuid

from microcdt import Cloudant

USERNAME = os.environ['COUCH_USER']
PASSWORD = os.environ['COUCH_PASSWORD']
HOST = os.environ['COUCH_HOST_URL']


class TestBasics(unittest.TestCase):
    """
    Tests for the microcdt class
    """
    database = 'microcdt-'+uuid.uuid4().hex
    cdt = Cloudant(HOST)
    cdt.auth = (USERNAME, PASSWORD)

    @classmethod
    def setUpClass(cls):
        cls.cdt.create_database(cls.database)

    @classmethod
    def tearDownClass(cls):
        cls.cdt.delete_database(cls.database)

    def test_createdoc(self):
        """
        Test that we can create a document
        """
        result = self.cdt.create_doc(self.database, {'name': 'adam'})
        self.assertTrue(result['ok'])

    def test_createdb(self):
        """
        Test that we can create a database
        """
        database = 'microcdt-'+uuid.uuid4().hex
        result = self.cdt.create_database(database)
        self.assertTrue(result['ok'])

    def test_bulk_docs(self):
        """
        Test that we can create multiple documents in a single request
        """
        data = [{'name': 'adam'}, {'name': 'bob'}, {'name': 'charlotte'}]
        result = self.cdt.bulk_docs(self.database, data)
        self.assertEquals(len(result), len(data))

    def test_readdoc(self):
        """
        Test that we can retrieve a document.
        Health warning: reading your writes NOT guaranteed to work
        """
        data = [{'name': 'adam'}, {'name': 'bob'}, {'name': 'charlotte'}]
        written_docs = self.cdt.bulk_docs(self.database, data)
        for doc in written_docs:
            read_doc = self.cdt.read_doc(self.database, doc['id'])
            self.assertEqual(read_doc['_rev'], doc['rev'])

    def test_updatedoc(self):
        """
        Test that we can update a document using bulk_docs
        Health warning: reading your writes NOT guaranteed to work
        """
        doc = self.cdt.create_doc(self.database, {'name': 'bob'})
        new_doc = self.cdt.update_doc(
            self.database,
            doc['id'],
            doc['rev'],
            {
                'name': 'bob',
                'city': 'folkstone'
            }
        )
        self.assertTrue(new_doc['rev'].startswith('2-'))

    def test_deletedoc(self):
        """
        Test that we can delete a document
        Health warning: reading your writes NOT guaranteed to work
        """
        doc = self.cdt.create_doc(self.database, {'name': 'bob'})
        result = self.cdt.delete_doc(self.database, doc['id'], doc['rev'])
        self.assertTrue(result['rev'].startswith('2-'))

    def test_alldocs_get(self):
        """
        Test that we get back the expected number of docs from all_docs
        """
        data = [{'name': 'adam'}, {'name': 'bob'}, {'name': 'charlotte'}]
        self.cdt.bulk_docs(self.database, data)
        docs = self.cdt.all_docs(self.database)
        self.assertTrue(len(docs) >= len(data))

if __name__ == '__main__':
    unittest.main()
