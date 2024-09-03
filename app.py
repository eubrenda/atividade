from flask import Flask, request, redirect, url_for, render_template
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['DATABASE'] = 'library.db'

def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        db.executescript('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS authors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS genres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS book_author (
                book_id INTEGER,
                author_id INTEGER,
                PRIMARY KEY (book_id, author_id),
                FOREIGN KEY (book_id) REFERENCES books (id),
                FOREIGN KEY (author_id) REFERENCES authors (id)
            );

            CREATE TABLE IF NOT EXISTS book_genre (
                book_id INTEGER,
                genre_id INTEGER,
                PRIMARY KEY (book_id, genre_id),
                FOREIGN KEY (book_id) REFERENCES books (id),
                FOREIGN KEY (genre_id) REFERENCES genres (id)
            );
        ''')

@app.route('/')
def index():
    return redirect(url_for('book_list'))

# Book Routes
@app.route('/books')
def book_list():
    db = get_db()
    books = db.execute('SELECT * FROM books').fetchall()
    return render_template('book_list.html', books=books)

@app.route('/books/new', methods=['GET', 'POST'])
def new_book():
    db = get_db()
    if request.method == 'POST':
        title = request.form['title']
        author_ids = request.form.getlist('authors')
        genre_ids = request.form.getlist('genres')

        db.execute('INSERT INTO books (title) VALUES (?)', (title,))
        book_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]

        for author_id in author_ids:
            db.execute('INSERT INTO book_author (book_id, author_id) VALUES (?, ?)', (book_id, author_id))
        for genre_id in genre_ids:
            db.execute('INSERT INTO book_genre (book_id, genre_id) VALUES (?, ?)', (book_id, genre_id))
        
        db.commit()
        return redirect(url_for('book_list'))
    
    authors = db.execute('SELECT * FROM authors').fetchall()
    genres = db.execute('SELECT * FROM genres').fetchall()
    return render_template('book_form.html', action=url_for('new_book'), authors=authors, genres=genres)

@app.route('/books/<int:book_id>/edit', methods=['GET', 'POST'])
def edit_book(book_id):
    db = get_db()
    if request.method == 'POST':
        title = request.form['title']
        author_ids = request.form.getlist('authors')
        genre_ids = request.form.getlist('genres')

        db.execute('UPDATE books SET title = ? WHERE id = ?', (title, book_id))
        db.execute('DELETE FROM book_author WHERE book_id = ?', (book_id,))
        db.execute('DELETE FROM book_genre WHERE book_id = ?', (book_id,))

        for author_id in author_ids:
            db.execute('INSERT INTO book_author (book_id, author_id) VALUES (?, ?)', (book_id, author_id))
        for genre_id in genre_ids:
            db.execute('INSERT INTO book_genre (book_id, genre_id) VALUES (?, ?)', (book_id, genre_id))
        
        db.commit()
        return redirect(url_for('book_list'))

    book = db.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    authors = db.execute('SELECT * FROM authors').fetchall()
    genres = db.execute('SELECT * FROM genres').fetchall()
    book_authors = [row['author_id'] for row in db.execute('SELECT author_id FROM book_author WHERE book_id = ?', (book_id,)).fetchall()]
    book_genres = [row['genre_id'] for row in db.execute('SELECT genre_id FROM book_genre WHERE book_id = ?', (book_id,)).fetchall()]
    return render_template('book_form.html', book=book, action=url_for('edit_book', book_id=book_id), authors=authors, genres=genres, book_authors=book_authors, book_genres=book_genres)

@app.route('/books/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    db = get_db()
    db.execute('DELETE FROM books WHERE id = ?', (book_id,))
    db.execute('DELETE FROM book_author WHERE book_id = ?', (book_id,))
    db.execute('DELETE FROM book_genre WHERE book_id = ?', (book_id,))
    db.commit()
    return redirect(url_for('book_list'))

# Author Routes
@app.route('/authors')
def author_list():
    db = get_db()
    authors = db.execute('SELECT * FROM authors').fetchall()
    return render_template('author_list.html', authors=authors)

@app.route('/authors/new', methods=['GET', 'POST'])
def new_author():
    if request.method == 'POST':
        name = request.form['name']
        db = get_db()
        db.execute('INSERT INTO authors (name) VALUES (?)', (name,))
        db.commit()
        return redirect(url_for('author_list'))
    return render_template('author_form.html', action=url_for('new_author'))

@app.route('/authors/<int:author_id>/edit', methods=['GET', 'POST'])
def edit_author(author_id):
    db = get_db()
    if request.method == 'POST':
        name = request.form['name']
        db.execute('UPDATE authors SET name = ? WHERE id = ?', (name, author_id))
        db.commit()
        return redirect(url_for('author_list'))
    author = db.execute('SELECT * FROM authors WHERE id = ?', (author_id,)).fetchone()
    return render_template('author_form.html', author=author, action=url_for('edit_author', author_id=author_id))

@app.route('/authors/<int:author_id>/delete', methods=['POST'])
def delete_author(author_id):
    db = get_db()
    db.execute('DELETE FROM authors WHERE id = ?', (author_id,))
    db.execute('DELETE FROM book_author WHERE author_id = ?', (author_id,))
    db.commit()
    return redirect(url_for('author_list'))

# Genre Routes
@app.route('/genres')
def genre_list():
    db = get_db()
    genres = db.execute('SELECT * FROM genres').fetchall()
    return render_template('genre_list.html', genres=genres)

@app.route('/genres/new', methods=['GET', 'POST'])
def new_genre():
    if request.method == 'POST':
        name = request.form['name']
        db = get_db()
        db.execute('INSERT INTO genres (name) VALUES (?)', (name,))
        db.commit()
        return redirect(url_for('genre_list'))
    return render_template('genre_form.html', action=url_for('new_genre'))

@app.route('/genres/<int:genre_id>/edit', methods=['GET', 'POST'])
def edit_genre(genre_id):
    db = get_db()
    if request.method == 'POST':
        name = request.form['name']
        db.execute('UPDATE genres SET name = ? WHERE id = ?', (name, genre_id))
        db.commit()
        return redirect(url_for('genre_list'))
    genre = db.execute('SELECT * FROM genres WHERE id = ?', (genre_id,)).fetchone()
    return render_template('genre_form.html', genre=genre, action=url_for('edit_genre', genre_id=genre_id))

@app.route('/genres/<int:genre_id>/delete', methods=['POST'])
def delete_genre(genre_id):
    db = get_db()
    db.execute('DELETE FROM genres WHERE id = ?', (genre_id,))
    db.execute('DELETE FROM book_genre WHERE genre_id = ?', (genre_id,))
    db.commit()
    return redirect(url_for('genre_list'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
