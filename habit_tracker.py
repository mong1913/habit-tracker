from db import (insert_myhabit, delete_value, get_data_from_tracker,
                insert_tracker, get_data_from_myhabit_by_name, update_myhabit)
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import sqlite3

class Habit_Tracker:

    def __init__(self, db):
        self.db = db
    
    def add_habit(self, habit_name, description, frequency, start_date):
        try:
            insert_myhabit(self.db, habit_name, description, frequency, start_date, 0, 0)
        except sqlite3.IntegrityError as err:
            raise err

    def delete_habit(self, habit_name):
        delete_value(self.db, habit_name, "myhabit")

    def completion_count(self, habit_name, period):
        '''
        Counts the records with the status of done and skip as completion.
        '''
        date_status = get_data_from_tracker(self.db, "date, status", habit_name)
        completion_mark = ('Done!', 'Skip.')

        if period == "day":
            success_counts = {}
            for date_str, status in date_status:
                if status in completion_mark:
                    event_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M").date()
                    event_date = datetime.strftime(event_date, "%Y-%m-%d")
                    success_counts[event_date] = success_counts.get(event_date, 0) + 1

        elif period == "week":
            success_counts = {}
            for date_str, status in date_status:
                if status in completion_mark:
                    event_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M").date()
                    year_week = event_date.strftime("%G-W%V")
                    success_counts[year_week] = success_counts.get(year_week, 0) + 1

        elif period == "month":
            success_counts = {}
            for date_str, status in date_status:
                if status in completion_mark:
                    event_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M").date()
                    year_month = event_date.strftime("%Y-%m")
                    success_counts[year_month] = success_counts.get(year_month, 0) + 1
        
        success_counts_list = sorted(success_counts.items())
        return success_counts_list

    def fill_history(self, habit_log, period):
        '''
        Fills the blank timestamps based on frequency, so that the log list with consecutive date/week/month can be used to count streak.
        '''
        today = date.today()
        today_month_str = today.strftime("%Y-%m") 
        log_list = []
        if period == "day":
            log_dict = {datetime.strptime(row[0], "%Y-%m-%d").date(): row[1] for row in habit_log}
            start_date = min(log_dict.keys())
            log_date = start_date
            while log_date <= today:
                success = log_dict.get(log_date, 0)
                log_list.append((log_date, success))
                log_date += timedelta(1)

        elif period == "week":
            log_dict = {datetime.strptime(row[0]+ "-1", "%G-W%V-%u").date(): row[1] for row in habit_log}
            start_week_mon = min(log_dict.keys())
            current_week_mon = start_week_mon
            while current_week_mon <= today:
                success = log_dict.get(current_week_mon, 0)
                log_list.append((current_week_mon, success))
                current_week_mon += timedelta(7)     

        elif period == "month": 
            log_dict = {datetime.strptime(row[0], "%Y-%m"): row[1] for row in habit_log} 
            start_month = min(log_dict.keys())
            this_month = datetime.strptime(today_month_str, "%Y-%m")
            current_month = start_month
            while current_month <= this_month:
                success = log_dict.get(current_month, 0)
                log_list.append((current_month, success))
                current_month += relativedelta(months=1)

        return log_list

    def streak_count(self, habit_log, period, times):
        '''
        Calculates the current and maximum streak of the habit based on the habit logs and the frequency.
        '''
        if not habit_log:
            return 0, 0
        else:
            filled_log_list = self.fill_history(habit_log, period)

        max_streak = 0
        updated_streak = 0
        for i in range(len(filled_log_list)):
            event_date, success = filled_log_list[i] 
            date_str = event_date.strftime("%Y-%m-%d")  
            week_str = event_date.strftime("%G-W%V")
            month_str = event_date.strftime("%Y-%m")
            month = datetime.strptime(month_str, "%Y-%m")

            if period == "day":
                current = date_str
                previous_period = (event_date - timedelta(1)).strftime("%Y-%m-%d")
            elif period == "week":
                current = week_str
                previous_period = (event_date - timedelta(7)).strftime("%G-W%V")
            elif period == "month":
                current = month_str
                previous_period = (month - relativedelta(months=1)).strftime("%Y-%m")                           

            if i == 0 or previous_period != previous_row:
                if success >= times:
                    updated_streak = 1 
                else: 
                    updated_streak = 0
            elif previous_period == previous_row:
                if success >= times:
                    updated_streak += 1 
                else: 
                    updated_streak = 0

            if updated_streak > max_streak:
                max_streak = updated_streak

            previous_row = current
        return updated_streak, max_streak

    def update_streak(self, habit_name):
        '''
        Gets current and maximum streak count by calling completion_count and streak_count funcitons.
        '''

        frequency = get_data_from_myhabit_by_name(self.db, "frequency", habit_name)
        if frequency is not None:
            frequency = frequency[0]

            times = int(frequency.split()[0])
            period = frequency.split()[3]

            updated_streak = 0
            max_streak = 0

            habit_log = self.completion_count(habit_name, period)
            updated_streak, max_streak = self.streak_count(habit_log, period, times)

        else:
            updated_streak, max_streak = 0, 0

        update_myhabit(self.db, habit_name, "current_streak", updated_streak)
        update_myhabit(self.db, habit_name, "max_streak", max_streak)

    def checkoff(self, habit_name, date, status):
        '''
        Calls the function from db module to insert the activity into the tracker table.
        Then, call the function in the habit-tracker class to update the new current and max streak count in the habit table.
        '''
        insert_tracker(self.db, habit_name, date, status)
        self.update_streak(habit_name)