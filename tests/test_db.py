import sqlite3, pytest
from contextlib import contextmanager
import db
from datetime import datetime

@pytest.fixture
def test_db_con(monkeypatch):
    con = sqlite3.connect(":memory:")
    
    @contextmanager
    def fake_con_db():
        yield con

    monkeypatch.setattr("db.con_db", fake_con_db)

    db.create_tables()

    return con

def test_create_tables(test_db_con):
    cur = test_db_con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='myhabit'")
    result1 = cur.fetchone()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tracker'")
    result2 = cur.fetchone()

    assert result1[0] == "myhabit"
    assert result2[0] == "tracker"

def test_get_data_from_myhabit_by_name(test_db_con):
    cur = test_db_con.cursor()
    cur.execute('''
                        INSERT INTO myhabit (habit_name, description, frequency, 
                                                start_date, current_streak, max_streak)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ''', ("Swimming", "Swim for 1 hour", "3 time(s) per week", "2025-01-01", 1, 2))
    
    test_db_con.commit()

    result = db.get_data_from_myhabit_by_name("current_streak", "Swimming")[0]

    assert result == 1

def test_get_data_from_myhabit_by_period(test_db_con):
    cur = test_db_con.cursor()
    cur.execute('''
                INSERT INTO myhabit (habit_name, description, frequency, 
                                    start_date, current_streak, max_streak)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', ("Swimming", "Swim for 1 hour", "3 time(s) per week", "2025-01-01", 1, 2))
    
    test_db_con.commit()

    result = db.get_data_from_myhabit_by_period("current_streak", "week")[0]

    assert result == 1

def test_get_habit_id(monkeypatch):
    def fake_func(arg1, arg2):
        assert arg1 == "habit_id"
        assert arg2 == "Swimming"
        return (3, )
    
    monkeypatch.setattr("db.get_data_from_myhabit_by_name", fake_func)
    
    result = db.get_habit_id("Swimming")
    assert result == 3

def test_get_habit_id_none(monkeypatch):
    
    monkeypatch.setattr("db.get_data_from_myhabit_by_name", 
                        lambda arg1, arg2: None)
    
    result = db.get_habit_id("Swimming")
    assert result == None

def test_get_data_from_tracker(test_db_con, monkeypatch):
    cur = test_db_con.cursor()
    
    def fake_func_get_habit_id(arg1):
        assert arg1 == "Swimming"
        return 1
    
    monkeypatch.setattr("db.get_habit_id", fake_func_get_habit_id)

    cur.execute('''
                INSERT INTO tracker (habit_id, date, status)
                VALUES (?, ?, ?)
                ''', (1, "2025-01-01", "Skip."))   
    test_db_con.commit()

    result = db.get_data_from_tracker("status", "Swimming")[0][0]
    assert result == "Skip."

def test_get_distinct_value(test_db_con):
    cur = test_db_con.cursor()
    cur.execute('''
                INSERT INTO myhabit (habit_name, description, frequency, 
                                    start_date, current_streak, max_streak)
                VALUES ("Swimming", "Swim for 1 hour", "3 time(s) per week", "2025-01-01", 1, 2),
                        ("Reading", "Read books", "2 time(s) per day", "2025-01-05", 2, 2),
                        ("Jogging", "Jog for 1 hour", "1 time(s) per week", "2025-02-01", 2, 3)
                ''')
    
    test_db_con.commit()

    result = db.get_distinct_value("max_streak", "myhabit")

    assert result == [2, 3]

def test_insert_myhabit(test_db_con):
    db.insert_myhabit("Swimming", "Swim for 1 hour", "3 time(s) per week", "2025-01-01", 1, 2)

    cur = test_db_con.cursor()
    cur.execute('''SELECT description FROM myhabit''')
    result = cur.fetchall()
    assert result[0][0] == "Swim for 1 hour"

def test_insert_tracker(test_db_con):
    db.insert_tracker(1, "2025-04-03", "Skip.")

    cur = test_db_con.cursor()
    cur.execute('''SELECT * FROM tracker''')
    result = cur.fetchall()
    assert result[0][3] == "Skip."

def test_delete_value(test_db_con, monkeypatch):
    cur = test_db_con.cursor()
    cur.execute('''
                INSERT INTO myhabit (habit_name, description, frequency, 
                                    start_date, current_streak, max_streak)
                VALUES ("Swimming", "Swim for 1 hour", "3 time(s) per week", "2025-01-01", 1, 2),
                        ("Reading", "Read books", "2 time(s) per day", "2025-01-05", 2, 2),
                        ("Jogging", "Jog for 1 hour", "1 time(s) per week", "2025-02-01", 2, 3)
                ''')
    test_db_con.commit()

    def fake_func_get_habit_id(arg1):
        assert arg1 == "Reading"
        return 2
    
    monkeypatch.setattr("db.get_habit_id", fake_func_get_habit_id)

    db.delete_value("Reading", "myhabit")
    cur.execute('''SELECT * FROM myhabit WHERE habit_name="Reading"''')
    result = cur.fetchall()

    assert result == []

def test_update_myhabit(test_db_con):
    cur = test_db_con.cursor()
    cur.execute('''
                INSERT INTO myhabit (habit_name, description, frequency, 
                                    start_date, current_streak, max_streak)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', ("Swimming", "Swim for 1 hour", "3 time(s) per week", "2025-01-01", 1, 2))
    
    test_db_con.commit()

    db.update_myhabit("Swimming", "current_streak", 2)
    cur.execute('''SELECT current_streak FROM myhabit WHERE habit_name="Swimming"''')
    result = cur.fetchone()
    assert result[0] == 2

def test_daily_and_monthly_habit_log(test_db_con):

    cur = test_db_con.cursor()
    cur.execute('''
                INSERT INTO myhabit (habit_name, description, frequency, 
                                    start_date, current_streak, max_streak)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', ("Swimming", "Swim for 1 hour", "1 time(s) per day", "2025-01-01", 1, 1))
    
    cur.execute('''
                INSERT INTO tracker (habit_id, date, status)
                VALUES (?, ?, ?)
                ''', (1, "2025-01-01", "Done!"))   
    
    test_db_con.commit()

    results, columns = db.daily_and_monthly_habit_log("2025-01-01")

    assert results[0] == ("2025-01-01", "Swimming", "Done!")
    assert columns == ["date", "habit_name", "status"]

def test_weekly_habit_log(test_db_con):

    cur = test_db_con.cursor()
    cur.execute('''
                INSERT INTO myhabit (habit_name, description, frequency, 
                                    start_date, current_streak, max_streak)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', ("Swimming", "Swim for 1 hour", "3 time(s) per week", "2025-01-07", 0, 0))
    
    cur.execute('''
                INSERT INTO tracker (habit_id, date, status)
                VALUES (?, ?, ?)
                ''', (1, "2025-01-07", "Done!"))   
    
    test_db_con.commit()

    time = datetime(2025, 1, 7)
    results, columns = db.weekly_habit_log(time)

    assert results[0] == ("2025-01-07", "2025-W01", "Swimming", "Done!")
    assert columns == ["date", "year_week", "habit_name", "status"]        

def test_count_done_skip(test_db_con, monkeypatch):
    cur = test_db_con.cursor()

    cur.execute('''
                INSERT INTO myhabit (habit_name, description, frequency, 
                                    start_date, current_streak, max_streak)
                VALUES ("Swimming", "Swim for 1 hour", "2 time(s) per day", "2025-01-07", 0, 1)
                ''')

    cur.execute('''
                INSERT INTO tracker (habit_id, date, status)
                VALUES (1, "2025-01-07", "Done!"),
                        (1, "2025-01-07", "Skip."),
                        (1, "2025-01-08", "Done!"),
                        (1, "2025-01-09", "Done!"),
                        (1, "2025-01-09", "Missed.")
                ''')   
    
    test_db_con.commit()

    def fake_func_get_habit_id(arg1):
        assert arg1 == "Swimming"
        return 1
    
    monkeypatch.setattr("db.get_habit_id", fake_func_get_habit_id)

    result = db.count_done_skip("Swimming", "date_only")

    assert result == [("2025-01-07", "2025-W01", "2025-01", 2),
                      ("2025-01-08", "2025-W01", "2025-01", 1),
                      ("2025-01-09", "2025-W01", "2025-01", 1)]