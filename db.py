#! /usr/bin/env python
#! db.py

"""This module provides quick methods for handling databases using MySQLdb.

Provides functionality for:
- Creating and dropping tables
- Running arbitrary SQL queries
- Common SQL queries
"""

import MySQLdb as mdb
import sys
import logging

def encode_field_pair(field_pair, primary_key, auto_inc=None):
    """Encodes a (field_name, type_description) pair as a string for the SQL CREATE TABLE
    statement. The primary key and auto-incrementing field (if any) are to be specified by name.

    This method is used to build field descriptors for creating tables. It is unlikely that the
    client will ever have to call it directly. 
    """
    field_name, type_desc = field_pair
    ret = field_name + " " + type_desc
    if field_name == primary_key:
        ret += ' PRIMARY KEY'
    if field_name == auto_inc:
        ret += ' AUTO_INCREMENT'
    return ret

def build_field_descriptor(fields, primary_key, auto_inc=None):
    """Returns a field descriptor for table creation.

    This returns a string consisting of the part of the CREATE TABLE statement that describes the
    structure of the table. The fields are specified as a list of strings of the form '<field_name>
    <field_type>'.
    """
    field_pairs = (field.split() for field in fields)
    ret = ', '.join(encode_field_pair(pair, primary_key, auto_inc) for pair in field_pairs)
    return '(' + ret + ')'

def build_create_command(table_name, overwrite=False):
    "Builds part of the table creation SQL query."
    command = 'CREATE TABLE '
    if overwrite:
        command += 'IF NOT EXISTS '
    command += table_name
    return command

def run_query(conn, query, commit=False):
    "Executes an SQL query."
    cursor = conn.cursor()
    cursor.execute(query)
    if commit:
        conn.commit()
    return cursor

def create_table(conn, name, fields, primary_key, auto_inc=None, overwrite=False):
    "Creates a database table based on the provided specification."
    try:
        command = build_create_command(name, overwrite=overwrite)
        field_desc = build_field_descriptor(fields, primary_key, auto_inc)
        query = command + " " + field_desc
        run_query(conn, query)
        
    except mdb.Error, e:
        DB_ERROR("Table creation failed!")

def drop_table(conn, name):
    "Drops a table from the current database."
    try:
        query = "drop table " + name
        run_query(conn, query)
    except mdb.Error, e:
        DB_ERROR("Table drop failed!")

def get_rows(cursor):
    "Returns the rows of the fetch operation represented by this cursor."
    return cursor.fetchall()

def get_column(conn, table_name, column_name, limit=None):
    "Returns a list of the contents of a single column in a table."
    try:
        cursor = conn.cursor(mdb.cursors.DictCursor)
        query = "SELECT %s from %s" % (column_name, table_name)
        if limit is not None:
            query += " LIMIT %d" % limit
        cursor.execute(query)
        rows = cursor.fetchall()
        return [row[column_name] for row in rows]
    
    except mdb.Error, e:
        DB_ERROR(e, "DATABASE READ FAILED")

#################### ERROR HANDLING ################################################################

def init_error_logging(logfile):
    "Start error logging with the specified log file."
    logging.basicConfig(filename=logfile, level=logging.ERROR,
                        format='%(asctime)s | %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def DB_ERROR(error, msg, die=False):
    "Simple error handling in case of an error."
    msg = '%s - Error %s' % (msg, error.args)
    print msg
    logging.error(msg)
    if die:
        sys.exit(1)


def test_fpenc():
    # Test field pair encoding function.
    print encode_field_pair(('name', 'VARCHAR(20)'), 'id')
    print encode_field_pair(('name', 'VARCHAR(20)'), 'name')
    print encode_field_pair(('name', 'VARCHAR(20)'), 'id', auto_inc='blah')
    print encode_field_pair(('name', 'VARCHAR(20)'), 'id', auto_inc='name')
    print encode_field_pair(('name', 'VARCHAR(20)'), 'name', auto_inc='id')
    print encode_field_pair(('name', 'VARCHAR(20)'), 'name', auto_inc='name')
    

def test_bfdesc():
    fields = ['name VARCHAR(20)', 'id INT', 'freq DOUBLE']
    primary_key = 'id'
    auto_inc = 'freq'
    print build_field_descriptor(fields, primary_key)
    print build_field_descriptor(fields, primary_key, auto_inc)


def test_error():
    init_error_logging("/tmp/mytest.log")
    DB_ERROR(SyntaxError("Too many arguments"), "Unpacking failed!")
    import utils.extraction as ext
    print ext.text('/tmp/mytest.log')

def test_build():
    print build_create_command('foobar') 
    print build_create_command('foobar', True)
    print build_create_command('foobar', False)

def test_rquery(conn):
    print get_rows(run_query(conn, 'SHOW TABLES'))
    print get_rows(run_query(conn, 'SELECT * FROM Writers'))

def test_gcolumn(conn):
    print get_column(conn, 'Writers', 'Name')
    print get_column(conn, 'Writers', 'Id', limit=2)
    print get_column(conn, 'Writers', 'blah')

    
def test_tables(conn):
    create_table(conn, 'foobar', ['name VARCHAR(20)', 'id INT', 'freq DOUBLE'], 'id')
    print get_rows(run_query(conn, 'show tables'))
    print get_rows(run_query(conn, 'desc foobar'))
    drop_table(conn, 'foobar')
    print get_rows(run_query(conn, 'show tables'))
    
def separator():
    print '########################################\n'
    
def test():
    conn = mdb.connect('localhost', 'test', 'testpass', 'testdb')
    test_fpenc()
    separator()
    test_bfdesc()
    separator()
    test_error()
    separator()
    test_build()
    separator()
    test_rquery(conn)
    separator()
    test_gcolumn(conn)
    separator()
    test_tables(conn)