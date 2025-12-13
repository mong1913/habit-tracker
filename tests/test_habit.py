from habit import Habit

class Fakeanalysis:
    def get_habit_data(self, column, habit_name):
        assert column == "*"
        assert habit_name == "Swimming"
        return (2, "Swimming", "Swimming for 1 hour", "3 time(s) per week", "2025-01-01", 2, 4)

    def habit_log_from_tracker(self, habit_name):
        assert habit_name == "Swimming"
        return [("2025-01-03", "Done!"), ("2025-01-01", "Done!")]
    
def test_init(monkeypatch):
    func_call = []

    def fake_func_1(self, habit_name):
        func_call.append("f1")

    def fake_func_2(self, habit_name):
        func_call.append("f2")

    monkeypatch.setattr(
        Habit,
        "load_habit_properties", 
        fake_func_1
    )

    monkeypatch.setattr(
        Habit,
        "load_habit_log", 
        fake_func_2
    )

    habit = Habit("Swimming")
    assert func_call == ["f1", "f2"]

def test_load_habit_properties(monkeypatch):

    habit = Habit.__new__(Habit)
    
    monkeypatch.setattr(
        "habit.Analysis",
        Fakeanalysis
    )

    habit = Habit("Swimming")

    habit.load_habit_properties("Swimming")
    assert habit.id == 2
    assert habit.habit_name == "Swimming"
    assert habit.description == "Swimming for 1 hour"
    assert habit.frequency == "3 time(s) per week"
    assert habit.start_date == "2025-01-01"
    assert habit.current_streak == 2 
    assert habit.longest_streak == 4

def test_load_habit_log(monkeypatch):

    habit = Habit.__new__(Habit)
    
    monkeypatch.setattr(
        "habit.Analysis",
        Fakeanalysis
    )

    habit = Habit("Swimming")

    habit.load_habit_log("Swimming")
    assert habit.log == [("2025-01-03", "Done!"), ("2025-01-01", "Done!")]
    assert habit.start_date == "2025-01-01"