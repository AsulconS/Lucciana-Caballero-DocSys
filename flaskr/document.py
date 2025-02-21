import os
import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, g, current_app, send_from_directory
from flaskr.db import get_db
from flaskr.auth import login_required
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash


ALLOWED_EXTENSIONS = {'pdf'}


bp = Blueprint('document', __name__)


def allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/')
@login_required
def index():
	"""Show documents relevant to the user."""
	db = get_db()
	docs = db.execute(
		'SELECT DISTINCT d.*, u_sender.username AS sender, dr.status AS drstatus '
		'FROM document d '
		'LEFT JOIN user u_sender ON d.sender_id = u_sender.id '
		'LEFT JOIN document_receiver dr ON d.id = dr.document_id '
		'LEFT JOIN user u_receiver ON dr.receiver_id = u_receiver.id '
		'WHERE dr.receiver_id = ? AND dr.status != "archived";',
		(g.user['id'],)
	).fetchall()
	return render_template('index.html', docs=docs, timestamp=datetime.datetime.utcnow().replace(microsecond=0))


@bp.route('/create_user', methods=('GET', 'POST'))
@login_required
def create_user():
	"""Create a new user."""
	if g.user['role'] != 'admin':
		flash('Only admins can create.', category='error')
		return redirect(url_for('document.index'))

	db = get_db()
	departments = db.execute('SELECT id, name FROM department').fetchall()

	if request.method == 'POST':
		username = request.form['username']
		email = request.form['email']
		password = request.form['password']
		role = request.form['role']
		department_id = request.form['department_id']
		error = None

		if not username:
			error = 'Username is required.'
		elif not password:
			error = 'Password is required.'
		elif not role:
			error = 'Role is required.'

		if error is not None:
			flash(error, category='error')
		else:
			db.execute(
				'INSERT INTO user (username, email, password, role, department_id) VALUES (?, ?, ?, ?, ?)',
				(username, email, generate_password_hash(password), role, department_id)
			)
			db.commit()
			flash('User created successfully!', category='success')
			return redirect(url_for('document.index'))

	return render_template('create_user.html', departments=departments)


@bp.route('/create_document/<ref_id>', methods=('GET', 'POST'))
@login_required
def create_document(ref_id):
	"""Create a new document."""
	if g.user['role'] == 'guest':
		flash('Guests cannot create documents.', category='error')
		return redirect(url_for('document.index'))

	try:
		ref_id = int(ref_id)
	except ValueError:
		ref_id = -1

	db = get_db()
	users = db.execute('SELECT id, username FROM user').fetchall()
	documents = db.execute('SELECT id, name FROM document').fetchall()
	departments = db.execute('SELECT id, name FROM department').fetchall()

	if request.method == 'POST':
		file = request.files['file']
		name = request.form['name']
		dpt_receivers = request.form['dpt_receivers'] if (ref_id < 0) else None
		description = request.form['description']
		error = None

		if not name:
			error = 'Name is required.'
		elif not description:
			error = 'Description is required.'
		elif not file:
			error = 'File part is required.'
		elif file.filename == '':
			error = 'File is required.'
		elif not allowed_file(file.filename):
			error = 'File type not supported.'
		elif not dpt_receivers and (ref_id < 0):
			error = 'Bad request'

		if error is not None:
			flash(error, category='error')
		else:
			# Insert the document
			cur = db.execute(
				'INSERT INTO document (name, description, status, sender_id) VALUES (?, ?, ?, ?)',
				(name, description, 'issued', g.user['id'])
			)
			db.commit()
			doc_id = cur.lastrowid

			# Insert the file
			filename = secure_filename(file.filename)
			doc_files_folder_path = os.path.join(current_app.config['UPLOAD_FOLDER_PATH'], str(doc_id))
			os.makedirs(doc_files_folder_path)
			file.save(os.path.join(doc_files_folder_path, filename))
			db.execute(
				'INSERT INTO document_filename (document_id, filename) VALUES (?, ?)',
				(doc_id, filename)
			)
			db.commit()

			if ref_id < 0:
				# Insert receivers
				dpt_receivers = dpt_receivers.split(',')
				if 'all' in dpt_receivers:
					# Add all users except the admin as receivers
					for user in users:
						db.execute(
							'INSERT INTO document_receiver (document_id, receiver_id, status) VALUES (?, ?, ?)',
							(doc_id, user['id'], 'issued')
						)
						db.execute(
							'INSERT INTO followup_response (document_id, receiver_id, response_document_id) VALUES (?, ?, ?)',
							(doc_id, user['id'], doc_id)
						)
				else:
					# Add selected users as receivers
					for dpt_id in dpt_receivers:
						user_receivers = db.execute('SELECT id FROM user WHERE user.department_id = ?', (dpt_id,))
						for user in user_receivers:
							db.execute(
								'INSERT INTO document_receiver (document_id, receiver_id, status) VALUES (?, ?, ?)',
								(doc_id, user['id'], 'issued')
							)
							db.execute(
								'INSERT INTO followup_response (document_id, receiver_id, response_document_id) VALUES (?, ?, ?)',
								(doc_id, user['id'], doc_id)
							)
			else:
				db.execute(
					'INSERT INTO followup_response (document_id, receiver_id, response_document_id) VALUES (?, ?, ?)',
					(ref_id, g.user['id'], doc_id)
				)
			db.commit()

			flash('Document created successfully!', category='success')
			return redirect(url_for('document.index'))

	if ref_id < 0:
		return render_template('create_document.html', departments=departments, documents=documents)
	return render_template('create_document.html', departments=departments, documents=documents, ref_id=int(ref_id))


