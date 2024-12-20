DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS document;
DROP TABLE IF EXISTS observation;
DROP TABLE IF EXISTS document_filenames;
DROP TABLE IF EXISTS document_receivers;

CREATE TABLE user (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	username TEXT UNIQUE NOT NULL,
	password TEXT NOT NULL,
	role TEXT NOT NULL CHECK (role IN ('boss', 'secretary', 'customer'))
);

CREATE TABLE document (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	description TEXT NOT NULL,
	status TEXT NOT NULL CHECK (status IN ('issued', 'received', 'archived')),
	created_by INTEGER NOT NULL,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (created_by) REFERENCES user (id)
);

CREATE TABLE observation (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	document_id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	content TEXT NOT NULL,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (document_id) REFERENCES document (id),
	FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE document_filenames (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	document_id INTEGER NOT NULL,
	filename TEXT NOT NULL,
	FOREIGN KEY (document_id) REFERENCES document (id)
);

CREATE TABLE document_receivers (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	document_id INTEGER NOT NULL,
	receiver_id INTEGER NOT NULL,
	FOREIGN KEY (document_id) REFERENCES document (id)
	FOREIGN KEY (receiver_id) REFERENCES user (id)
);
