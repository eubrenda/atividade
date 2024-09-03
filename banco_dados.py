import sqlite3

def init_db():
    with sqlite3.connect('library.db') as conn:
        cursor = conn.cursor()
        cursor.executescript('''
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
        conn.commit()

if __name__ == '__main__':
    init_db()