@bp.route('/status/<status>', methods=('GET',))
@login_required
def status(status):
	"""View documents with certain status."""
	db = get_db()
	docs = db.execute(
		'SELECT DISTINCT d.*, u_sender.username AS sender, u_receiver.username AS receiver '
		'FROM document d '
		'LEFT JOIN user u_sender ON d.sender_id = u_sender.id '
		'LEFT JOIN document_receiver dr ON d.id = dr.document_id '
		'LEFT JOIN user u_receiver ON dr.receiver_id = u_receiver.id '
		'WHERE dr.receiver_id = ? AND dr.status = ?;',
		(g.user['id'], status)
	).fetchall()
	return render_template('index.html', docs=docs, status=status, timestamp=datetime.datetime.utcnow().replace(microsecond=0))


@bp.route('/<int:id>/follow_up', methods=('GET',))
@login_required
def follow_up(id):
	"""View follow-up details for a specific document."""
	db = get_db()
	receivers = db.execute(
		'SELECT u.username as receiver_username, dr.received_at AS received_at, dr.status AS status '
		'FROM document_receiver dr '
		'JOIN user u ON dr.receiver_id = u.id '
		'WHERE dr.document_id = ?;',
		(id,)
	).fetchall()
	document = db.execute(
		'SELECT DISTINCT d.*, u.username AS sender '
		'FROM document d '
		'JOIN user u ON d.sender_id = u.id '
		'WHERE d.id = ?;',
		(id,)
	).fetchone()

	if document is None:
		abort(404, f"Document with ID {id} doesn't exist.")

	timestamp = datetime.datetime.utcnow().replace(microsecond=0)
	return render_template('follow_up.html', document=document, receivers=receivers, timestamp=timestamp)


@bp.route('/<int:id>/observations', methods=('GET', 'POST'))
@login_required
def observations(id):
	"""View and add observations for a document."""
	db = get_db()

	if request.method == 'POST':
		observation = request.form['observation']
		if not observation:
			flash("Observation cannot be empty.", "error")
		else:
			db.execute(
				'INSERT INTO observation (document_id, user_id, content) VALUES (?, ?, ?)',
				(id, g.user['id'], observation)
			)
			db.commit()
			flash("Observation added successfully.", "success")

	# Fetch document and its observations
	document = db.execute('SELECT * FROM document WHERE id = ?', (id,)).fetchone()
	observations = db.execute(
		'SELECT o.content, u.username, o.created_at '
		'FROM observation o JOIN user u ON o.user_id = u.id '
		'WHERE o.document_id = ? ORDER BY o.created_at DESC',
		(id,)
	).fetchall()

	if document is None:
		abort(404, f"Document with ID {id} doesn't exist.")

	return render_template('observations.html', document=document, observations=observations)


