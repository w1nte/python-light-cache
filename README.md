# light-cache 1.0.0
Light-Cache is a simple way to cache data with auto-expiring in the filesystem.

## Usage:
Create a cache file which has a expiration time of 10 minutes.
After 10 minutes, the cache file will automatically be invalid, "cache.get" returns false and deletes the file.
```python
>>> from light_cache import Cache
>>> cache = Cache()
>>> cache.set('c1', b'Hello World', 600)  # expiration time of 10 minutes
>>> print(cache.get('c1'))
...
b'Hello World'
...
>>> cache.clean()
```

To clean up all expired cache files, call ```cache.clean()``` at the end of the script.

## Reference:
* Cache(default_expiration=60, directory='cache')
    * set(name, content, expiry=default_expiration)
    * get(name)
    * remove(name, force=true)
    * clean(force=false)

## Requirements:
Tested with Python Version 2.7.10 and 3.4.3

## Licence
This projekt is licensed under the MIT License - see the LICENSE.md file for details
