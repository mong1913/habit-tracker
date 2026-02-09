from analysis import Analysis
from habit_tracker import Habit_Tracker


class Habit:
    def __init__(self, db, habit_name):
        """
        When the object is initialized, load habit properties and its event log.
        """
        self.db = db
        self.id = None
        self.habit_name = None
        self.description = None
        self.frequency = None
        self.start_date = None
        self.current_streak = None
        self.longest_streak = None
        self.log = None
        self.load_habit_properties(habit_name)
        self.load_habit_log(habit_name)

    def load_habit_properties(self, habit_name):
        """
        Updates streak count in myhabit table, then gets habit properties and loads to the object attributes.
        """
        analysis = Analysis(self.db)
        habit_tracker = Habit_Tracker(self.db)

        habit_tracker.update_streak(habit_name)
        habit_properties = analysis.get_habit_data("*", habit_name)
        if habit_properties:
            (
                self.id,
                self.habit_name,
                self.description,
                self.frequency,
                self.start_date,
                self.current_streak,
                self.longest_streak,
            ) = habit_properties
        else:
            return None

    def load_habit_log(self, habit_name):
        """
        Loads the habit log from tracker table to the object attribute.
        """
        analysis = Analysis(self.db)
        self.log = analysis.habit_log_from_tracker(habit_name)
