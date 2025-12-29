from datetime import date
import analysis
from analysis import Analysis
import pytest

class FakeHabitTracker:

    def __init__(self, db):
        self.db = db

    def completion_count(self, habit_name, period):
        assert habit_name == "Cooking"
        assert period == "day"
        if habit_name == "Cooking":
            return [(None, 2), (None, 0), (None, 3), (None, 2)]
        else:
            return []

@pytest.fixture
def sut():
    db = "fake_db.db"
    return Analysis(db)

def test_get_habit_data(sut, monkeypatch):

    def fake_function(db, column, habit_name):
        assert db == "fake_db.db"
        assert habit_name == "Swimming"
        if column == "*":
            return (1, "Swimming", "Swimming for 1 hour", "Weekly", "2025-01-01", 2, 3)
        else:
            return (3, )

    monkeypatch.setattr(analysis, 
        "get_data_from_myhabit_by_name",
        fake_function
    )

    result_one = sut.get_habit_data("max_streak", "Swimming")
    assert result_one == (3, )

    result_all = sut.get_habit_data("*", "Swimming")
    assert result_all == (1, "Swimming", "Swimming for 1 hour", "Weekly", "2025-01-01", 2, 3)
    assert len(result_all) == 7

def test_habit_list(sut, monkeypatch):

    def fake_function(db, column, table):
        assert db == "fake_db.db"
        return ["Swimming", "Jogging"]
    
    monkeypatch.setattr(analysis, 
        "get_distinct_value",
        fake_function
    )

    result = sut.habit_list()
    assert result == ["Swimming", "Jogging"]

def test_habit_list_none(sut, monkeypatch):
    '''
    no habits in the table, so return empty habit list.
    '''
    def fake_function(db, column, table):
        assert db == "fake_db.db"
        return []
    
    monkeypatch.setattr(analysis, "get_distinct_value", fake_function)

    result = sut.habit_list()
    assert result == []

def test_habit_list_by_frequency(sut, monkeypatch):

    def fake_function(db, column, period):
        assert db == "fake_db.db"
        assert column == "habit_name"
        assert period == "Weekly"
        return ["Swimming", "Jogging"]
    
    monkeypatch.setattr(analysis, "get_data_from_myhabit_by_period", fake_function) 

    result = sut.habit_list_by_frequency("Weekly")
    assert result == ["Swimming", "Jogging"]

def test_habit_list_by_frequency_none(sut, monkeypatch):
    '''
    no habit is found for this frequency/period.
    the result should be empty list.
    '''

    def fake_function(db, column, period):
        assert db == "fake_db.db"
        assert column == "habit_name"
        assert period == "Weekly"
        return []
    
    monkeypatch.setattr(analysis, "get_data_from_myhabit_by_period", fake_function) 

    result = sut.habit_list_by_frequency("Weekly")
    assert result == []

def test_habit_log_from_tracker(sut, monkeypatch):

    def fake_function(db, column, habit_name):
        assert db == "fake_db.db"
        assert column == "date, status"
        assert habit_name == "Swimming"
        return ["2025-01-01", "Done!"]
    
    monkeypatch.setattr(analysis, "get_data_from_tracker", fake_function) 

    result = sut.habit_log_from_tracker("Swimming")
    assert result == ["2025-01-01", "Done!"]

def test_habit_data_in_selected_period_week(sut, monkeypatch):

    def fake_function(db, selected_time):
        assert db == "fake_db.db"
        assert selected_time == "2025-01-01"
        results = ["2025-01-01", "Swimming", "Done!"]
        columns = ["date", "habit_name", "status"]
        return results, columns
    
    monkeypatch.setattr(analysis, "weekly_habit_log", fake_function)

    result = sut.habit_data_in_selected_period("2025-01-01", True)
    assert result == (["2025-01-01", "Swimming", "Done!"], ["date", "habit_name", "status"])

def test_habit_data_in_selected_period_non_week(sut, monkeypatch):

    def fake_function(db, selected_time):
        assert db == "fake_db.db"
        assert selected_time == "2025-01-01"
        results = ["2025-01-01", "Swimming", "Done!"]
        columns = ["date", "habit_name", "status"]
        return results, columns

    monkeypatch.setattr(analysis, "daily_and_monthly_habit_log", fake_function)

    result = sut.habit_data_in_selected_period("2025/01/01", False)
    assert result == (["2025-01-01", "Swimming", "Done!"], ["date", "habit_name", "status"])

class Fakedate(date):
    @classmethod
    def today(cls):
        return cls(2025, 1, 7)

def test_calculate_successrate_day(sut, monkeypatch):
    '''
    normal case: 3 successful records in 4 days.
    Success rate should be 3/4=0.75
    '''

    def fake_function_db(db, column, habit_name):
        assert db == "fake_db.db"
        assert column == "frequency, start_date"
        assert habit_name == "Cooking"
        return ("2 time(s) per day", "2025-01-04 11:11")

    monkeypatch.setattr(analysis, "get_data_from_myhabit_by_name", fake_function_db)
    monkeypatch.setattr(analysis, "Habit_Tracker", FakeHabitTracker)
    monkeypatch.setattr(analysis, "date", Fakedate)

    result = sut.calculate_successrate("Cooking")
    assert result == 0.75

def test_calculate_successrate_no_record(sut, monkeypatch):
    '''
    no such habit is found in the database, and thus None is returned when query data from database.
    Success rate should be 0.
    '''

    def fake_function_db(db, column, habit_name):
        assert db == "fake_db.db"
        assert column == "frequency, start_date"
        assert habit_name == "Running"
        return None

    monkeypatch.setattr(analysis, "get_data_from_myhabit_by_name", fake_function_db)
    monkeypatch.setattr(analysis, "date", Fakedate)

    result = sut.calculate_successrate("Running")
    assert result == 0

def test_calculate_successrate_wrongdate(sut, monkeypatch):
    '''
    Start date is later than today.
    Success rate should be 0.
    '''

    def fake_function_db(db, column, habit_name):
        assert db == "fake_db.db"
        assert column == "frequency, start_date"
        assert habit_name == "Cooking"
        return ("2 time(s) per day", "2025-01-20 11:11")

    monkeypatch.setattr(analysis, "get_data_from_myhabit_by_name", fake_function_db)
    monkeypatch.setattr(analysis, "date", Fakedate)

    result = sut.calculate_successrate("Cooking")
    assert result == 0