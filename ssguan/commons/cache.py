# -*- coding: utf-8 -*-
#  Copyright 2015 www.suishouguan.com
#
#  Licensed under the Private License (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://github.com/samuelbaizg/ssguan/blob/master/LICENSE
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import unicode_literals

import collections
import functools
import inspect
import pickle
import threading
import time

import six

from ssguan import config
from ssguan.commons import typeutils, funcutils, loggingg


_logger = loggingg.get_logger(config.LOGGER_COMMONS)


class Value(object):

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


NOT_FOUND = Value('NOT_FOUND')
NOT_SET = Value('NOT_SET')
# Stub class to ensure not passing in a `timeout` argument results in
# the default timeout
DEFAULT_TIMEOUT = Value('DEFAULT_TIMEOUT')

MEMCACHE_MAX_KEY_LENGTH = 250


def default_key_func(key, key_prefix, version):
    """
    Default function to generate keys.

    Constructs the key used by all other methods. By default it prepends
    the `key_prefix'. KEY_FUNCTION can be used to specify an alternate
    function with custom key making behavior.
    """
    return '%s:%s:%s' % (key_prefix, version, key)


def get_key_func(key_func):
    """
    Function to decide which key function to use.

    Defaults to ``default_key_func``.
    """
    if key_func is not None:
        if callable(key_func):
            return key_func
        else:
            return funcutils.import_module(key_func)
    return default_key_func


