from pytest import mark
from databases import Deta, Local, Temp

dbs = [Deta('test'), Local('test'), Temp('test')]

@mark.parametrize("db", dbs)
def test_add_get(db):
    db['foo'] = 'bar'
    assert db['foo'] == 'bar'

@mark.parametrize("db", dbs)
def test_remove_contains(db):
    del db['foo']
    assert 'foo' not in db

@mark.parametrize("db", dbs)
def test_save_list(db):
    with open('assets/logo.png', 'rb') as file:
        fb = file.read()
    db.save(fb, 'logo.png')
    assert 'logo.png' in db.list()

@mark.parametrize("db", dbs)
def test_delete_contains(db):
    db.delete('logo.png')
    assert not db.contains('logo.png')