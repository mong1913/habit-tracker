from db import (get_data_from_myhabit_by_name, get_data_from_myhabit_by_period, get_distinct_value, get_data_from_tracker,
                 weekly_habit_log, daily_and_monthly_habit_log, count_done_skip)
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

class Analysis:

    def __init__(self):
        pass

    def get_habit_data(self, column, habit_name):
        return get_data_from_myhabit_by_name(column, habit_name)
    
    def habit_list(self):
        habit_list = get_distinct_value("habit_name", "myhabit")
        return habit_list if habit_list else []

    def habit_list_by_frequency(self, period):
        habit_by_frequency = get_data_from_myhabit_by_period("habit_name", period)
        return habit_by_frequency if habit_by_frequency else []

    def habit_log_from_tracker(self, habit_name):
        return get_data_from_tracker("date, status", habit_name)

    def habit_data_in_selected_period(self, selected_time, weekly=False):
        '''
        Args:
            selected_time: date
            weekly true for getting weekly log. Assign False to weekly parameter for getting daily or monthly log.
        Returns:
            - For weekly log: a list of tuple(date, year_week, habit_name, status) in the specific week.
            - For daily log: a list of tuple(date, habit_name, status) on the specific date.
            - For monthly log: a list of tuple(date, habit_name, status) in the specific month.
        '''
        if weekly == True:
            results, columns = weekly_habit_log(selected_time)
        else:
            converted_time = str(selected_time).replace("/", "-")
            results, columns = daily_and_monthly_habit_log(converted_time)

        if results:
            final_result = [[item][0] for item in results]
        else:
            final_result = None

        column_name = []
        for i in range(len(columns)):
            column_name.append(columns[i])

        return final_result, column_name
    
    def calculate_successrate(self, habit_name):
        '''
        Calculates the completion(Done and Skip) rate (0.0-1.0).

        Logic(example for day period):
            - get frequency(e.g. 3 time(s) per day) and start date.
            - count days that reached target as success count.
            - count days since start date as total count.

        Returns:
            float: success count devided by total count.
            0.0 if habit data not found or the start date is later than today.
        '''
        habit_data = get_data_from_myhabit_by_name("frequency, start_date", habit_name)
        if habit_data is None:
            return 0
        
        frequency, start_date = habit_data
        times = int(frequency.split()[0])
        period = frequency.split()[3]

        start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M").date()
        today = date.today()

        if start_date > today:
            return 0

        try:
            if period == "day":
                habit_log = count_done_skip(habit_name, 'date_only')
                total_count = (today - start_date).days + 1
                success_count = sum(1 for row in habit_log if row[3] >= times) 
                
            elif period == "week":
                habit_log = count_done_skip(habit_name, 'year_week')
                start_of_this_week = today - timedelta(today.weekday() - 1)
                start_of_target_week = start_date - timedelta(start_date.weekday() - 1)
                total_count = (start_of_this_week - start_of_target_week).days / 7 + 1
                success_count = sum(1 for row in habit_log if row[3] >= times)

            elif period == "month":
                habit_log = count_done_skip(habit_name, 'year_month')
                delta = relativedelta(today, start_date)
                total_count = delta.years * 12 + delta.months + 1
                success_count = sum(1 for row in habit_log if row[3] >= times)

            success_rate = round(success_count / total_count, 2)
            return success_rate 
        
        except:
            return 0
        

 