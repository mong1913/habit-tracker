import sqlite3, pytest
from contextlib import contextmanager
import db
from datetime import datetime

def test_get_cursor(tmp_path):

    fake_db_path = tmp_path / "test.db"

    with db.get_cursor(fake_db_path) as cur:
        cur.execute('''CREATE TABLE test_table (id INTEGER, habit TEXT)''')
        cur.execute('''INSERT INTO test_table VALUES (1, "Reading")''')
        cur.connection.commit()

    with db.get_cursor(fake_db_path) as cur:
        cur.execute('''SELECT habit FROM test_table WHERE id=1''')
        result = cur.fetchone()
    
    assert result[0] == "Reading"

@pytest.fixture
def mock_cursor(tmp_path, monkeypatch):

    fake_db_path = tmp_path / "test.db"

    @contextmanager
    def fake_get_cursor(db=None):
        fake_con = sqlite3.connect(fake_db_path)
        fake_cur = fake_con.cursor()
        try:
            yield fake_cur
        except Exception as err:
            fake_con.rollback()
            raise err
        finally:
            fake_cur.close()
            fake_con.close()
    
    monkeypatch.setattr(db, "get_cursor", fake_get_cursor)
    return fake_get_cursor

def test_create_tables(mock_cursor):
    
    db.create_tables()

    with mock_cursor() as cur:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='myhabit'")
        result1 = cur.fetchone()

        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tracker'")
        result2 = cur.fetchone()

    assert result1[0] == "myhabit"
    assert result2[0] == "tracker"

