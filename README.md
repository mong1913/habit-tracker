<h1 align="center"> Habit Tracker App </h1>

## Introduction
A personal habit tracker app based on Python.
It helps users to create habits, log activities and track completion rate.

## Features
- **Habit Management:** Add new habits and delete unwanted habits. Support daily, weekly and monthly habits. <br>
- **Activity Logging:** Check off habits and mark the status as "done", "skip" or "missed" at anytime. <br>
- **Data Analytics:** Calculate the current streak, the longest streak and completion rate of habits. <br>
- **Web UI:** Graphical user interface based on Streamlit makes the app intuitive and user friendly. <br>
- **Data Storage:** Storage user habit data in SQLite for tracking and analysis. <br>
- **Predefined Data:** About four weeks of predefined data can be loaded to familiarize users with the application. <br>

## Running the app locally
**1. Install Python and Git if you don't have them**

**2. Clone the Repository**
```sh
git clone https://github.com/mong1913/habit-tracker.git
```

**3. Navigate to the App Directory**

**4. Create a Virtual Environment (Optional)**
```sh
python -m venv venv
source venv/bin/activate
```

**5. Install dependencies**
```sh
pip install -r requirements.txt
```

**6. Run the Streamlit App**
```sh
streamlit run app.py
```

## Usage
**1. Create a new habit** <br>
&nbsp;&nbsp;&nbsp;&nbsp;Users can add a new habit in the page "Add Habit". <br>
&nbsp;&nbsp;&nbsp;&nbsp;After putting the habit name, the description and the frequency, users press "Submit" button to add the habit into the database.

**2. Check off the habit** <br>
&nbsp;&nbsp;&nbsp;&nbsp;In the page "Check Off Habits", users can mark status of a habit. <br>
&nbsp;&nbsp;&nbsp;&nbsp;There are three modes for the status: "Done!", "Skip.", and "Missed." <br>
&nbsp;&nbsp;&nbsp;&nbsp;Habits can be check off at anytime, even at the time in the pass. <br>
&nbsp;&nbsp;&nbsp;&nbsp;Press the button "Submit" to send the record to the database.

**3. View habit report and data analysis** <br>
&nbsp;&nbsp;&nbsp;&nbsp;There are five tabs in the page "Analysis".
- Overview: Highlights of all habits and the habits with the same frequency. <br>
- Habit details: Details can event logs can be seen for the chosen habit. Users can also delete the habit in this tab. <br>
- Day View: All records on the specific date are shown. <br>
- Week View: All records in the specific week of the chosen date are displayed here. <br>
- Month View: All records in the specific year and month are displayed in this tab. <br>

https://github.com/user-attachments/assets/ecd5dc93-b643-45f7-8e9e-fdfb67b1f750