class BaseCache(object):
    """
    Base Cache class.
    """

    def __init__(self, params):
        timeout = params.get('timeout', params.get('TIMEOUT', 300))
        if timeout is not None:
            try:
                timeout = int(timeout)
            except (ValueError, TypeError):
                timeout = 300
        self.default_timeout = timeout

        options = params.get('OPTIONS', {})
        max_entries = params.get(
            'max_entries', options.get('MAX_ENTRIES', 300))
        try:
            self._max_entries = int(max_entries)
        except (ValueError, TypeError):
            self._max_entries = 300

        cull_frequency = params.get(
            'cull_frequency', options.get('CULL_FREQUENCY', 3))
        try:
            self._cull_frequency = int(cull_frequency)
        except (ValueError, TypeError):
            self._cull_frequency = 3

        self.key_prefix = params.get('KEY_PREFIX', '')
        self.version = params.get('VERSION', 1)
        self.key_func = get_key_func(params.get('KEY_FUNCTION'))

    def get_backend_timeout(self, timeout=DEFAULT_TIMEOUT):
        """
        Returns the timeout value usable by this backend based upon the provided
        timeout.
        """
        if timeout == DEFAULT_TIMEOUT:
            timeout = self.default_timeout
        elif timeout == 0:
            # ticket 21147 - avoid time.time() related precision issues
            timeout = -1
        return None if timeout is None else time.time() + timeout

    def make_key(self, key, version=None):
        """Constructs the key used by all other methods. By default it
        uses the key_func to generate a key (which, by default,
        prepends the `key_prefix' and 'version'). A different key
        function can be provided at the time of cache construction;
        alternatively, you can subclass the cache backend to provide
        custom key making behavior.
        """
        if version is None:
            version = self.version

        new_key = self.key_func(key, self.key_prefix, version)
        return new_key

    def add(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        """
        Set a value in the cache if the key does not already exist. If
        timeout is given, that timeout will be used for the key; otherwise
        the default cache timeout will be used.

        Returns True if the value was stored, False otherwise.
        """
        raise NotImplementedError(
            'subclasses of BaseCache must provide an add() method')

    def get(self, key, default=None, version=None):
        """
        Fetch a given key from the cache. If the key does not exist, return
        default, which itself defaults to None.
        """
        raise NotImplementedError(
            'subclasses of BaseCache must provide a get() method')

    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        """
        Set a value in the cache. If timeout is given, that timeout will be
        used for the key; otherwise the default cache timeout will be used.
        """
        raise NotImplementedError(
            'subclasses of BaseCache must provide a set() method')

    def delete(self, key, version=None):
        """
        Delete a key from the cache, failing silently.
        """
        raise NotImplementedError(
            'subclasses of BaseCache must provide a delete() method')

    def get_many(self, keys, version=None):
        """
        Fetch a bunch of keys from the cache. For certain backends (memcached,
        pgsql) this can be *much* faster when fetching multiple values.

        Returns a dict mapping each key in keys to its value. If the given
        key is missing, it will be missing from the response dict.
        """
        d = {}
        for k in keys:
            val = self.get(k, version=version)
            if val is not None:
                d[k] = val
        return d

    def get_or_set(self, key, default=None, timeout=DEFAULT_TIMEOUT, version=None):
        """
        Fetch a given key from the cache. If the key does not exist,
        the key is added and set to the default value. The default value can
        also be any callable. If timeout is given, that timeout will be used
        for the key; otherwise the default cache timeout will be used.

        Return the value of the key stored or retrieved.
        """
        if default is None:
            raise ValueError('You need to specify a value.')
        val = self.get(key, version=version)
        if val is None:
            if callable(default):
                default = default()
            self.add(key, default, timeout=timeout, version=version)
            # Fetch the value again to avoid a race condition if another caller
            # added a value between the first get() and the add() above.
            return self.get(key, default, version=version)
        return val

    def has_key(self, key, version=None):
        """
        Returns True if the key is in the cache and has not expired.
        """
        return self.get(key, version=version) is not None

    def incr(self, key, delta=1, version=None):
        """
        Add delta to value in the cache. If the key does not exist, raise a
        ValueError exception.
        """
        value = self.get(key, version=version)
        if value is None:
            raise ValueError("Key '%s' not found" % key)
        new_value = value + delta
        self.set(key, new_value, version=version)
        return new_value

    def decr(self, key, delta=1, version=None):
        """
        Subtract delta from value in the cache. If the key does not exist, raise
        a ValueError exception.
        """
        return self.incr(key, -delta, version=version)

    def __contains__(self, key):
        """
        Returns True if the key is in the cache and has not expired.
        """
        # This is a separate method, rather than just a copy of has_key(),
        # so that it always has the same functionality as has_key(), even
        # if a subclass overrides it.
        return self.has_key(key)

    def set_many(self, data, timeout=DEFAULT_TIMEOUT, version=None):
        """
        Set a bunch of values in the cache at once from a dict of key/value
        pairs.  For certain backends (memcached), this is much more efficient
        than calling set() multiple times.

        If timeout is given, that timeout will be used for the key; otherwise
        the default cache timeout will be used.
        """
        for key, value in data.items():
            self.set(key, value, timeout=timeout, version=version)

    def delete_many(self, keys, version=None):
        """
        Delete a bunch of values in the cache at once. For certain backends
        (memcached), this is much more efficient than calling delete() multiple
        times.
        """
        for key in keys:
            self.delete(key, version=version)

    def clear(self):
        """Remove *all* values from the cache at once."""
        raise NotImplementedError(
            'subclasses of BaseCache must provide a clear() method')

    def validate_key(self, key):
        """
        Warn about keys that would not be portable to the memcached
        backend. This encourages (but does not force) writing backend-portable
        cache code.
        """
        if len(key) > MEMCACHE_MAX_KEY_LENGTH:
            """_logger.warn(
                'Cache key will cause errors if used with memcached: %r '
                '(longer than %s)' % (key, MEMCACHE_MAX_KEY_LENGTH)
            )"""
        for char in key:
            if ord(char) < 33 or ord(char) == 127:
                """_logger.warn(
                    'Cache key contains characters that will cause errors if '
                    'used with memcached: %r' % key
                )"""
                break

    def incr_version(self, key, delta=1, version=None):
        """Adds delta to the cache version for the supplied key. Returns the
        new version.
        """
        if version is None:
            version = self.version

        value = self.get(key, version=version)
        if value is None:
            raise ValueError("Key '%s' not found" % key)

        self.set(key, value, version=version + delta)
        self.delete(key, version=version)
        return version + delta

    def decr_version(self, key, delta=1, version=None):
        """Subtracts delta from the cache version for the supplied key. Returns
        the new version.
        """
        return self.incr_version(key, -delta, version)

    def close(self, **kwargs):
        """Close the cache connection"""
        pass


# Global in-memory store of cache data. Keyed by name, to provide
# multiple named local memory caches.
_locmem_caches = {}
_locmem_expire_info = {}
_locmem_locks = {}


class LocMemCache(BaseCache):
    def __init__(self, name, params):
        BaseCache.__init__(self, params)
        self._cache = _locmem_caches.setdefault(name, {})
        self._expire_info = _locmem_expire_info.setdefault(name, {})
        self._lock = _locmem_locks.setdefault(name, funcutils.RWLock())

    def add(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        pickled = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
        with self._lock.writer():
            if self._has_expired(key):
                self._set(key, pickled, timeout)
                return True
            return False

    def get(self, key, default=None, version=None, acquire_lock=True):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        pickled = None
        with (self._lock.reader() if acquire_lock else funcutils.contextmanager_dummy()):
            if not self._has_expired(key):
                pickled = self._cache[key]
        if pickled is not None:
            try:
                return pickle.loads(pickled)
            except pickle.PickleError:
                return default

        with (self._lock.writer() if acquire_lock else funcutils.contextmanager_dummy()):
            try:
                del self._cache[key]
                del self._expire_info[key]
            except KeyError:
                pass
            return default

    def _set(self, key, value, timeout=DEFAULT_TIMEOUT):
        if len(self._cache) >= self._max_entries:
            self._cull()
        self._cache[key] = value
        self._expire_info[key] = self.get_backend_timeout(timeout)

    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        pickled = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
        with self._lock.writer():
            self._set(key, pickled, timeout)

    def incr(self, key, delta=1, version=None):
        with self._lock.writer():
            value = self.get(key, version=version, acquire_lock=False)
            if value is None:
                raise ValueError("Key '%s' not found" % key)
            new_value = value + delta
            key = self.make_key(key, version=version)
            pickled = pickle.dumps(new_value, pickle.HIGHEST_PROTOCOL)
            self._cache[key] = pickled
        return new_value

    def has_key(self, key, version=None):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        with self._lock.reader():
            if not self._has_expired(key):
                return True

        with self._lock.writer():
            try:
                del self._cache[key]
                del self._expire_info[key]
            except KeyError:
                pass
            return False

    def _has_expired(self, key):
        exp = self._expire_info.get(key, -1)
        if exp is None or exp > time.time():
            return False
        return True

    def _cull(self):
        if self._cull_frequency == 0:
            self.clear()
        else:
            doomed = [k for (i, k) in enumerate(self._cache)
                      if i % self._cull_frequency == 0]
            for k in doomed:
                self._delete(k)

    def _delete(self, key):
        try:
            del self._cache[key]
        except KeyError:
            pass
        try:
            del self._expire_info[key]
        except KeyError:
            pass

    def delete(self, key, version=None):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        with self._lock.writer():
            self._delete(key)

    def clear(self):
        self._cache.clear()
        self._expire_info.clear()


def force_text(obj):
    if isinstance(obj, six.text_type):
        return obj
    try:
        return six.text_type(obj)
    except UnicodeDecodeError:
        return obj.decode('utf-8')


def force_binary(obj):
    if isinstance(obj, six.binary_type):
        return obj

    try:
        return six.binary_type(obj)
    except UnicodeEncodeError:
        return obj.encode('utf-8')


META_ACCEPTED_ATTR = '_cache_meta_accepted'
META_ARG_NAME = 'meta'


class CacheHandler(object):
    """
    A Cache Handler to manage access to Cache instances.

    Ensures only one instance of each alias exists per thread.
    """

    def __init__(self):
        self._caches = threading.local()

    def __getitem__(self, alias):
        try:
            return self._caches.caches[alias]
        except AttributeError:
            self._caches.caches = {}
        except KeyError:
            pass

        cache = self._create_cache(alias)
        self._caches.caches[alias] = cache
        return cache

    def all(self):
        return getattr(self._caches, 'caches', {}).values()

    def _create_cache(self, backend, **kwargs):
        params = {"TIMEOUT": config.cacheCFG.get_default_cache_timeout(),
                  "KEY_PREFIX": "locmem"
                  }
        return LocMemCache(config.cacheCFG.get_default_cache_alias(), params)


_cache_backends = CacheHandler()


def create_cache_key(*parts):
    """ Generate cache key using global delimiter char """
    if len(parts) == 1:
        parts = parts[0]
        if isinstance(parts, six.string_types):
            parts = [parts]

    return config.cacheCFG.get_cache_key_delimiter().join(force_text(p) for p in parts)


def create_tag_cache_key(*parts):
    return create_cache_key(config.cacheCFG.get_tag_prefix(), *parts)


def get_timestamp():
    return int(time() * 1000000)


class MetaCallable(collections.Mapping):
    """ Object contains meta information about method or function decorated with dec_cached,
        passed arguments, returned results, signature description and so on.
    """

    def __init__(self, args=(), kwargs=None, returned_value=NOT_SET, call_args=None):
        self.args = args
        self.kwargs = kwargs or {}
        self.returned_value = returned_value
        self.call_args = call_args or {}
        self.function = None
        self.scope = None

    def __contains__(self, item):
        return item in self.call_args

    def __iter__(self):
        return iter(self.call_args)

    def __len__(self):
        return len(self.call_args)

    def __getitem__(self, item):
        return self.call_args[item]

    @property
    def has_returned_value(self):
        return self.returned_value is not NOT_SET


class TaggedCacheProxy(object):
    """ Each cache key/value pair can have additional tags to check
     if cached values is still valid.
    """

    def __init__(self, cache_instance):
        """
            :param cache_instance: should support `set_many` and
            `get_many` operations
        """
        self._cache = cache_instance

    def make_value(self, key, value, tags):
        data = {}
        tags = [create_tag_cache_key(_) for _ in tags]

        # get tags and their cached values (if exists)
        tags_dict = self._cache.get_many(tags)

        # set new timestamps for missed tags
        for tag_key in tags:
            if tag_key not in tags_dict:
                # this should be sent to cache as separate key-value
                data[tag_key] = get_timestamp()

        tags_dict.update(data)

        data[key] = {
            'value': value,
            'tags': tags_dict,
        }

        return data

    def __getattr__(self, item):
        return getattr(self._cache, item)

    def set(self, key, value, *args, **kwargs):
        value_dict = self.make_value(key, value, kwargs.pop('tags'))
        return self._cache.set_many(value_dict, *args, **kwargs)

    def get(self, key, default=None, **kwargs):
        value = self._cache.get(key, default=NOT_FOUND, **kwargs)

        # not found in cache
        if value is NOT_FOUND:
            return default

        tags_dict = value.get('tags')
        if not tags_dict:
            return value

        # check if it has valid tags
        cached_tags_dict = self._cache.get_many(tags_dict.keys())

        # compare dicts
        if typeutils.dict_to_hash(cached_tags_dict) != typeutils.dict_to_hash(tags_dict):
            # cache is invalid - return default value
            return default

        return value.get('value', default)

    def invalidate(self, tags):
        """ Invalidates cache by tags """
        ts = get_timestamp()
        return self._cache.set_many({create_tag_cache_key(tag): ts for tag in tags})


class Cached(object):

    if config.cacheCFG.is_lazymode():
        def _get_cache_instance(self):
            if self._cache_instance is None:
                return _cache_backends[self._cache_alias]
            return self._cache_instance
    else:
        def _get_cache_instance(self):
            if self._cache_instance is None:
                self._cache_instance = _cache_backends[self._cache_alias]
            return self._cache_instance

    cache_instance = property(_get_cache_instance)

    def __init__(self,
                 function,
                 cache_key=None,
                 timeout=DEFAULT_TIMEOUT,
                 cache_instance=None,
                 cache_alias=None,
                 as_property=False):

        # processing different types of cache_key parameter
        if cache_key is None:
            self.cache_key = self.create_cache_key
        elif isinstance(cache_key, (list, tuple)):
            self.cache_key = create_cache_key(
                force_text(key).join(('{', '}')) for key in cache_key
            )
        else:
            self.cache_key = cache_key

        self.function = function
        self.as_property = as_property
        self.timeout = timeout
        self.instance = None
        self.klass = None

        self._scope = None
        self._cache_instance = cache_instance
        self._cache_alias = cache_alias or config.cacheCFG.get_default_cache_alias()

    @property
    def scope(self):
        return self.instance or self.klass or self._scope

    @scope.setter
    def scope(self, value):
        self._scope = value

    def get_timeout(self, callable_meta):
        if isinstance(self.timeout, int) or self.timeout is DEFAULT_TIMEOUT:
            return self.timeout

        return self._format(self.timeout, callable_meta)

    def __call__(self, *args, **kwargs):
        callable_meta = self.collect_meta(args, kwargs)
        cache_key = self.generate_cache_key(callable_meta)
        cached_value = self.get_cached_value(cache_key)

        if cached_value is NOT_FOUND:
            value = self.function(*callable_meta.args, **callable_meta.kwargs)
            callable_meta.returned_value = value
            self.set_cached_value(cache_key, callable_meta)
            return value

#         _logger.debug('Hit cache_key="%s"', cache_key)
        return cached_value

    def create_cache_key(self, *args, **kwargs):
        """ if cache_key parameter is not specified we use default algorithm """
        scope = self.scope
        prefix = funcutils.get_function_path(self.function, scope)

        args = list(args)
        if scope:
            try:
                args.remove(scope)
            except ValueError:
                pass

        for k in sorted(kwargs):
            args.append(kwargs[k])
        return create_cache_key(prefix, *args)

    def update_arguments(self, args, kwargs):
        # if we got instance method or class method - modify positional
        # arguments
        if self.instance:
            # first argument in args is "self"
            args = (self.instance,) + args
        elif self.klass:
            # firs argument in args is "cls"
            args = (self.klass,) + args

        return args, kwargs

    def __get__(self, instance, klass):
        if instance is not None:
            # bound method
            self.instance = instance
        elif klass:
            # class method
            self.klass = klass

        if self.as_property and instance is not None:
            return self.__call__()

        return self

    def get_cached_value(self, cache_key):
        #         _logger.debug('Get cache_key="%s"', cache_key)
        return self.cache_instance.get(cache_key, NOT_FOUND)

    def set_cached_value(self, cache_key, callable_meta, **extra):
        timeout = self.get_timeout(callable_meta)
        if timeout is not DEFAULT_TIMEOUT:
            extra['timeout'] = timeout
#         _logger.debug('Set cache_key="%s" timeout="%s"', cache_key, extra.get('timeout'))
        self.cache_instance.set(
            cache_key, callable_meta.returned_value, **extra)

    @staticmethod
    def _check_if_meta_required(callable_template):
        """
        Checks if we need to provide `meta` arg into cache key constructor,
        there are two way to get this right.

            1. Use single `meta` argument:

            def construct_key(meta):
                ...

            2. User `dec_meta_accepted` decorator:

            @dec_meta_accepted
            def construct_key(m):
                ...

        """
        arg_spec = inspect.getargspec(callable_template)

        if getattr(callable_template, META_ACCEPTED_ATTR, False):
            return True
        elif (arg_spec.varargs is None and
              arg_spec.keywords is None and
              arg_spec.args == [META_ARG_NAME]):
            return True

        return False

    def _format(self, template, meta):
        if isinstance(template, (staticmethod, classmethod)):
            template = template.__func__

        if isinstance(template, collections.Callable):
            if self._check_if_meta_required(template):
                return template(meta)
            else:
                return template(*meta.args, **meta.kwargs)

        if not self.function:
            return template

        try:
            if isinstance(template, six.string_types):
                return force_text(template).format(**meta.call_args)
            elif isinstance(template, (list, tuple, set)):
                return [force_text(t).format(**meta.call_args) for t in template]
        except KeyError as ex:
            raise ValueError('Parameter "%s" is required for "%s"' %
                             (ex.message, template))

        raise TypeError(
            'Unsupported type for key template: {!r}'.format(type(template))
        )

    def collect_meta(self, args, kwargs, returned_value=NOT_SET):
        """ :returns: MetaCallable """
        args, kwargs = self.update_arguments(args, kwargs)

        meta = MetaCallable(args=args, kwargs=kwargs,
                            returned_value=returned_value)

        if not self.function:
            return meta

        # default arguments are also passed to template function
        arg_spec = inspect.getargspec(self.function)
        diff_count = len(arg_spec.args) - len(args)

        # do not provide default arguments which were already passed
        if diff_count > 0 and arg_spec.defaults:
            # take minimum here
            diff_count = min(len(arg_spec.defaults), diff_count)
            default_kwargs = dict(zip(arg_spec.args[-diff_count:],
                                      arg_spec.defaults[-diff_count:]))
        else:
            default_kwargs = {}

        default_kwargs.update(kwargs)
        meta.kwargs = default_kwargs
        meta.function = self.function
        meta.scope = self.scope

        try:
            meta.call_args = inspect.getcallargs(
                self.function, *args, **kwargs)
        except TypeError:
            # sometimes not all required parameters are provided, just ignore
            # them
            meta.call_args = meta.kwargs
        return meta

    def generate_cache_key(self, callable_meta):
        return self._format(self.cache_key, callable_meta)

    def invalidate_cache_by_key(self, *args, **kwargs):
        callable_meta = self.collect_meta(args, kwargs)
        cache_key = self.generate_cache_key(callable_meta)
        return self.cache_instance.delete(cache_key)

    def __unicode__(self):
        return (
            '<Cached: callable="{}", cache_key="{}", timeout={}>'.format(
                funcutils.get_function_path(self.function, self.scope),
                funcutils.get_function_path(self.cache_key),
                self.timeout)
        )

    def __str__(self):
        if six.PY2:
            return force_binary(self.__unicode__())
        return self.__unicode__()

    def __repr__(self):
        try:
            return self.__str__()
        except (UnicodeEncodeError, UnicodeDecodeError):
            return '[Bad Unicode data]'


class TaggedCached(Cached):
    """ Cache with tags and prefix support """

    def __init__(self,
                 function,
                 cache_key=None,
                 timeout=None,
                 cache_instance=None,
                 cache_alias=None,
                 as_property=False,
                 tags=(),
                 prefix=None):

        super(TaggedCached, self).__init__(
            function=function,
            cache_key=cache_key,
            cache_instance=cache_instance,
            cache_alias=cache_alias,
            timeout=timeout,
            as_property=as_property,
        )
        assert tags or prefix
        self.tags = tags
        self.prefix = prefix

        if self._cache_instance:
            self._cache_instance = TaggedCacheProxy(self.cache_instance)

    if config.cacheCFG.is_lazymode():
        @property
        def cache_instance(self):
            if self._cache_instance is None:
                return TaggedCacheProxy(_cache_backends[self._cache_alias])
            return self._cache_instance
    else:
        @property
        def cache_instance(self):
            if self._cache_instance is None:
                self._cache_instance = TaggedCacheProxy(
                    _cache_backends[self._cache_alias])
            return self._cache_instance

    def invalidate_cache_by_tags(self, tags=(), *args, **kwargs):
        """ Invalidate cache for this method or property by one of provided tags
            :type tags: str | list | tuple | callable
        """
        if not self.tags:
            raise ValueError('Tags were not specified, nothing to invalidate')

        def to_set(obj):
            return set([obj] if isinstance(obj, six.string_types) else obj)

        callable_meta = self.collect_meta(args, kwargs)
        all_tags = to_set(self._format(self.tags, callable_meta))

        if not tags:
            tags = all_tags
        else:
            tags = to_set(self._format(tags, callable_meta))
            if all_tags:
                tags = tags & all_tags

        return self.cache_instance.invalidate(tags)

    def invalidate_cache_by_prefix(self, *args, **kwargs):
        if not self.prefix:
            raise ValueError('Prefix was not specified, nothing to invalidate')

        callable_meta = self.collect_meta(args, kwargs)
        prefix = self._format(self.prefix, callable_meta)
        return self.cache_instance.invalidate([prefix])

    def generate_cache_key(self, callable_meta):
        cache_key = super(TaggedCached, self).generate_cache_key(callable_meta)
        if self.prefix:
            prefix = self._format(self.prefix, callable_meta)
            cache_key = create_cache_key(prefix, cache_key)
        return cache_key

    def set_cached_value(self, cache_key, callable_meta, **extra):
        # generate tags and prefix only after successful execution
        tags = self._format(self.tags, callable_meta)

        if self.prefix:
            prefix = self._format(self.prefix, callable_meta)
            tags = set(tags) | {prefix}

        return super(TaggedCached, self).set_cached_value(cache_key, callable_meta, tags=tags)

    def __unicode__(self):
        return six.text_type(
            '<TaggedCached: callable="{}", cache_key="{}", tags="{}", prefix="{}", '
            'timeout={}>'.format(
                funcutils.get_function_path(self.function, self.scope),
                funcutils.get_function_path(self.cache_key),
                funcutils.get_function_path(self.tags),
                funcutils.get_function_path(self.prefix),
                self.timeout)
        )

# noinspection PyPep8Naming


class dec_cached(object):
    """ Caches result of decorated callable.
        Possible use-cases are:

        @dec_cached()
        def func(...):

        @dec_cached('cache_key')  # cache key only
        def func(...):

        @dec_cached('cache_key', 300)  # cache key and timeout in seconds
        def func(...):

        @dec_cached('cache_key', 300, ('user', 'books'))  # + tags
        def func(...):

        @dec_cached('{a}:{b}')
        def func(a, b):  # cache keys based on method parameters

        @dec_cached(['a', 'b'])
        def func(a, b):  # cache keys based on method parameters

        @dec_cached(callable_with_parameters)
        def func(a, b):  # cache_key = callable_with_parameters(a, b)

    """

    def __init__(self, cache_key=None, timeout=config.cacheCFG.get_default_cache_timeout(), tags=(), prefix=None,
                 cache_instance=None, cache_alias=None):
        if tags or prefix:
            self.cache = TaggedCached(
                function=None,
                cache_key=cache_key,
                tags=tags,
                timeout=timeout,
                prefix=prefix,
                cache_instance=cache_instance,
                cache_alias=cache_alias,
            )
        else:
            self.cache = Cached(
                function=None,
                cache_key=cache_key,
                timeout=timeout,
                cache_instance=cache_instance,
                cache_alias=cache_alias,
            )

        self._instance = None
        self._class = None
        self._func = None
        self._wrapped = False

    def __get__(self, instance, owner):
        self._instance = instance
        self._class = owner
        return self.wrapper()

    def wrapper(self):
        if not self._wrapped:
            if self._instance or self._class:
                wrapped = self._func.__get__(self._instance, self._class)

                if isinstance(self._func, staticmethod):
                    # we don't need instance or class, however we need scope
                    self.cache.scope = self._instance or self._class
                    self._instance = None
                    self._class = None
                else:
                    wrapped = six.get_method_function(wrapped)
            else:
                wrapped = self._func

            functools.update_wrapper(self.cache, wrapped)
            self.cache.function = wrapped
            self.cache.instance = self._instance
            self.cache.klass = self._class
            self._wrapped = True

        return self.cache

    def __call__(self, func):
        self._func = func

        if isinstance(func, collections.Callable):
            return self.wrapper()

        return self

    def __repr__(self):
        return repr(self.cache)


def dec_cached_property(cache_key=None, timeout=config.cacheCFG.get_default_cache_timeout(), tags=(), prefix=None,
                        cache_instance=None, cache_alias=None):
    """ Works the same as `cached` decorator, but intended to use
        for properties, e.g.:

        class User(object):

            @dec_cached_property('{self.id}:friends_count', 120)
            def friends_count(self):
                return <calculated friends count>

    """
    def wrapper(func):
        if tags or prefix:
            cache = TaggedCached(
                function=func,
                cache_key=cache_key,
                tags=tags,
                timeout=timeout,
                prefix=prefix,
                cache_instance=cache_instance,
                cache_alias=cache_alias,
                as_property=True,
            )
        else:
            cache = Cached(
                function=func,
                cache_key=cache_key,
                timeout=timeout,
                cache_instance=cache_instance,
                cache_alias=cache_alias,
                as_property=True,
            )

        return cache

    return wrapper


def dec_meta_accepted(func):

    if isinstance(func, (staticmethod, classmethod)):
        _func = func.__func__
    else:
        _func = func
    setattr(_func, META_ACCEPTED_ATTR, True)

    return func
