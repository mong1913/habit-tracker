import streamlit as st
from db import create_tables
from habit_tracker import Habit_Tracker
from analysis import Analysis
from habit import Habit
from datetime import timedelta, datetime
import sqlite3
import pandas as pd
import os
import shutil

user_db = "habit_tracker.db"
demo_predefined_db = "demo.db"
demo_working_db = (
    "demo_working.db"  # copy of demo_predefined_db for user to interact with
)

create_tables()

# Initialize
if "page" not in st.session_state:
    st.session_state.page = "Home"

if "db_file" not in st.session_state:
    st.session_state.db_file = user_db

# Sidebar menu
with st.sidebar:
    st.title("**Habit Tracker!**")
    if st.session_state.db_file == "demo_working.db":
        st.warning(
            "You are currently in Demo Mode. "
            "Changes will not be saved to your personal tracker. "
            "Feel free to delete or edit."
        )
    st.header("Menu")

    if st.button("Home"):
        st.session_state.page = "Home"
    if st.button("Add Habit"):
        st.session_state.page = "Add_habit"
    if st.button("Check Off Habits"):
        st.session_state.page = "Checkoff"
    if st.button("Analysis"):
        st.session_state.page = "Analysis"

    st.write("---")
    st.header("App Mode")
    if st.button("My Habit"):
        st.session_state.db_file = user_db
        # tracker.set_db(user_db)
        # analysis.set_db(user_db)
        st.rerun()
    if st.button("Fresh Demo"):
        if os.path.exists(demo_predefined_db):
            shutil.copy(demo_predefined_db, demo_working_db)
            st.session_state.db_file = demo_working_db
            st.rerun()
        else:
            st.error("Demo database not found!")

    tracker = Habit_Tracker(st.session_state.db_file)
    analysis = Analysis(st.session_state.db_file)
    now = datetime.now()
    today = datetime.today()

page = st.session_state.page
myhabits = analysis.habit_list()

if page == "Home":
    st.header("Welcome to Habit Tracker", divider="gray")
    st.text("")
    st.text("")
    st.markdown("#### **Currently you have the following habits:**")
    if len(myhabits) == 0:
        st.write("No habits yet. Go to 'Add Habit' to start your first habit!")
    else:
        habits = ", ".join(myhabits)
        st.write(f"{habits}")
    st.text("")
    st.write("Go to side bar for the next actions! Have Fun :)")

elif page == "Add_habit":
    st.header("Start a New Habit")
    new_habit_name = st.text_input("New habit: ")
    description = st.text_input("Description: ")
    frequency = st.selectbox(
        "The habit will repeat:",
        ("X time(s) per day", "X time(s) per week", "X time(s) per month"),
    )
    X = st.slider("X = ", 1, 10)
    frequency = str(X) + frequency[1:]

    if st.button("Submit"):
        time = now.strftime("%Y-%m-%d %H:%M")

        try:
            tracker.add_habit(new_habit_name, description, frequency, start_date=time)
            st.success(f"Successfully added habit {new_habit_name}!")

        except sqlite3.IntegrityError:
            st.warning(f"{new_habit_name} already exists in my habit list!")

elif page == "Checkoff":
    st.header("Habit Check Off")

    habit_to_checkoff = st.selectbox("I want to mark new status of...", myhabits)
    check_off_time = st.radio(
        "Check off time:", ["Now", "Custom"], key="check_off_time"
    )

    if check_off_time == "Now":
        time = now.strftime("%Y-%m-%d %H:%M")

    elif check_off_time == "Custom":
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            years = list(range(now.year - 2, now.year + 3))
            year = st.selectbox("Year", years, index=years.index(now.year))
        with col2:
            months = list(range(1, 13))
            month = st.selectbox("Month", months, index=months.index(now.month))
        with col3:
            if month == 2:
                days = list(range(1, 30))
                day = st.selectbox("Day", days, index=days.index(now.day))
            elif month in [1, 3, 5, 7, 8, 10, 12]:
                days = list(range(1, 32))
                day = st.selectbox("Day", days, index=days.index(now.day))
            elif month in [4, 6, 9, 11]:
                days = list(range(1, 31))
                day = st.selectbox("Day", days, index=days.index(now.day))
        with col4:
            hours = list(range(0, 24))
            hour = st.selectbox("Hour", hours, index=hours.index(now.hour))
        with col5:
            minutes = list(range(0, 60))
            minute = st.selectbox("Minute", minutes, index=minutes.index(now.minute))

        time = datetime(year, month, day, hour, minute).strftime("%Y-%m-%d %H:%M")

    check_off_status = st.selectbox("Status:", ("Done!", "Skip.", "Missed."))

    if st.button("Submit"):
        tracker.checkoff(
            habit_name=habit_to_checkoff, date=time, status=check_off_status
        )
        st.success(
            f"New status submitted: **{habit_to_checkoff}** at **{time}**: {check_off_status}"
        )

