from omniutils.dictionary_utils import DictionaryUtils

def test_expand_lists_recursive_simple():
    data = {
        "id": 1,
        "tags": ["python", "utils"],
        "meta": {"author": "user", "likes": [10, 20]}
    }
    expected = [
        {'id': 1, 'tags': 'python', 'meta__author': 'user', 'meta__likes': 10},
        {'id': 1, 'tags': 'python', 'meta__author': 'user', 'meta__likes': 20},
        {'id': 1, 'tags': 'utils',  'meta__author': 'user', 'meta__likes': 10},
        {'id': 1, 'tags': 'utils',  'meta__author': 'user', 'meta__likes': 20}
    ]
    expanded = DictionaryUtils.expand_lists_recursive(data)

    # Ordena as listas de dicionários para uma comparação consistente,
    # ordenando pelas chaves 'tags' e 'meta__likes'.
    sort_key = lambda d: (d.get('tags'), d.get('meta__likes'))
    assert sorted(expanded, key=sort_key) == sorted(expected, key=sort_key)
