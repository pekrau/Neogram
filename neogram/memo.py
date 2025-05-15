"""Singleton set for detecting cyclical refences in YAML includes.
This probably won't work in multi-threaded situations.
"""

_memo = set()

def clear():
    global _memo
    _memo.clear()


def check(key):
    global _memo
    key = repr(key)
    if key in _memo:
        raise ValueError

def add(key):
    global _memo
    key = repr(key)
    _memo.add(key)

def check_add(key):
    check(key)
    add(key)

def remove(key):
    global _memo
    key = repr(key)
    _memo.remove(key)
