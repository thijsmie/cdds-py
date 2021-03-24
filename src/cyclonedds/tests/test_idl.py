import pytest

from cyclonedds.idl import compile


def test_compile_idl(tmp_path):
    file = tmp_path / "test.idl"
    file.write_text("""module test { struct TestData { string data; }; };""")
    types = compile(file)
    t = types[0].TestData(data="Hi!")
    