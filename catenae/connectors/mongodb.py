#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient


class MongodbConnector:

    def __init__(self, host, port, default_database=None,
                 default_collection=None, connect=False):
        self.config = {'host': host, 'port': port}
        if default_database:
            self.database = default_database
        if default_collection:
            self.collection = default_collection
        self.client = None
        if connect:
            self.open_connection()

    def _get_collection(self, database_name, collection_name):
        self.open_connection()
        database_name, collection_name = \
            self._set_database_collection_names(database_name,
                                                collection_name)
        database = getattr(self.client, database_name)
        collection = getattr(database, collection_name)
        return collection

    def open_connection(self):
        if not self.client:
            self.client = MongoClient(**self.config)

    def close_connection(self):
        if self.client:
            self.client.close()

    def _set_database_collection_names(self, database_name, collection_name):
        if not database_name:
            database_name = self.database
        if not collection_name:
            collection_name = self.collection
        return database_name, collection_name

    def get_and_close(self, query=None, database_name=None,
                      collection_name=None):
        result = self.get(query, database_name, collection_name)
        self.close_connection()
        return result

    def exists(self, query, database_name=None, collection_name=None):
        collection = self._get_collection(database_name, collection_name)
        if not collection.find_one(query):
            return False
        return True

    def create_index(self, attribute, database_name=None, collection_name=None,
                     unique=False, type_='asc'):
        if type_ == 'desc':
            type_ = -1
        else:
            type_ = 1
        collection = self._get_collection(database_name, collection_name)
        collection.create_index([(attribute, type_)], unique=unique, background=True)

    def get(self, query=None, database_name=None, collection_name=None, sort=None,
            sort_attribute=None, sort_type=None, limit=None, index=None,
            index_attribute=None, index_type=None):
        collection = self._get_collection(database_name, collection_name)
        if sort_attribute and sort_type:
            if sort_type == 'desc':
                sort_type = -1
            else:
                sort_type = 1
            sort = [(sort_attribute, sort_type)]
        if limit == 1:
            result = collection.find_one(query, sort=sort)
            if result:
                return iter([result])
            return iter([])
        result = collection.find(query, sort=sort)
        if index or (index_attribute and index_type):
            if index:
                result = result.hint(index)
            else:
                if index_type == 'desc':
                    index_type = -1
                else:
                    index_type = 1
                result = result.hint([(index_attribute, index_type)])
        if limit:
            result = result.limit(limit)
        return result

    def get_random(self, query=None, database_name=None, collection_name=None,
                   sort=None, sort_attribute=None, sort_type=None, limit=1):
        collection = self._get_collection(database_name, collection_name)
        if sort_attribute and sort_type:
            if sort_type == 'desc':
                sort_type = -1
            else:
                sort_type = 1
            sort = [(sort_attribute, sort_type)]
        operation = [{'$sample': {'size': limit}}]
        if query:
            operation = [{'$match': query}] + operation
        if sort:
            operation = operation + [{'$sort': sort}]
        result = collection.aggregate(operation)
        return result

    def update(self, query, value, database_name=None, collection_name=None):
        collection = self._get_collection(database_name, collection_name)
        collection.update_one(query, {'$set': value}, upsert=True)

    def put(self, value, query=None, database_name=None, collection_name=None):
        if query:
            self.update(query, value, database_name, collection_name)
        else:
            self.insert(value, database_name, collection_name)

    def remove(self, query=None, database_name=None, collection_name=None):
        collection = self._get_collection(database_name, collection_name)
        collection.remove(query)

    def insert(self, value, database_name=None, collection_name=None):
        collection = self._get_collection(database_name, collection_name)
        collection.insert_one(dict(value))

    def count(self, query=None, database_name=None, collection_name=None):
        collection = self._get_collection(database_name, collection_name)
        if not query:
            query = {}
        return collection.count_documents(filter=query)
