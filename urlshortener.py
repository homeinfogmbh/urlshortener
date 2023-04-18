"""ORM models."""

from __future__ import annotations
from string import ascii_letters, digits
from typing import Union

from flask import Flask, Response, redirect, request
from peewee import AutoField, TextField

from basex import decode, encode
from peeweeplus import JSONModel, MySQLDatabaseProxy
from wsgilib import JSON, JSONMessage


__all__ = ['MANAGER', 'RESOLVER', 'ShortURL']


DATABASE = MySQLDatabaseProxy('urlshortener')
MANAGER = Flask('manager')
POOL = ascii_letters + digits
EXCLUDE = '0oO1ilIL'

for excluded in EXCLUDE:
    POOL = POOL.replace(excluded, '')

RESOLVER = Flask('resolver')


class ShortURL(JSONModel):
    """Table for shortened URLs."""

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

    def to_json(self) -> dict[str, Union[int, str]]:
        """Return a JSON-ish dict."""
        json = super().to_json()
        json['hash'] = self.hash
        return json


@MANAGER.route('/', methods=['POST'], strict_slashes=False)
def add_short_url() -> JSON:
    """Add a new short URL."""

    try:
        short_url = ShortURL.get(ShortURL.url == request.json)
    except ShortURL.DoesNotExist:
        short_url = ShortURL(url=request.json)
        short_url.save()

    return JSON(short_url.hash)


@MANAGER.route('/<hash_>', methods=['DELETE'])
def delete_short_url(hash_: str) -> JSONMessage:
    """Delete a short URL."""

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
def resolve_short_url(hash_: str) -> Response:
    """Resolve a short URL."""

    return redirect(ShortURL.by_hash(hash_).url)
