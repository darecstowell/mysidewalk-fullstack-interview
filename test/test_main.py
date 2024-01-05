import os
import sqlite3
import unittest
from unittest import mock

from main import (
    CONFIG_FILE_PATH,
    create_database,
    insert_lines_into_database,
    load_yml_config,
    query_database_and_write_to_file,
    write_to_file,
)


class TestMain(unittest.TestCase):
	def test_load_yml_config(self):
		# Test case 1: Loading configuration from config.yml
		with mock.patch('builtins.open', mock.mock_open(read_data='key: value\n')) as mock_file:
			config = load_yml_config()
			mock_file.assert_called_once_with(CONFIG_FILE_PATH, 'r', encoding='utf-8')
			self.assertEqual(config, {'key': 'value'})
	
	def test_write_to_file(self):
		# Test case 1: Empty results list
		file_name = './test/test_results.txt'
		results = []
		result_file = open(file_name, 'w', encoding='utf-8')
		write_to_file(results, result_file)
		result_file.close()
		with open(file_name, 'r', encoding='utf-8') as file:
			self.assertEqual(file.read(), '')
		os.remove(file_name)

		# Test case 2: Single result
		results = [('Result 1',)]
		result_file = open(file_name, 'w', encoding='utf-8')
		write_to_file(results, result_file)
		result_file.close()
		with open(file_name, 'r', encoding='utf-8') as file:
			self.assertEqual(file.read(), 'Result 1\n')
		os.remove(file_name)

		# Test case 3: Multiple results
		results = [('Result 1',), ('Result 2',), ('Result 3',)]
		result_file = open(file_name, 'w', encoding='utf-8')
		write_to_file(results, result_file)
		result_file.close()
		with open(file_name, 'r', encoding='utf-8') as file:
			self.assertEqual(file.read(), 'Result 1\nResult 2\nResult 3\n')
		os.remove(file_name)

	def test_create_database_and_insert_lines(self):
		# Test case 1: Creating a database
		db_name = './test/test.db'
		conn, cursor = create_database(db_name)
		self.assertIsInstance(conn, sqlite3.Connection)
		self.assertIsInstance(cursor, sqlite3.Cursor)
		cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lines'")
		self.assertEqual(cursor.fetchone()[0], 'lines')
		conn.close()
		os.remove(db_name)
		
		# Test case 1: Empty lines list
		lines = []
		conn, cursor = create_database(db_name)
		insert_lines_into_database(lines, conn, cursor)
		cursor.execute('SELECT line FROM lines')
		self.assertEqual(cursor.fetchall(), [])
		conn.close()
		os.remove(db_name)

		# Test case 2: Single line
		lines = ['Line 1']
		conn, cursor = create_database(db_name)
		insert_lines_into_database(lines, conn, cursor)
		cursor.execute('SELECT line FROM lines')
		self.assertEqual(cursor.fetchall(), [('Line 1',)])
		conn.close()
		os.remove(db_name)

		# Test case 3: Multiple lines
		lines = ['Line 1', 'Line 2', 'Line 3']
		conn, cursor = create_database(db_name)
		insert_lines_into_database(lines, conn, cursor)
		cursor.execute('SELECT line FROM lines')
		self.assertEqual(cursor.fetchall(), [('Line 1',), ('Line 2',), ('Line 3',)])
		conn.close()
		os.remove(db_name)
  
	def test_query_database_and_write_to_file(self):
		# Test case 1: Empty database
		db_name = './test/test.db'
		file_name = './test/test_results.txt'
		conn, cursor = create_database(db_name)
		result_file = open(file_name, 'w', encoding='utf-8')
		query_database_and_write_to_file(cursor, 10, result_file)
		result_file.close()
		with open(file_name, 'r', encoding='utf-8') as file:
			self.assertEqual(file.read(), '')
		conn.close()
		os.remove(db_name)
		os.remove(file_name)

		# Test case 2: Single page of results
		conn, cursor = create_database(db_name)
		insert_lines_into_database(['Line 1', 'Line 2', 'Line 3'], conn, cursor)
		result_file = open(file_name, 'w', encoding='utf-8')
		query_database_and_write_to_file(cursor, 10, result_file)
		result_file.close()
		with open(file_name, 'r', encoding='utf-8') as file:
			self.assertEqual(file.read(), 'Line 1\nLine 2\nLine 3\n')
		conn.close()
		os.remove(db_name)
		os.remove(file_name)

		# Test case 3: Multiple pages of results
		conn, cursor = create_database(db_name)
		lines = ['{} Line'.format(i) for i in range(1, 11)]
		insert_lines_into_database(lines, conn, cursor)
		result_file = open(file_name, 'w', encoding='utf-8')
		query_database_and_write_to_file(cursor, 10, result_file)
		result_file.close()
		with open(file_name, 'r', encoding='utf-8') as file:
			self.assertEqual(file.read(), '1 Line\n2 Line\n3 Line\n4 Line\n5 Line\n6 Line\n7 Line\n8 Line\n9 Line\n10 Line\n')
		conn.close()
		os.remove(db_name)
		os.remove(file_name)
		
if __name__ == '__main__':
	unittest.main()