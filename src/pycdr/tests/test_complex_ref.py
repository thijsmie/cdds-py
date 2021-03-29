import pytest
from test_classes import List, Node


def test_complex_nested_type():
    a = List([Node([Node([]), Node([Node([])])]), Node([])])

    assert a == List.deserialize(a.serialize())
