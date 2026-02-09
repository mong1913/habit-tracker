import sqlite3
from contextlib import contextmanager


@contextmanager
def get_cursor(db="habit_tracker.db"):
    con = sqlite3.connect(db)
    cur = con.cursor()
    try:
        yield cur
    except Exception as err:
        con.rollback()
        raise err
    finally:
        cur.close()
        con.close()


def create_tables():
    """
    Creates a habit(myhabit) table and a tracker table.
    """
    with get_cursor() as cur:
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS myhabit (
                    habit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    habit_name TEXT UNIQUE,
                    description TEXT,
                    frequency TEXT,
                    start_date TEXT,
                    current_streak INTEGER,
                    max_streak INTEGER)
                    """)

        cur.execute("""
                    CREATE TABLE IF NOT EXISTS tracker (
                    checkin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    habit_id INTEGER,
                    date TEXT, 
                    status TEXT,
                    FOREIGN KEY(habit_id) REFERENCES myhabit(habit_id) ON DELETE CASCADE)
                    """)


def get_data_from_myhabit_by_name(db, column, habit_name):
    with get_cursor(db) as cur:
        cur.execute(
            f"""SELECT {column} FROM myhabit WHERE habit_name = ?""", (habit_name,)
        )
        result = cur.fetchone()
        return result if result else None


def get_data_from_myhabit_by_period(db, column, period):
    with get_cursor(db) as cur:
        cur.execute(
            f"""SELECT {column} FROM myhabit WHERE frequency LIKE ?""", ("%" + period,)
        )
        results = cur.fetchall()
        return [row[0] for row in results] if results else []


def get_habit_id(db, habit_name):
    result = get_data_from_myhabit_by_name(db, "habit_id", habit_name)
    return result[0] if result else None


def get_data_from_tracker(db, column, habit_name):
    with get_cursor(db) as cur:
        habit_id = get_habit_id(db, habit_name)
        cur.execute(
            f""" SELECT {column} FROM tracker
                        WHERE habit_id = ? ORDER BY date DESC""",
            (habit_id,),
        )
        results = cur.fetchall()
        return [row for row in results] if results else []


def get_distinct_value(db, column, table):
    with get_cursor(db) as cur:
        cur.execute(f"""SELECT DISTINCT {column} FROM {table}""")
        results = cur.fetchall()
        return [row[0] for row in results] if results else []


def insert_myhabit(
    db, habit_name, description, frequency, start_date, current_streak, max_streak
):
    with get_cursor(db) as cur:
        cur.execute(
            """
                    INSERT INTO myhabit (habit_name, description, frequency, 
                                            start_date, current_streak, max_streak)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
            (
                habit_name.title(),
                description,
                frequency,
                start_date,
                current_streak,
                max_streak,
            ),
        )
        cur.connection.commit()


def insert_tracker(db, habit_name, date, status):
    with get_cursor(db) as cur:
        habit_id = get_habit_id(db, habit_name)
        cur.execute(
            """
                    INSERT INTO tracker (habit_id, date, status)
                    VALUES (?, ?, ?)
                    """,
            (habit_id, date, status),
        )
        cur.connection.commit()


def delete_value(db, habit_name, table):
    with get_cursor(db) as cur:
        cur.execute("PRAGMA foreign_keys = ON")
        habit_id = get_habit_id(db, habit_name)

        cur.execute(
            f"""
                    DELETE FROM {table} WHERE habit_id = ?
                    """,
            (habit_id,),
        )
        cur.connection.commit()


def update_myhabit(db, habit_name, column, value):
    with get_cursor(db) as cur:
        cur.execute(
            f""" 
                UPDATE myhabit SET {column} = ? WHERE habit_name = ?
                """,
            (value, habit_name),
        )
        cur.connection.commit()


def daily_and_monthly_habit_log(db, time):
    """
    Returns habit log on the specific date or in the specific month.

    Args:
        time: date of interest in "YYYY-MM-DD" format.
    Returns:
        list: a list of tuple(date, habit name, status). Tuples are records from the tracker table on the specific date or in the specific month.
    """
    with get_cursor(db) as cur:
        cur.execute(
            """ 
                    SELECT t.date, m.habit_name, t.status
                    FROM myhabit m
                    JOIN tracker t ON m.habit_id = t.habit_id
                    WHERE t.date LIKE ?
                    ORDER BY t.date DESC
                    """,
            (time + "%",),
        )
        rows = cur.fetchall()
        results = [row for row in rows] if rows else []
        columns = [descrip[0] for descrip in cur.description]
        return results, columns


def weekly_habit_log(db, time):
    """
    Returns habit log in the specific week.

    Args:
        time: date of interest in "YYYY-MM-DD" format. The week of the date will be used to filter records.
    Returns:
        list: a list of tuple(date, year week, habit name, status). Tuples are records from the tracker table in the specific week.
    """
    week = time.strftime("%Y-W%W")
    with get_cursor(db) as cur:
        cur.execute(
            """ 
                    SELECT t.date, STRFTIME('%Y-W%W', t.date) AS year_week, m.habit_name, t.status
                    FROM myhabit m
                    JOIN tracker t ON m.habit_id = t.habit_id
                    WHERE year_week = ?
                    ORDER BY t.date DESC
                    """,
            (week,),
        )
        rows = cur.fetchall()
        results = [row for row in rows] if rows else []
        columns = [descrip[0] for descrip in cur.description]
        return results, columns
