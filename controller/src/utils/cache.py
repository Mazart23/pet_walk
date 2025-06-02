from flask import Flask
from flask_caching import Cache


cache: Cache | None = None


def configure_cache(app: Flask):
    global cache
    app.config['CACHE_TYPE'] = 'SimpleCache'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 86400 # 24h
    cache = Cache(app)