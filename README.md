[![Book Todays Classes](https://github.com/zactodd/UCRecCentreAutoBook/actions/workflows/auto_book.yml/badge.svg)](https://github.com/zactodd/UCRecCentreAutoBook/actions/workflows/auto_book.yml)
# Edit Classes
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
python auto_book USERNAME PASSWORD --random_delay
```
