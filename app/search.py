import logging
from typing import Generator

import sqlalchemy as sa
from flask import current_app
from elasticsearch import Elasticsearch, helpers

from app.db import db


class ElasticsearchService:
    def __init__(self, es_client=None) -> None:
        self.es_client = es_client
        self.logger = logging.getLogger("app.elasticsearch")

    def get_es_client(self) -> Elasticsearch | None:
        if self.es_client is None:
            self.es_client = current_app.elasticsearch
        return self.es_client

    def create_index(self, index_name: str) -> None:
        es_client = self.get_es_client()
        if es_client is None:
            return None
        if not es_client.indices.exists(index=index_name):
            es_client.indices.create(index=index_name)
            self.logger.info("Index [%s] created.", index_name)

    def add_to_index(self, index: str, doc_id: int, document: dict) -> None:
        es_client = self.get_es_client()
        if es_client is None:
            return
        es_client.index(index=index, id=doc_id, document=document)

    def remove_from_index(self, index: str, doc_id: int) -> None:
        es_client = self.get_es_client()
        if es_client is None:
            return
        es_client.delete(index=index, id=doc_id, ignore=[404])

    def query_index(self, index, query, page, per_page) -> (list[int], int):
        es_client = self.get_es_client()
        if es_client is None:
            return [], 0
        search = es_client.search(
            index=index,
            query={"multi_match": {"query": query, "fields": ["*"]}},
            from_=(page - 1) * per_page,
            size=per_page)
        ids = [int(hit['_id']) for hit in search['hits']['hits']]
        return ids, search['hits']['total']['value']

    def remove_all_docs_from_index(self, index: str) -> None:
        es_client = self.get_es_client()
        es_client.delete_by_query(
            index=index,
            body={
                "query": {"match_all": {}}
            }
        )

    def stream_documents_to_index(self, doc_stream: Generator, chunk_size: int = 1000) -> None:
        error_count = 0
        for status_ok, response in helpers.streaming_bulk(
                client=self.get_es_client(),
                actions=doc_stream,
                chunk_size=chunk_size
        ):
            if not status_ok:
                error_count += 0

                doc_id = response["index"].get("_id")
                error = response["index"].get("error", {})
                status = response["index"].get("status")

                self.logger.error(
                    "Failed doc %s | status=%s | error=%s",
                    doc_id, status, error
                )

        if error_count > 0:
            self.logger.error("Bulk indexing finished with %s errors", error_count)


es_service = ElasticsearchService()


class SearchableMixin:
    es_service = es_service
    searchable_fields = []
    index_name = None

    @classmethod
    def get_index_name(cls) -> str:
        if cls.index_name is None:
            cls.index_name = cls.__tablename__
        return cls.index_name

    def get_searchable_fields(self) -> list:
        if not self.searchable_fields:
            raise AttributeError('Specify the searchable_fields attribute')
        return self.searchable_fields

    def prepare_document(self) -> dict:
        return {
            "document": {
                field: getattr(self, field)
                for field in self.get_searchable_fields()
            }
        }

    def prepare_data_to_bulk(self) -> dict:
        return {
            "_index": self.get_index_name(),
            "_id": self.id,
            "_source": self.prepare_document()["document"]
        }

    def add_instance_to_index(self) -> None:

        self.es_service.add_to_index(
            index=self.get_index_name(),
            doc_id=self.id,
            document=self.prepare_document()
        )

    def remove_instance_from_index(self, index: str = None) -> None:
        if index is None:
            index = self.get_index_name()
        self.es_service.remove_from_index(
            index=index,
            doc_id=self.id
        )

    @classmethod
    def search(cls: db.Model, expression: str, page: int, per_page: int) -> (list, int):
        ids, total = es_service.query_index(cls.get_index_name(), expression, page, per_page)
        if total == 0:
            return [], 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        query = sa.select(cls).where(cls.id.in_(ids)).order_by(
            db.case(*when, value=cls.id))
        return db.session.scalars(query), total

    @classmethod
    def before_commit(cls: db.Model, session: db.session) -> None:
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls: db.Model, session: db.session) -> None:
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                obj.add_instance_to_index()
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                obj.add_instance_to_index()
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                obj.remove_instance_from_index()
        session._changes = None

    @classmethod
    def reindex(cls: db.Model) -> None:

        cls.es_service.remove_all_docs_from_index(cls.get_index_name())

        doc_stream = (
            obj.prepare_data_to_bulk()
            for obj in db.session.scalars(sa.select(cls))
        )

        cls.es_service.stream_documents_to_index(
            doc_stream,
            chunk_size=1000
        )

    @classmethod
    def create_index(cls) -> None:
        cls.es_service.create_index(cls.get_index_name())
