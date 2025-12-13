import sqlite3

def con_db(db="habit_tracker.db"):
    con = sqlite3.connect(db)
    return con

def create_tables():
    '''
    Create habit(myhabit) and tracker table.        
    status in tracker takes 3 values: "Done!", "Skip.", "Missed."
    '''
    with con_db() as con:
        cur = con.cursor()
        
        cur.execute('''
                    CREATE TABLE IF NOT EXISTS myhabit (
                    habit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    habit_name TEXT UNIQUE,
                    description TEXT,
                    frequency TEXT,
                    start_date TEXT,
                    current_streak INTEGER,
                    max_streak INTEGER)
                    ''')

        cur.execute('''
                    CREATE TABLE IF NOT EXISTS tracker (
                    checkin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    habit_id INTEGER,
                    date TEXT, 
                    status TEXT,
                    FOREIGN KEY(habit_id) REFERENCES myhabit(habit_id) ON DELETE CASCADE)
                    ''')

        cur.close()

def get_data_from_myhabit_by_name(column, habit_name):
    with con_db() as con:
        cur = con.cursor()
        try:   
            cur.execute(f'''SELECT {column} FROM myhabit WHERE habit_name = ?''', (habit_name,))
            result = cur.fetchone()
            return result if result else None
        finally:
            cur.close()  

def get_data_from_myhabit_by_period(column, period):
    with con_db() as con:
        cur = con.cursor()
        try:   
            cur.execute(f'''SELECT {column} FROM myhabit WHERE frequency LIKE ?''', ('%' + period,))
            results = cur.fetchall()
            return [row[0] for row in results] if results else None
        finally:
            cur.close()  

def get_habit_id(habit_name):
    '''
    Args: 
        habit_name: str
    Returns:
        habit_id: int
    '''
    try: 
        return get_data_from_myhabit_by_name("habit_id", habit_name)[0]
    except:
        return None

def get_data_from_tracker(column, habit_name):
    with con_db() as con:
        cur = con.cursor()
        habit_id = get_habit_id(habit_name)
        cur.execute(f''' SELECT {column} FROM tracker
                        WHERE habit_id = ? ORDER BY date DESC''', (habit_id,))
        try:   
            results = cur.fetchall()
            return [row for row in results] if results else None
        except:
            return None
        finally:
            cur.close()  

def get_distinct_value(column, table):
    with con_db() as con:
        cur = con.cursor()
        cur.execute(f'''SELECT DISTINCT {column} FROM {table}''')
        try:    
            results = cur.fetchall()
            return [row[0] for row in results] if results else None
        except:
            return None
        finally:
            cur.close()  

def insert_myhabit(habit_name, description, frequency, start_date, current_streak, max_streak):
    with con_db() as con:
        cur = con.cursor()
        try:
            cur.execute('''
                        INSERT INTO myhabit (habit_name, description, frequency, 
                                                start_date, current_streak, max_streak)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ''', (habit_name, description, frequency, start_date, current_streak, max_streak))
            con.commit() 
        finally:
            cur.close()        

def insert_tracker(habit_name, date, status):
    with con_db() as con:
        cur = con.cursor()
        habit_id = get_habit_id(habit_name)
        try:
            cur.execute('''
                        INSERT INTO tracker (habit_id, date, status)
                        VALUES (?, ?, ?)
                        ''', (habit_id, date, status))
            con.commit() 
        finally:
            cur.close()  

def delete_value(habit_name, table):
    with con_db() as con:
        con.execute("PRAGMA foreign_keys = ON")
        cur = con.cursor()
        habit_id = get_habit_id(habit_name)
        try:
            cur.execute(f'''
                        DELETE FROM {table} WHERE habit_id = ?
                        ''', (habit_id, ))
            con.commit() 
        finally:
            cur.close()

def update_myhabit(habit_name, column, value):
    with con_db() as con:
        cur = con.cursor()
        try:
            cur.execute(f''' 
                    UPDATE myhabit SET {column} = ? WHERE habit_name = ?
                    ''', (value, habit_name))        
            con.commit()
        finally:
            cur.close()  

def daily_and_monthly_habit_log(time):
    '''
    Args:
        time: date
    Returns:
        list: a list of tuple(date, habit name, status). Tuples are records from tracker table on the specific date or in the specific month.
    '''
    with con_db() as con:
        cur = con.cursor()
        cur.execute(''' 
                    SELECT t.date, m.habit_name, t.status
                    FROM myhabit m
                    JOIN tracker t ON m.habit_id = t.habit_id
                    WHERE t.date LIKE ?
                    ORDER BY t.date DESC
                    ''', (time + '%', ))
        try:   
            rows = cur.fetchall()
            results = [row for row in rows] if rows else None
            columns = [descrip[0] for descrip in cur.description]
            return results, columns
        except:
            return None
        finally:
            cur.close()

def weekly_habit_log(time):
    '''
    Args:
        time: date
    Returns:
        list: a list of tuple(date, year week, habit name, status). Tuples are records from tracker table in the specific week.
    '''
    week = time.strftime("%Y-W%W")
    with con_db() as con:
        cur = con.cursor()
        cur.execute(''' 
                    SELECT t.date, STRFTIME('%Y-W%W', t.date) AS year_week, m.habit_name, t.status
                    FROM myhabit m
                    JOIN tracker t ON m.habit_id = t.habit_id
                    WHERE m.frequency LIKE ? AND year_week = ?
                    ORDER BY t.date DESC
                    ''', ('%' + 'week' + '%', week))
        try:   
            rows = cur.fetchall()
            results = [row for row in rows] if rows else None
            columns = [descrip[0] for descrip in cur.description]
            return results, columns
        except:
            return None
        finally:
            cur.close()

def count_done_skip(habit_name, period):
    '''
    Counts completion(including Done and Skip) for the specific habit based on the period(date, week or month).
    The column "count_row" will be used to compare with the target in the specific period.
    
    Example:
    2 records(e.g. 2 times for teeth brushing on the same date) are found in the tracker table: (1, "2025-01-01", 'Done!'), (1, "2025-01-01", 'Done!')
    Returns a list of tuple("2025-01-01", "2025-W01", "2025-01", 2"), which meets the goal and can be used for later streak calculation.
    '''
    with con_db() as con:
        cur = con.cursor()
        habit_id = get_habit_id(habit_name)    

        cur.execute(f'''
                    SELECT 
                    DATE(date) AS date_only, 
                    STRFTIME('%Y-W%W', date) AS year_week,
                    STRFTIME('%Y-%m', date) AS year_month,
                    SUM(CASE WHEN status IN ('Done!', 'Skip.') THEN 1 ELSE 0 END) AS count_row
                    FROM (
                    SELECT habit_id, date, status
                    FROM tracker
                    WHERE habit_id = {habit_id})    
                    GROUP BY {period}
                    ''')
        try:   
            results = cur.fetchall()
            return  [row for row in results] if results else None
        except:
            return None
        finally:
            cur.close()

