DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS document;
DROP TABLE IF EXISTS department;
DROP TABLE IF EXISTS observation;
DROP TABLE IF EXISTS document_filename;
DROP TABLE IF EXISTS document_receiver;

-- Department Table --
CREATE TABLE department (
	id TEXT PRIMARY KEY,
	name TEXT NOT NULL,
	description TEXT NOT NULL
);

-- User Table --
CREATE TABLE user (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	username TEXT NOT NULL UNIQUE,
	email TEXT NOT NULL UNIQUE,
	password TEXT NOT NULL,
	role TEXT NOT NULL DEFAULT 'user',
	department_id TEXT NOT NULL,

	FOREIGN KEY (department_id) REFERENCES department (id),

	CHECK (
		role IN ('admin', 'manager', 'secretary', 'user', 'guest')
	),
	CHECK (
		email LIKE '%_@_%._%' AND
		LENGTH(email) - LENGTH(REPLACE(email, '@', '')) = 1 AND
		SUBSTR(LOWER(email), 1, INSTR(email, '.') - 1) NOT GLOB '*[^@_0-9a-z]*' AND
		SUBSTR(LOWER(email), INSTR(email, '.') + 1) NOT GLOB '*[^a-z]*'
	)
);

-- Comment Table --
CREATE TABLE document (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	description TEXT NOT NULL,
	status TEXT NOT NULL CHECK (status IN ('issued', 'received', 'archived')),
	sender_id INTEGER NOT NULL,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

	FOREIGN KEY (sender_id) REFERENCES user (id)
);

-- Observation Table --
CREATE TABLE observation (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	document_id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	content TEXT NOT NULL,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

	FOREIGN KEY (document_id) REFERENCES document (id),
	FOREIGN KEY (user_id) REFERENCES user (id)
);

-- Document Filename Table --
CREATE TABLE document_filename (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	document_id INTEGER NOT NULL,
	filename TEXT NOT NULL,

	FOREIGN KEY (document_id) REFERENCES document (id)
);

-- Document Receiver Table --
CREATE TABLE document_receiver (
	document_id INTEGER NOT NULL,
	receiver_id INTEGER NOT NULL,
	received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	status TEXT NOT NULL CHECK (status IN ('issued', 'received', 'archived')),

	PRIMARY KEY (document_id, receiver_id),
	FOREIGN KEY (document_id) REFERENCES document (id),
	FOREIGN KEY (receiver_id) REFERENCES user (id)
);
