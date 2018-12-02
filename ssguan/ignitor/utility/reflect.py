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
"""
    Reflect utilities.
"""

import functools
import inspect

import six

from ssguan.ignitor.base.error import NoFoundError


def wrap_func(func, *args, **kwargs):
    wrapper = functools.partial(func, *args, **kwargs)
    try:
        functools.update_wrapper(wrapper, func)
    except AttributeError:
        # func already wrapped by funcols.partial won't have
        # __name__, __module__ or __doc__ and the update_wrapper()
        # call will fail.
        pass
    return wrapper

def import_module(path):
    """
        import module from string
        :param str funcpath: the string of absolute path a module
    """
    try:
        if "." in path:
            modpath, hcls = path.rsplit('.', 1)
            mod = __import__(modpath, None, None, [''])
            mod = getattr(mod, hcls)
        else:
            mod = __import__(path, None, None, [''])
    except:
        raise NoFoundError("module", path)
    return mod

def get_function_path(func, bound_to=None):
    """
        Get received func path (as string), to import func later with `import_string`.
    """
    if isinstance(func, six.string_types):
        return func

    # static and class methods
    if hasattr(func, '__func__'):
        real_func = func.__func__
    elif callable(func):
        real_func = func
    else:
        return func

    func_path = []

    module = getattr(real_func, '__module__', '__main__')
    if module:
        func_path.append(module)

    if not bound_to:
        try:
            bound_to = six.get_method_self(func)
        except AttributeError:
            pass

    if bound_to:
        if isinstance(bound_to, six.class_types):
            func_path.append(bound_to.__name__)
        else:
            func_path.append(bound_to.__class__.__name__)

    func_path.append(real_func.__name__)
    return '.'.join(func_path)

def get_function_args(func):
    """
        Return FullArgSpec(args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations)
    """
    return inspect.getfullargspec(func)

def eval_script(script, **kwargs):
    """
        Execute a python script.
    """    
    if script == '':
        return True
    if type(script) != str:
        return script(**kwargs)
    else:
        return eval(script, kwargs)