@pytest.fixture
def init_fake_table(mock_cursor):
    db.create_tables()
    with mock_cursor() as cur:
        cur.execute('''INSERT INTO myhabit (habit_name, description, frequency, 
                                        start_date, current_streak, max_streak)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', ("Swimming", "Swim for 1 hour", "3 time(s) per week", "2025-01-01", 1, 2))
        cur.connection.commit()
        cur.execute('''PRAGMA database_list''')
        db_path = cur.fetchone()[2]
    return db_path

def test_get_data_from_myhabit_by_name(init_fake_table):

    result = db.get_data_from_myhabit_by_name(init_fake_table, "habit_id", "Swimming")
    result_none = db.get_data_from_myhabit_by_name(init_fake_table, "habit_id", "Reading")
    assert result[0] == 1
    assert result_none == None

def test_get_data_from_myhabit_by_period(init_fake_table):

    result = db.get_data_from_myhabit_by_period(init_fake_table, "current_streak", "week")[0]
    assert result == 1

def test_get_habit_id(init_fake_table, monkeypatch):

    def fake_func(db, column, habit_name):
        assert db == init_fake_table
        assert column == "habit_id"
        assert habit_name == "Swimming"
        return (3, )
    
    monkeypatch.setattr(db, "get_data_from_myhabit_by_name", fake_func)
    
    result = db.get_habit_id(init_fake_table, "Swimming")
    assert result == 3

def test_get_habit_id_none(init_fake_table, monkeypatch):
    
    monkeypatch.setattr(db, "get_data_from_myhabit_by_name", 
                        lambda arg1, arg2, arg3: [])
    
    result = db.get_habit_id(init_fake_table, "Swimming")
    assert result == None

def test_get_data_from_tracker(mock_cursor, init_fake_table, monkeypatch):
    with mock_cursor() as cur:
        cur.execute('''
                    INSERT INTO tracker (habit_id, date, status)
                    VALUES (?, ?, ?)
                    ''', (1, "2025-01-01", "Done!"))   
        cur.connection.commit()

    def fake_func_get_habit_id(db, habit_name):
        assert db == init_fake_table
        assert habit_name == "Swimming"
        return 1
    
    monkeypatch.setattr(db, "get_habit_id", fake_func_get_habit_id)

    result = db.get_data_from_tracker(init_fake_table, "status", "Swimming")
    assert result[0][0] == "Done!"

def test_get_distinct_value(mock_cursor, init_fake_table):
    with mock_cursor() as cur:
        cur.execute('''INSERT INTO myhabit (habit_name, description, frequency, 
                                        start_date, current_streak, max_streak)
                    VALUES ("Reading", "Read books", "2 time(s) per day", "2025-01-05", 2, 2),
                           ("Jogging", "Jog for 1 hour", "1 time(s) per week", "2025-02-01", 2, 3)''')
        cur.connection.commit()

    result = db.get_distinct_value(init_fake_table, "habit_name", "myhabit")

    assert result == ["Jogging", "Reading", "Swimming"]

def test_insert_myhabit(mock_cursor, init_fake_table):
    db.insert_myhabit(init_fake_table, "dancing", "Dance for 1 hour", "1 time(s) per month", "2025-05-01", 1, 2)

    with mock_cursor() as cur:
        cur.execute('''SELECT DISTINCT habit_name FROM myhabit''')
        result = cur.fetchall()

    assert result[0] == ("Dancing", ), ("Swimming", )

def test_insert_tracker(mock_cursor, init_fake_table, monkeypatch):

    def fake_func_get_habit_id(db, habit_name):
        return 1
    
    monkeypatch.setattr(db, "get_habit_id", fake_func_get_habit_id)

    db.insert_tracker(init_fake_table, 1, "2025-04-03", "Skip.")

    with mock_cursor() as cur:
        cur.execute('''SELECT * FROM tracker where habit_id=1''')
        result = cur.fetchone()
    assert result[3] == "Skip."

def test_delete_value(mock_cursor, init_fake_table, monkeypatch):

    def fake_func_get_habit_id(db, habit_name):
        assert db == init_fake_table
        assert habit_name == "Swimming"
        return 1
    
    monkeypatch.setattr(db, "get_habit_id", fake_func_get_habit_id)

    db.delete_value(init_fake_table, "Swimming", "myhabit")
    with mock_cursor() as cur:
        cur.execute('''SELECT DISTINCT habit_name FROM myhabit''')
        result = cur.fetchall()

    assert result == []

def test_update_myhabit(mock_cursor, init_fake_table):
    with mock_cursor() as cur:
        cur.execute('''SELECT current_streak FROM myhabit WHERE habit_name="Swimming"''')
        result_before = cur.fetchone()

    db.update_myhabit(init_fake_table, "Swimming", "current_streak", 3)

    with mock_cursor() as cur:
        cur.execute('''SELECT current_streak FROM myhabit WHERE habit_name="Swimming"''')
        result_after = cur.fetchone()

    assert result_before[0] == 1
    assert result_after[0] == 3

def test_daily_and_monthly_habit_log(mock_cursor, init_fake_table):

    with mock_cursor() as cur:
        cur.execute('''
                    INSERT INTO myhabit (habit_name, description, frequency, 
                                        start_date, current_streak, max_streak)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', ("Reading", "Read books", "2 time(s) per month", "2025-01-01", 1, 1))
        
        cur.execute('''
                    INSERT INTO tracker (habit_id, date, status)
                    VALUES (?, ?, ?)
                    ''', (2, "2025-01-01", "Done!"))   
        
        cur.connection.commit()

    results, columns = db.daily_and_monthly_habit_log(init_fake_table, "2025-01-01")

    assert results[0] == ("2025-01-01", "Reading", "Done!")
    assert columns == ["date", "habit_name", "status"]

def test_daily_and_monthly_habit_log_none(init_fake_table):

    results, columns = db.daily_and_monthly_habit_log(init_fake_table, "2025-01-02")

    assert results == []
    assert columns == ["date", "habit_name", "status"]

def test_weekly_habit_log(mock_cursor, init_fake_table):

    with mock_cursor() as cur:
        cur.execute('''
                    INSERT INTO tracker (habit_id, date, status)
                    VALUES (?, ?, ?)
                    ''', (1, "2025-01-07", "Done!"))   
        cur.connection.commit()

    time = datetime(2025, 1, 10)
    results, columns = db.weekly_habit_log(init_fake_table, time)

    assert results[0] == ("2025-01-07", "2025-W01", "Swimming", "Done!")
    assert columns == ["date", "year_week", "habit_name", "status"]