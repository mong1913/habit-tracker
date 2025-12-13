from habit_tracker import Habit_Tracker
import sqlite3, pytest

def test_add_habit(monkeypatch):

    item_list = []

    def fake_func(arg1, arg2, arg3, arg4, arg5, arg6):
        item_list.append((arg1, arg2, arg3, arg4, 0, 0))

    monkeypatch.setattr(
        "habit_tracker.insert_myhabit",
        fake_func
    )

    habit_tracker = Habit_Tracker()

    habit_tracker.add_habit("arg1", "arg2", "arg3", "arg4")
    assert item_list == [("arg1", "arg2", "arg3", "arg4", 0, 0)]

def test_add_habit_error(monkeypatch):
    def fake_func_error(arg1, arg2, arg3, arg4, arg5, arg6):
        raise sqlite3.IntegrityError
    
    monkeypatch.setattr(
        "habit_tracker.insert_myhabit",
        fake_func_error
    )

    habit_tracker = Habit_Tracker()

    with pytest.raises(sqlite3.IntegrityError):
        habit_tracker.add_habit("arg1", "arg2", "arg3", "arg4")
    
def test_delete_habit(monkeypatch):
    item_list = []
    def fake_func(arg1, arg2):
        item_list.append((arg1, "myhabit"))

    monkeypatch.setattr(
        "habit_tracker.delete_value",
        fake_func
    )

    habit_tracker = Habit_Tracker()

    habit_tracker.delete_habit("arg1")
    assert item_list == [("arg1", "myhabit")]

def test_streak_count_day():

    habit_tracker = Habit_Tracker()

    habit_log = [("2025-01-10", "test", "2025-01", 2), 
                 ("2025-01-11", "test", "2025-01", 3)]
    updated_streak, max_streak = habit_tracker.streak_count(habit_log, "day", 2)

    assert updated_streak == 2
    assert max_streak == 2

def test_streak_count_week():

    habit_tracker = Habit_Tracker()

    habit_log = [("2025-01-10", "2025-W01", "2025-01", 2), 
                 ("2025-01-16", "2025-W02", "2025-01", 3),
                 ("2025-01-29", "2025-W04", "2025-01", 2)]
    updated_streak, max_streak = habit_tracker.streak_count(habit_log, "week", 2)

    assert updated_streak == 1
    assert max_streak == 2

def test_streak_count_month():

    habit_tracker = Habit_Tracker()

    habit_log = [("2025-01-10", "test", "2025-01", 2), 
                 ("2025-02-16", "test", "2025-02", 3),
                 ("2025-04-29", "test", "2025-04", 2)]
    updated_streak, max_streak = habit_tracker.streak_count(habit_log, "month", 2)

    assert updated_streak == 1
    assert max_streak == 2

def test_update_streak(monkeypatch):

    item_list = []

    def fake_func_get_data(arg1, arg2):
        assert arg2 == "Swimming"
        return ["3 time(s) per day"]
    
    def fake_func_count_success(arg1, arg2):
        assert arg1 == "Swimming"
        assert arg2 == "date_only"
        return None
    
    def fake_func_streak_count(self, arg1, arg2, arg3):
        assert arg2 == "day"
        assert arg3 == 3
        return (2, 3)
    
    def fake_update_myhabit(arg1, arg2, arg3):
        item_list.append((arg1, arg2, arg3))
    
    monkeypatch.setattr("habit_tracker.get_data_from_myhabit_by_name", 
                        fake_func_get_data    
    )    

    monkeypatch.setattr("habit_tracker.count_done_skip", 
                        fake_func_count_success  
    )    

    monkeypatch.setattr(Habit_Tracker,
                        "streak_count", 
                        fake_func_streak_count
    )    

    monkeypatch.setattr("habit_tracker.update_myhabit", 
                        fake_update_myhabit
    )    

    habit_tracker = Habit_Tracker()

    habit_tracker.update_streak("Swimming")
    assert item_list == [("Swimming", "current_streak", 2), 
                         ("Swimming", "max_streak", 3)]

def test_update_streak_wrong_period(monkeypatch):

    item_list = []

    def fake_func_get_data(arg1, arg2):
        assert arg2 == "Swimming"
        return ["3 time(s) per year"]
    
    def fake_update_myhabit(arg1, arg2, arg3):
        item_list.append((arg1, arg2, arg3))
    
    monkeypatch.setattr("habit_tracker.get_data_from_myhabit_by_name", 
                        fake_func_get_data    
    )    

    monkeypatch.setattr("habit_tracker.count_done_skip", 
                        lambda arg1, arg2: None 
    )    

    monkeypatch.setattr(Habit_Tracker,
                        "streak_count", 
                        lambda self, arg1, arg2, arg3: None
    )    

    monkeypatch.setattr("habit_tracker.update_myhabit", 
                        fake_update_myhabit
    )    

    habit_tracker = Habit_Tracker()

    habit_tracker.update_streak("Swimming")
    
    assert item_list == [("Swimming", "current_streak", 0), 
                         ("Swimming", "max_streak", 0)]

def test_update_start_date(monkeypatch):

    item_list = []

    def fake_func_get_data(arg1, arg2):
        assert arg2 == "Swimming"
        return [("2025-01-04", ), ("2025-01-03", )]

    def fake_update_myhabit(arg1, arg2, arg3):
        item_list.append((arg1, arg2, arg3))

    monkeypatch.setattr("habit_tracker.get_data_from_tracker", 
                        fake_func_get_data
    )    

    monkeypatch.setattr("habit_tracker.update_myhabit", 
                        fake_update_myhabit
    )    

    habit_tracker = Habit_Tracker()

    habit_tracker.update_start_date("Swimming")

    assert item_list == [("Swimming", "start_date", "2025-01-03")]

def test_checkoff(monkeypatch):

    list_1 = []
    list_2 = []
    list_3 = []

    def fake_func_insert_tracker(arg1, arg2, arg3):
        list_1.append((arg1, arg2, arg3))

    monkeypatch.setattr(
        "habit_tracker.insert_tracker",
        fake_func_insert_tracker
    )

    monkeypatch.setattr(
        Habit_Tracker,
        "update_streak",
        lambda self, arg1: list_2.append(arg1)
    )

    monkeypatch.setattr(
        Habit_Tracker,
        "update_start_date",
        lambda self, arg1: list_3.append(arg1)
    )

    habit_tracker = Habit_Tracker()

    habit_tracker.checkoff("Swimming", "2025-01-01", "Done!")

    assert list_1 == [("Swimming", "2025-01-01", "Done!")]
    assert list_2 == ["Swimming"]
    assert list_3 == ["Swimming"]