elif page == "Analysis":
    st.header("Habit Report")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Overview", "Habit details", "Day View", "Week View", "Month View"]
    )

    # Overview
    with tab1:
        selected_habit = st.selectbox(
            "Choose periodicity",
            ["All habits", "Daily habits", "Weekly habits", "Monthly habits"],
        )
        if selected_habit == "All habits":
            if myhabits is not None:
                st.write(", ".join(myhabits))
        elif selected_habit == "Daily habits":
            daily_habits = analysis.habit_list_by_frequency("day")
            if daily_habits is not None:
                st.write(", ".join(daily_habits))
        elif selected_habit == "Weekly habits":
            weekly_habits = analysis.habit_list_by_frequency("week")
            if weekly_habits is not None:
                st.write(", ".join(weekly_habits))
        elif selected_habit == "Monthly habits":
            monthly_habits = analysis.habit_list_by_frequency("month")
            if monthly_habits is not None:
                st.write(", ".join(monthly_habits))

    # Show details of the specific habit
    with tab2:
        # st.write("Current habits:", myhabits)
        if "habit_visible" not in st.session_state:
            st.session_state.habit_visible = True

        selected_habit = st.selectbox("Habit: ", myhabits)

        col1, col2 = st.columns([3, 1])

        st.session_state.habit_visible = True
        if st.session_state.habit_visible:
            with col1:
                st.subheader(selected_habit)

                habit = Habit(st.session_state.db_file, selected_habit)
                habit_name = habit.habit_name
                if habit_name is not None:  # and success_rate is not None:
                    success_rate = analysis.calculate_successrate(selected_habit)
                    st.write(f"Description: {habit.description}")
                    st.write(f"Start date: {habit.start_date}")
                    st.write(f"Frequency: {habit.frequency}")
                    st.write(f"Longest streak: {habit.longest_streak}")
                    st.write(f"Current streak: {habit.current_streak}")
                    st.write(f"Success rate: {success_rate * 100:.2f}%")
                    df = pd.DataFrame(habit.log, columns=["Date", "Status"])
                    st.dataframe(df)
                else:
                    st.warning("No data.")

            with col2:
                with st.popover("Delete this habit"):
                    st.warning("Are you sure to delete this habit and all its records?")
                    if st.button("Yes, delete the habit"):
                        if selected_habit is not None:
                            tracker.delete_habit(selected_habit)
                        # st.success(f"Successfully deleted habit {selected_habit}!")
                        st.session_state.habit_visible = False
                        st.rerun()

    # Daily View: data in the specific date
    with tab3:
        selected_date = st.date_input("Date", "today")
        habit_data = analysis.habit_data_in_selected_period(selected_date)[0]
        column_names = analysis.habit_data_in_selected_period(selected_date)[1]

        if habit_data is not None:
            df = pd.DataFrame(habit_data, columns=column_names)
            st.dataframe(df)
        else:
            st.warning("No record on the selected date!")

    # Weekly View: data in the specific week
    with tab4:
        selected_date_in_week = st.date_input("Choose a date of interest week", "today")
        first_day_of_week = selected_date_in_week - timedelta(
            days=selected_date_in_week.weekday()
        )
        habit_data = analysis.habit_data_in_selected_period(first_day_of_week, True)[0]
        column_names = analysis.habit_data_in_selected_period(first_day_of_week, True)[
            1
        ]

        if habit_data is not None:
            df = pd.DataFrame(habit_data, columns=column_names)
            st.dataframe(df)
        else:
            st.warning("No record in the selected week!")

    # Month View: data in the specific month
    with tab5:
        years = list(range(now.year - 2, now.year + 3))
        selected_year = st.selectbox("Year", years, index=years.index(now.year))
        months = list(range(1, 13))
        selected_month = st.selectbox("Month", months, index=months.index(now.month))
        time = str(selected_year) + "-" + f"{selected_month:02}"
        habit_data = analysis.habit_data_in_selected_period(time)[0]
        column_names = analysis.habit_data_in_selected_period(time)[1]

        if habit_data is not None:
            df = pd.DataFrame(habit_data, columns=column_names)
            st.dataframe(df)
        else:
            st.warning("No record in the selected month!")
