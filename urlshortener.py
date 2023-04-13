"""ORM models."""

from __future__ import annotations
from string import ascii_letters, digits

from flask import Flask, Response, redirect, request
from peewee import AutoField, TextField

from basex import decode, encode
from peeweeplus import JSONModel, MySQLDatabaseProxy
from wsgilib import JSON, JSONMessage


__all__ = ['MANAGER', 'RESOLVER', 'ShortURL']


DATABASE = MySQLDatabaseProxy('urlshortener')
MANAGER = Flask('manager')
POOL = ascii_letters + digits
RESOLVER = Flask('resolver')


class ShortURL(JSONModel):
    """Table for URLs."""

    class Meta:
        table_name = 'short_url'
        database = DATABASE
        schema = database.database

    id = AutoField()
    url = TextField()

    @classmethod
    def by_hash(cls, hash_: str) -> ShortURL:
        """Return the URL record by the given hash."""
        return cls.get(cls.id == decode(hash_, POOL))

    @property
    def hash(self) -> str:
        """Returns the URL's hash."""
        return encode(self.id, POOL)


@MANAGER.route('/', methods=['POST'], strict_slashes=False)
def add_url() -> JSON:
    """Add a new URL."""

    url = ShortURL(url=request.json)
    url.save()
    return JSON(url.id)


@MANAGER.route('/<hash_>', methods=['DELETE'])
def delete_url(hash_: str) -> JSONMessage:
    """Add a new URL."""

    try:
        short_url = ShortURL.by_hash(hash_)
    except ShortURL.DoesNotExist:
        return JSONMessage('No such URL', status=404)

    short_url.delete_instance()
    return JSONMessage('Short URL deleted.', status=200)


@MANAGER.route('/', methods=['GET'], strict_slashes=False)
def list_short_urls() -> JSON:
    """List short URLs."""

    return JSON([short_url.to_json() for short_url in ShortURL])


@RESOLVER.route('/<hash_>', methods=['GET'])
def resolve_url(hash_: str) -> Response:
    """Resolve a URL."""

    return redirect(ShortURL.by_hash(hash_).url)
