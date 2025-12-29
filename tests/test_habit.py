from habit import Habit
import habit
import pytest

class Fakeanalysis:

    def __init__(self, db):
        self.db = db

    def get_habit_data(self, column, habit_name):
        assert column == "*"
        assert habit_name == "Swimming"
        return (2, "Swimming", "Swimming for 1 hour", "3 time(s) per week", "2025-01-01", 2, 4)

    def habit_log_from_tracker(self, habit_name):
        assert habit_name == "Swimming"
        return [("2025-01-03", "Done!"), ("2025-01-01", "Done!")]
    
class FakeHabitTracker:

    def __init__(self, db):
        self.db = db

    def update_streak(self, habit_name):
        assert habit_name == "Swimming"
        return None
    
@pytest.fixture
def sut(monkeypatch):
    db = "fake_db.db"
    monkeypatch.setattr(habit, "Analysis", Fakeanalysis)
    monkeypatch.setattr(habit, "Habit_Tracker", FakeHabitTracker)
    return Habit(db, "Swimming")
    
def test_init(monkeypatch):
    func_call = []

    def fake_func_1(self, habit_name):
        assert habit_name == "Swimming"
        func_call.append("f1")
        
    def fake_func_2(self, habit_name):
        assert habit_name == "Swimming"
        func_call.append("f2")

    monkeypatch.setattr(Habit, "load_habit_properties", fake_func_1)
    monkeypatch.setattr(Habit, "load_habit_log", fake_func_2)

    habit = Habit("fake_db.db", "Swimming")
    assert func_call == ["f1", "f2"]

def test_load_habit_properties(sut):

    sut.load_habit_properties("Swimming")
    assert sut.id == 2
    assert sut.habit_name == "Swimming"
    assert sut.description == "Swimming for 1 hour"
    assert sut.frequency == "3 time(s) per week"
    assert sut.start_date == "2025-01-01"
    assert sut.current_streak == 2 
    assert sut.longest_streak == 4

def test_load_habit_log(sut):

    sut.load_habit_log("Swimming")
    assert sut.log == [("2025-01-03", "Done!"), ("2025-01-01", "Done!")]
    assert sut.start_date == "2025-01-01"