@bp.route('/update_status/<int:id>', methods=('POST',))
@login_required
def update_status(id):
	"""Update the status of a document."""
	new_status = request.form.get('status')
	db = get_db()

	# Check if the document exists
	document = db.execute(
		'SELECT id, sender_id FROM document WHERE id = ?', (id,)
	).fetchone()

	if document is None:
		flash('Document not found.', category='error')
		return redirect(url_for('document.index'))

	# Ensure only admin and secretary can update the status
	if g.user['role'] not in ['admin', 'secretary']:
		flash('You are not authorized to update the document status.', category='error')
		return redirect(url_for('document.index'))

	# Update the status
	db.execute(
		'UPDATE document SET status = ? WHERE id = ?',
		(new_status, id)
	)
	db.commit()
	flash('Document status updated successfully!', category='success')
	return redirect(url_for('document.index'))


@bp.route('/mark_received/<int:id>', methods=('GET', 'POST'))
@login_required
def mark_received(id):
	db = get_db()

	# Check if the document exists and if the status is 'issued' or 'archived'
	document = db.execute(
		'SELECT * FROM document WHERE id = ?;',
		(id,)
	).fetchone()

	if not document:
		flash('Document not found or already received.', category='error')
		return redirect(url_for('document.index'))

	# Update the status to 'received'
	db.execute(
		'UPDATE document_receiver SET status = "received" WHERE document_id = ? AND receiver_id = ?',
		(id, g.user['id'])
	)
	db.commit()

	flash('Document marked as received.', category='success')
	return redirect(url_for('document.index'))


@bp.route('/mark_archived/<int:id>', methods=('GET', 'POST'))
@login_required
def mark_archived(id):
	db = get_db()

	# Check if the document exists and if the status is 'received'
	document = db.execute(
		'SELECT * FROM document WHERE id = ?;',
		(id,)
	).fetchone()

	if not document:
		flash('Document not found or already archived.', category='error')
		return redirect(url_for('document.index'))

	# Update the status to 'archived'
	db.execute(
		'UPDATE document_receiver SET status = "archived" WHERE document_id = ? AND receiver_id = ?',
		(id, g.user['id'])
	)
	db.commit()

	flash('Document marked as archived.', category='success')
	return redirect(url_for('document.index'))


@bp.route('/delete/<int:id>', methods=('POST',))
@login_required
def delete(id):
	"""Delete a document. Only accessible to admins."""
	if g.user['role'] != 'admin':
		flash('You are not authorized to delete documents.', category='error')
		return redirect(url_for('document.index'))

	db = get_db()
	document = db.execute(
		'SELECT id FROM document WHERE id = ?', (id,)
	).fetchone()
	document_filename = db.execute(
		'SELECT filename FROM document_filename WHERE document_id = ?',
		(id,),
	).fetchone()

	if document is None:
		flash('Document not found.', category='error')
		return redirect(url_for('document.index'))

	doc_files_folder_path = os.path.join(current_app.config['UPLOAD_FOLDER_PATH'], str(id))
	filepath = os.path.join(doc_files_folder_path, document_filename['filename'])
	if os.path.isfile(filepath):
		os.remove(filepath)
		os.rmdir(doc_files_folder_path)

	db.execute('DELETE FROM document WHERE id = ?', (id,))
	db.execute('DELETE FROM document_filename WHERE document_id = ?', (id,))
	db.commit()
	flash('Document deleted successfully!', category='success')
	return redirect(url_for('document.index'))


@bp.route('/download_file/<int:id>')
@login_required
def download_file(id):
	db = get_db()
	document_filename = db.execute(
		'SELECT filename FROM document_filename WHERE document_id = ?',
		(id,),
	).fetchone()
	doc_files_folder_path = os.path.join(current_app.config['UPLOAD_FOLDER_PATH'], str(id))
	return send_from_directory(doc_files_folder_path, document_filename['filename'], as_attachment=True)


@bp.route('/search_document', methods=('GET', 'POST'))
@login_required
def search_document():
	docname = request.form['docname']
	db = get_db()
	docs = db.execute(
		'SELECT DISTINCT d.*, u_sender.username AS sender, dr.status AS drstatus '
		'FROM document d '
		'LEFT JOIN user u_sender ON d.sender_id = u_sender.id '
		'LEFT JOIN document_receiver dr ON d.id = dr.document_id '
		'LEFT JOIN user u_receiver ON dr.receiver_id = u_receiver.id '
		'WHERE dr.receiver_id = ? AND dr.status != "archived" AND d.name = ?;',
		(g.user['id'], docname)
	).fetchall()
	return render_template('index.html', docs=docs)
