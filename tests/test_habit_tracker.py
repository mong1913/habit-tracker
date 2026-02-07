from habit_tracker import Habit_Tracker
import habit_tracker
import sqlite3, pytest
from datetime import datetime, date

@pytest.fixture
def sut():
    db = "fake_db.db"
    return Habit_Tracker(db)

def test_add_habit(sut, monkeypatch):

    item_list = []
    def fake_func(db, habit_name, description, frequency, start_date, arg5, arg6):
        item_list.append((db, habit_name, description, frequency, start_date, 0, 0))

    monkeypatch.setattr(habit_tracker, "insert_myhabit", fake_func)

    sut.add_habit("habit_name", "description", "frequency", "start_date")
    assert item_list == [("fake_db.db", "habit_name", "description", "frequency", "start_date", 0, 0)]

def test_add_habit_error(sut, monkeypatch):
    def fake_func_error(db, habit_name, description, frequency, start_date, arg5, arg6):
        raise sqlite3.IntegrityError
    
    monkeypatch.setattr(habit_tracker, "insert_myhabit", fake_func_error)

    with pytest.raises(sqlite3.IntegrityError):
        sut.add_habit("habit_name", "description", "frequency", "start_date")
    
def test_delete_habit(sut, monkeypatch):
    item_list = []
    def fake_func(db, habit_name, table):
        item_list.append((db, habit_name, "myhabit"))

    monkeypatch.setattr(habit_tracker, "delete_value", fake_func)

    sut.delete_habit("habit_name")
    assert item_list == [("fake_db.db", "habit_name", "myhabit")]

def test_completion_count(sut, monkeypatch):

    def fake_get_data_from_tracker(db, columns, habit_name):
        assert columns == "date, status"
        return [("2025-01-10 12:11", "Done!"), ("2025-01-10 18:22", "Done!"), ("2025-01-11 17:09", "Skip.")]

    monkeypatch.setattr(habit_tracker, "get_data_from_tracker", fake_get_data_from_tracker)

    success_counts_list = sut.completion_count("Swimming", "day")
    assert success_counts_list == [("2025-01-10", 2), ("2025-01-11", 1)]

class Fakedate(date):
    @classmethod
    def today(cls):
        return cls(2025, 1, 7)

def test_fill_history(sut, monkeypatch):

    habit_log = [("2025-01-04", 2), ("2025-01-05", 1)]

    monkeypatch.setattr(habit_tracker, "date", Fakedate)
    log_list = sut.fill_history(habit_log, "day")

    assert log_list == [(date(2025, 1, 4), 2), (date(2025, 1, 5), 1), (date(2025, 1, 6), 0), (date(2025, 1, 7), 0)]

def test_fill_history_year_transition(sut, monkeypatch):

    habit_log = [("2024-12-30", 2), ("2025-01-05", 1)]

    monkeypatch.setattr(habit_tracker, "date", Fakedate)
    log_list = sut.fill_history(habit_log, "day")

    assert log_list == [(date(2024, 12, 30), 2), (date(2024, 12, 31), 0), (date(2025, 1, 1), 0), (date(2025, 1, 2), 0), (date(2025, 1, 3), 0), 
                        (date(2025, 1, 4), 0), (date(2025, 1, 5), 1), (date(2025, 1, 6), 0), (date(2025, 1, 7), 0)]

def test_streak_count_day(sut, monkeypatch):

    def fake_fill_history(db, habit_log, period):
        assert habit_log == [("2025-01-10", 2), ("2025-01-11", 2), ("2025-01-13", 3)]
        assert period == "day"
        return [(date(2025, 1, 10), 2), (date(2025, 1, 11), 2), (date(2025, 1, 12), 0), (date(2025, 1, 13), 3)]
    
    monkeypatch.setattr(Habit_Tracker, "fill_history", fake_fill_history)

    habit_log = [("2025-01-10", 2), ("2025-01-11", 2), ("2025-01-13", 3)]
    updated_streak, max_streak = sut.streak_count(habit_log, "day", 2)

    assert updated_streak == 1
    assert max_streak == 2

def test_streak_count_week(sut, monkeypatch):

    def fake_fill_history(db, habit_log, period):
        assert habit_log == [("2025-W01", 2), ("2025-W02", 3), ("2025-W04", 2)]
        assert period == "week"
        return [(datetime(2024, 12, 30), 2), (datetime(2025, 1, 6), 3), (datetime(2025, 1, 13), 0), (datetime(2025, 1, 20), 2)]
    
    monkeypatch.setattr(Habit_Tracker, "fill_history", fake_fill_history)    
    
    habit_log = [("2025-W01", 2), ("2025-W02", 3), ("2025-W04", 2)]
    updated_streak, max_streak = sut.streak_count(habit_log, "week", 2)

    assert updated_streak == 1
    assert max_streak == 2

def test_streak_count_month(sut, monkeypatch):

    def fake_fill_history(db, habit_log, period):
        assert habit_log == [("2025-01", 2), ("2025-02", 3), ("2025-04", 2)]
        assert period == "month"
        return [(datetime(2025, 1, 1, 0, 0), 2), (datetime(2025, 2, 1, 0, 0), 3), \
                (datetime(2025, 3, 1, 0, 0), 0), (datetime(2025, 4, 1, 0, 0), 2)]   
    
    monkeypatch.setattr(Habit_Tracker, "fill_history", fake_fill_history)    

    habit_log = [("2025-01", 2), ("2025-02", 3), ("2025-04", 2)]
    updated_streak, max_streak = sut.streak_count(habit_log, "month", 2)

    assert updated_streak == 1
    assert max_streak == 2

def test_update_streak(sut, monkeypatch):

    item_list = []

    def fake_get_data(db, frequency, habit_name):
        assert db == "fake_db.db"
        assert habit_name == "Swimming"
        return ["3 time(s) per day"]
    
    def fake_completion_count(db, habit_name, period):
        assert habit_name == "Swimming"
        assert period == "day"
        return None
    
    def fake_streak_count(self, habit_log, period, times):
        assert period == "day"
        assert times == 3
        return (2, 3)
    
    def fake_update_myhabit(db, habit_name, column, value):
        assert db == "fake_db.db"
        assert habit_name == "Swimming"        
        item_list.append((habit_name, column, value))
    
    monkeypatch.setattr(habit_tracker, "get_data_from_myhabit_by_name", fake_get_data) 
    monkeypatch.setattr(Habit_Tracker, "completion_count", fake_completion_count)   
    monkeypatch.setattr(Habit_Tracker, "streak_count", fake_streak_count)    
    monkeypatch.setattr(habit_tracker, "update_myhabit", fake_update_myhabit)    

    sut.update_streak("Swimming")
    assert item_list == [("Swimming", "current_streak", 2), 
                         ("Swimming", "max_streak", 3)]

def test_checkoff(sut, monkeypatch):

    list_1 = []
    list_2 = []

    def fake_insert_tracker(db, habit_name, date, status):
        assert db == "fake_db.db"
        list_1.append((habit_name, date, status))

    def fake_update_streak(self, habit_name):
        list_2.append(habit_name)

    monkeypatch.setattr(habit_tracker, "insert_tracker", fake_insert_tracker)
    monkeypatch.setattr(Habit_Tracker, "update_streak", fake_update_streak)

    sut.checkoff("Swimming", "2025-01-01", "Done!")

    assert list_1 == [("Swimming", "2025-01-01", "Done!")]
    assert list_2 == ["Swimming"]
