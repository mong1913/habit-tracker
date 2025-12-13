from datetime import date
from analysis import Analysis

def test_get_habit_data(monkeypatch):

    def fake_function(column, habit_name):
        assert habit_name == "Swimming"
        if column == "*":
            return (1, "Swimming", "Swimming for 1 hour", "Weekly", "2025-01-01", 2, 3)
        else:
            return (3, )

    monkeypatch.setattr(
        "analysis.get_data_from_myhabit_by_name",
        fake_function
    )

    analysis = Analysis()
    
    result_one = analysis.get_habit_data("max_streak", "Swimming")
    assert result_one == (3, )

    result_all = analysis.get_habit_data("*", "Swimming")
    assert result_all == (1, "Swimming", "Swimming for 1 hour", "Weekly", "2025-01-01", 2, 3)
    assert len(result_all) == 7

def test_habit_list(monkeypatch):

    def fake_function(column, table):
        return ["Swimming", "Jogging"]
    
    monkeypatch.setattr(
        "analysis.get_distinct_value",
        fake_function
    )

    analysis = Analysis()

    result = analysis.habit_list()
    assert result == ["Swimming", "Jogging"]

def test_habit_list_none(monkeypatch):
    '''
    no habits in the table, so return empty habit list.
    '''
    def fake_function(column, table):
        return None
    
    monkeypatch.setattr(
        "analysis.get_distinct_value",
        fake_function
    )

    analysis = Analysis()

    result = analysis.habit_list()
    assert result == []

def test_habit_list_by_frequency(monkeypatch):

    def fake_function(column, period):
        assert column == "habit_name"
        assert period == "Weekly"
        return ["Swimming", "Jogging"]
    
    monkeypatch.setattr(
        "analysis.get_data_from_myhabit_by_period",
        fake_function
    ) 

    analysis = Analysis()

    result = analysis.habit_list_by_frequency("Weekly")
    assert result == ["Swimming", "Jogging"]

def test_habit_list_by_frequency_none(monkeypatch):
    '''
    no habit is found for this frequency/period.
    the result should be empty list.
    '''

    def fake_function(column, period):
        assert column == "habit_name"
        assert period == "Weekly"
        return None
    
    monkeypatch.setattr(
        "analysis.get_data_from_myhabit_by_period",
        fake_function
    ) 

    analysis = Analysis()

    result = analysis.habit_list_by_frequency("Weekly")
    assert result == []

def test_habit_log_from_tracker(monkeypatch):

    def fake_function(column, habit_name):
        assert column == "date, status"
        assert habit_name == "Swimming"
        return ["2025-01-01", "Done!"]
    
    monkeypatch.setattr(
        "analysis.get_data_from_tracker",
        fake_function
    ) 

    analysis = Analysis()

    result = analysis.habit_log_from_tracker("Swimming")
    assert result == ["2025-01-01", "Done!"]

def test_habit_data_in_selected_period_week(monkeypatch):

    def fake_function(selected_time):
        assert selected_time == "2025-01-01"
        results = ["2025-01-01", "Swimming", "Done!"]
        columns = ["date", "habit_name", "status"]
        return results, columns
    
    monkeypatch.setattr(
        "analysis.weekly_habit_log",
        fake_function
    )

    analysis = Analysis()

    result = analysis.habit_data_in_selected_period("2025-01-01", True)
    assert result == (["2025-01-01", "Swimming", "Done!"], ["date", "habit_name", "status"])

def test_habit_data_in_selected_period_non_week(monkeypatch):

    def fake_function(selected_time):
        assert selected_time == "2025-01-01"
        results = ["2025-01-01", "Swimming", "Done!"]
        columns = ["date", "habit_name", "status"]
        return results, columns
    
    monkeypatch.setattr(
        "analysis.daily_and_monthly_habit_log",
        fake_function
    )

    analysis = Analysis()

    result = analysis.habit_data_in_selected_period("2025/01/01", False)
    assert result == (["2025-01-01", "Swimming", "Done!"], ["date", "habit_name", "status"])

class Fakedate(date):
    @classmethod
    def today(cls):
        return cls(2025, 1, 7)

def test_calculate_successrate(monkeypatch):
    '''
    normal case: 3 successful records in 4 days.
    Success rate should be 3/4=0.75
    '''

    def fake_function_db(column, habit_name):
        assert habit_name == "Cooking"
        return ("2 time(s) per day", "2025-01-04 11:11")

    def fake_function_count(habit_name, column):
        assert habit_name == "Cooking"
        return [(None, None, None, 2), (None, None, None, 0), (None, None, None, 3), (None, None, None, 2)]

    monkeypatch.setattr(
        "analysis.get_data_from_myhabit_by_name", 
        fake_function_db
    )

    monkeypatch.setattr(
        "analysis.count_done_skip", 
        fake_function_count
    )

    monkeypatch.setattr(
        "analysis.date",
        Fakedate
    )

    analysis = Analysis()

    result = analysis.calculate_successrate("Cooking")
    assert result == 0.75

def test_calculate_successrate_no_record(monkeypatch):
    '''
    no such habit is found in the database, and thus None is returned when query data from database.
    Success rate should be 0.
    '''

    def fake_function_db(column, habit_name):
        assert habit_name == "Running"
        return None

    monkeypatch.setattr(
        "analysis.get_data_from_myhabit_by_name", 
        fake_function_db
    )

    monkeypatch.setattr(
        "analysis.date",
        Fakedate
    )

    analysis = Analysis()

    result = analysis.calculate_successrate("Running")
    assert result == 0

def test_calculate_successrate_wrongdate(monkeypatch):
    '''
    Start date is later than today.
    Success rate should be 0.
    '''

    def fake_function_db(column, habit_name):
        assert habit_name == "Cooking"
        return ("2 time(s) per day", "2025-01-20 11:11")

    monkeypatch.setattr(
        "analysis.get_data_from_myhabit_by_name", 
        fake_function_db
    )

    monkeypatch.setattr(
        "analysis.date",
        Fakedate
    )

    analysis = Analysis()

    result = analysis.calculate_successrate("Cooking")
    assert result == 0