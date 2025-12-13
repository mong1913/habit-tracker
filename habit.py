from analysis import Analysis

class Habit:

    def __init__(self, habit_name):
        '''
        When the object is initialize, load habit properties and log.
        '''
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
        analysis = Analysis()
        habit_properties = analysis.get_habit_data("*", habit_name)
        if habit_properties:
            (self.id,
            self.habit_name, 
            self.description,
            self.frequency,
            self.start_date,
            self.current_streak,
            self.longest_streak
            ) = habit_properties
        else:    
            return None

    def load_habit_log(self, habit_name):
        analysis = Analysis()
        self.log = analysis.habit_log_from_tracker(habit_name)
        if self.log is not None:
            self.start_date = self.log[-1][0]
