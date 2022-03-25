def special_sort(source_endpoint_func):
    numbers = source_endpoint_func()

    odds = []
    evens = []
    for n in numbers:
        if n % 2 == 0:
            evens.append(n)
        else:
            odds.append(n)

    return sorted(odds) + sorted(evens)


import requests


def make_a_request():
    r = requests.get('https://duckduckgo.com/')
    return r.json

