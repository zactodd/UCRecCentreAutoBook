# AutoBook

## Warning: Current implmentation will rebook cancelled classes.

[![Book Todays Classes](https://github.com/zactodd/UCRecCentreAutoBook/actions/workflows/auto_book.yml/badge.svg)](https://github.com/zactodd/UCRecCentreAutoBook/actions/workflows/auto_book.yml)
## Edit Classes
You can change classes by editing the json file auto_book/classes_to_book.json
```json
{
  "day1": [
        {"class": "class1 name", "time": "class1 time1"},
        {"class": "class2 name", "time": "class2 time2"}
      ]
}
```
The day must be lowercase, the class must be written the same as it is written in the app on website including spaces and spial chaters, the time is in 24 hour time.

For example:
```json
{
  "monday": [
      {"class": "Zumba", "time": "17:10:00"},
      {"class": "Pump", "time": "18:10:00"}
    ],
  "tuesday": [
      {"class": "FIT50", "time": "12:05:00"},
      {"class": "Run Canterbury", "time": "17:10:00"},
      {"class": "Zumba", "time": "17:10:00"}
    ]
}
 ```

Class can also be booked by replacing the time with a time named time such as 'morning'.
Below is are the named times with there upper an lower bounds.
```
{
    'morning': ('05:30:00', '12:00:00'),
    'afternoon': ('12:00:00', '18:30:00'),
    'evening': ('18:30:00', '23:59:59'),
    'early morning': ('5:30:00', '8:30:00'),
    'late morning': ('8:30:00', '12:00:00'),
    'midday': ('11:00:00', '13:00:00'),
    'early afternoon': ('12:00:00', '15:30:00'),
    'late afternoon': ('15:30:00', '18:30:00'),
    'early evening': ('18:30:00', '21:00:00'),
    'late evening': ('21:00:00', '23:59:59')
}
```

Updating our previous class file with named times would result in the following:
```json
{
  "monday": [
      {"class": "Zumba", "time": "late afternoon"},
      {"class": "Pump", "time": "late afternoon"}
    ],
  "tuesday": [
      {"class": "FIT50", "time": "midday"},
      {"class": "Run Canterbury", "time": "late afternoon"},
      {"class": "Zumba", "time": "late afternoon"}
    ]
}
 ```

# Script Automation
## Github Actions
First fork the repository.

Then you will need to setup 'secrets' for your username and password.
- Go to the repository settings
- Select 'secrets.
- Select 'add new repository secret'. 
- Create a secret for your username titled 'USERNAME' and a secret for your password named 'PASSWORD'.

The current action script will work the same as running the code below locally
```bash
python auto_book USERNAME PASSWORD
```

## Calendar
The script generates an up-to-date iCalendar file which includes all classes booked by the UCRecCentreAutoBook script. You can subscribe to this feed (in Google Calendar or other) by using the url:

```
https://raw.githubusercontent.com/<github-username>/UCRecCentreAutoBook/main/auto_book/.gym_calendar.ics
```

It is enabled by using the 'calendar_notification' paramter when running the script. For example:
```bash
python auto_book USERNAME PASSWORD --calendar_notification 
```
