
import sqlite3
from itertools import islice

import yaml

CONFIG_FILE_PATH = 'config.yml'

def main():
	"""
	The main function of the script.
	"""
	# load configs
	config = load_yml_config()
	input_file_path = config['input_file_path']
	output_file_path = config['output_file_path']
	database_path = config['database_path']
	batch_size = config['batch_size']
 
	# create database and result file
	result_file = open(output_file_path, 'w', encoding='utf-8')
	conn, cursor = create_database(database_path)

	# open the file and insert lines into database in batches
	with open(input_file_path, 'r', encoding='utf-8') as input_file:
		print("Inserting lines into database.", end='')
		while True:
			lines = list(islice(input_file, batch_size))
			if not lines:
				break
			print('.', end='')
			insert_lines_into_database(lines, conn, cursor)
	input_file.close()

	# query the database in batches and write the results to a file
	query_database_and_write_to_file(cursor, batch_size, result_file)
	result_file.close()
	print("Done. Result file created at: " + output_file_path)

def load_yml_config():
	"""
	Loads the configuration from the config.yml file.
 
	:return: A dictionary containing the configuration.
	"""
	with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as file:
		config = yaml.safe_load(file)
	return config

def create_database(db_name):
	"""
	Creates a SQLite database with the given name and returns the connection and cursor objects.

	:param db_name: The name of the database to be created.
	:return: A tuple containing the connection and cursor objects.
	"""
	conn = sqlite3.connect(db_name)
	conn.execute("PRAGMA synchronous=1")
	conn.execute("PRAGMA temp_store=MEMORY")
	conn.execute("PRAGMA locking_mode=EXCLUSIVE")
	conn.execute("PRAGMA cache_size=5000")
	conn.execute("PRAGMA page_size=4096")
	cursor = conn.cursor()
	cursor.execute('''
		DROP TABLE IF EXISTS lines
	''')
	cursor.execute('''
		CREATE TABLE lines (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			line TEXT
		)
	''')
	return conn, cursor

def insert_lines_into_database(lines, conn, cursor):
	"""
	Inserts the given lines into the database.

	:param lines: A list of lines to insert into the database.
	:param conn: The connection object to use for inserting into the database.
	:param cursor: The cursor object to use for inserting into the database.
	"""
	for line in lines:
		cursor.execute('INSERT INTO lines (line) VALUES (?)', (line,))
	conn.commit()

def query_database_and_write_to_file(cursor, batch_size, result_file):
	"""
	Queries the database using paging and writes the results to a file.

	:param cursor: The cursor object to use for querying the database.
	:param batch_size: The number of results to return per page.
	:param result_file: The file to write the results to.
	"""
	page = 0
	while True:
		cursor.execute('''
			SELECT line 
			FROM lines
			ORDER BY 
				CASE WHEN SUBSTR(line, 1, 1) GLOB '[0-9]' THEN 0 ELSE 1 END,
				CAST(SUBSTR(line, 1, INSTR(line || ' ', ' ') - 1) AS INTEGER), 
				line
			LIMIT ? OFFSET ?
		''', (batch_size, page * batch_size))
		results = cursor.fetchall()
		if not results:
			break
		write_to_file(results, result_file)
		page += 1

def write_to_file(results, result_file):
	"""
	Writes the results to a file.
	
 	:param results: A list of tuples containing the results.
	:param result_file: The file to write the results to.
	"""
	for result in results:
		result_file.write(result[0].strip() + '\n')


if __name__ == "__main__":
	main()
