# Setup
Download or clone repo then running the program in terminal with.
```bash
python auto_book/main.py
```
Input your username (Email) and password for the reccentre when requested.


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
 
 Note currently the program reads the classes to book at the start of the program so you will have to restart if you want to change them after running.
