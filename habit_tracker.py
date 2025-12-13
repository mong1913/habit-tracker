from db import (insert_myhabit, delete_value, 
                insert_tracker, get_data_from_myhabit_by_name, get_data_from_tracker, update_myhabit, count_done_skip)
from datetime import datetime, timedelta 
from dateutil.relativedelta import relativedelta
import sqlite3

class Habit_Tracker:

    def __init__(self):
        pass
    
    def add_habit(self, habit_name, description, frequency, start_date):
        try:
            insert_myhabit(habit_name, description, frequency, start_date, 0, 0)

        except sqlite3.IntegrityError as err:
            raise err

    def delete_habit(self, habit_name):
        delete_value(habit_name, "myhabit")

    def streak_count(self, habit_log, period, times):
        max_streak = 0
        for i in range(len(habit_log)):
            date_str, week_str, month_str, success = habit_log[i]            
            date = datetime.strptime(date_str, "%Y-%m-%d")
            month = datetime.strptime(month_str, "%Y-%m")
             
            if period == "day":
                current = date_str
                previous_period = (date - timedelta(1)).strftime("%Y-%m-%d")
            elif period == "week":
                current = week_str
                previous_period = (date - timedelta(7)).strftime("%Y-W%W")
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
        frequency = get_data_from_myhabit_by_name("frequency", habit_name)[0]

        times = int(frequency.split()[0])
        period = frequency.split()[3]

        updated_streak = 0
        max_streak = 0
        if period == "day":
            habit_log = count_done_skip(habit_name, "date_only")
            updated_streak, max_streak = self.streak_count(habit_log, "day", times)
        elif period == "week":
            habit_log = count_done_skip(habit_name, "year_week")
            updated_streak, max_streak = self.streak_count(habit_log, "week", times)
        elif period == "month":
            habit_log = count_done_skip(habit_name, "year_month")
            updated_streak, max_streak = self.streak_count(habit_log, "month", times)
        
        update_myhabit(habit_name, "current_streak", updated_streak)
        update_myhabit(habit_name, "max_streak", max_streak)

    def update_start_date(self, habit_name):
        first_date = get_data_from_tracker("date", habit_name)[-1][0]
        update_myhabit(habit_name, "start_date", first_date)

    def checkoff(self, habit_name, date, status):
        insert_tracker(habit_name, date, status)
        self.update_streak(habit_name)
        self.update_start_date(habit_name)

 


    # def update_streak_once(self, habit_name):
    #     row_list = get_data_from_tracker("*", habit_name)

    #     updated_streak = 0
    #     for i in range(len(row_list), 0, -1):
    #         checkin_id, habit_id, date, status, streak = row_list[i]
    #         converted_date = datetime.strptime(date.split(" ")[0], "%Y-%m-%d")

    #         if i == len(row_list) or (converted_date - timedelta(days=1)) != date_previous:
    #             updated_streak = 0 if status == "Missed." else 1

    #         elif (converted_date - timedelta(days=1)) == date_previous:
    #             if status in ["Done!", "Skip."]:
    #                 updated_streak += 1  
    #             else: updated_streak = 0
        
    #         else: updated_streak = updated_streak # if >= 2 times records in a day

    #         update_tracker(checkin_id, updated_streak)
    #         date_previous = converted_date

    #     update_myhabit(habit_name, updated_streak)

    # def update_streak_multitimes(self, habit_name, frequency):
    #     row_list = get_data_from_tracker("*", habit_name)
    #     times = int(frequency[0])
    #     _, _, period = frequency.partition("per ")

    #     count = 0
    #     updated_streak = 0
    #     for i in range(len(row_list)-1, -1, -1):
    #         checkin_id, habit_id, date, status, streak = row_list[i]
    #         if period == "day":
    #             converted_period = datetime.strptime(date.split(" ")[0], "%Y-%m-%d")
    #             previous_period = datetime.strptime(date.split(" ")[0], "%Y-%m-%d")-timedelta(1)
    #         # elif period == "week":
    #         #     converted_period = datetime.strptime(date.split(" ")[0], "%Y-%m-%d")
    #         elif period == "month":
    #             converted_period = date[:7]
    #             #year = datetime.strptime(date[:4], "%Y")
    #             month = date[5:7]
    #             previous_period = date[:4] + str(int(month)-1)
            
    #         if i == len(row_list)-1 or converted_period != previous_period:
    #             if status in ["Done!", "Skip."]:
    #                 count = 1 
    #             else: 
    #                 count = 0

    #         elif converted_period == previous_period:
    #             if status in ["Done!", "Skip."]:
    #                 count += 1 
    #             else: 
    #                 count = 0
            
    #         if count == times:
    #             updated_streak += 1  
    #         elif count == 0:
    #             updated_streak = 0

    #         update_tracker(checkin_id, updated_streak)
    #         #period_previous = converted_period

    #     update_myhabit(habit_name, updated_streak)









 
