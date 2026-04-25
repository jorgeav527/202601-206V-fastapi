import sqlite3


def init_db():
    connection = sqlite3.connect("basedatos.db")
    with open("schema.sql") as f:
        connection.executescript(f.read())

    cur = connection.cursor()
    cur.execute(
        "INSERT INTO posts (title, content) VALUES (?, ?)",
        ("First Post", "Content for the first post"),
    )
    connection.commit()
    connection.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized.")