# Introduction 

prodman (short for Productivity Manager) is a time management tool I created to optimize my own productivity and minimize procrastination. I use it to plan, track, and analyze my time and my habits. Additionally, prodman incorporates mechanisms to minimize devation from my planned schedule (*hassler*), and provide positive reinforcements for sticking to my planned schedule (*applause*).

In some sense, it can be thought of as a Pomodoro technique (https://en.wikipedia.org/wiki/Pomodoro_Technique) timer on (a lot of) steroids. prodman is written entirely in Python; its visualization features rely heavily on Dash (https://plotly.com/dash/), but it has a fully functional commandline interface that may be utilized without the graphical features. Since I primarily work on a Mac, prodman's vocal cues are written for OS X - but may easily be adapted to other operating systems. 

# Usage:

## GUI:
### Tracker
This is where most of the user's time will be spent. The Tracker gives the user cues about what task/focus to concentrate on at a given time, based on a schedule that the user has built under the Schedule tab, and deployed. The Tracker contains numerical analytics updated every second, and graphical analytics updated every 10 seconds. 

*Pause* will pause the session. 

*Next* will jump to the next block without finishing current one.

*Finish* will end the session. 

*Record Session* will save the session for historical analysis under the History tab)

[Tracker gif](https://github.com/cyrusmaz/prodman/blob/master/gifs/session.gif)

### Schedule
#### Schedule: Custom
This is where the user designs an individual session, allocating specific amounts of time to specific tasks, with specific foci. I will refer to each row as a 'block' henceforth. 

*Task* (mandatory): choose from dropdown menu. Will be read out loud by the tracker. 

*Length* (mandatory): positive numerical value (in minutes)

*Focus* (optional): will be read out loud by the tracker. 

*Notes* (optional): will NOT be read out loud by the tracker.

Setting *Hassler* to 'Yes' for a block will incessantly prompt the user to type in a command before starting the block. This feature is designed so as to minimize deviations from schedule. 

Setting *Applause* to 'Yes' for a block will applaud the user after the end of the block.

Setting *Dinger* to a numerical value will play a ding sound effect at regular intervals of the numerical value (in minutes). Note that if for a given block *Dinger* > *Length*, no ding sound effect will be played. 

The user may deploy a schedule to the Tracker or save it to Templates for later user/editing.

[Schedule: Custom gif](https://github.com/cyrusmaz/prodman/blob/master/gifs/custom_sched.gif)

[Deploy Schedule gif](https://github.com/cyrusmaz/prodman/blob/master/gifs/deploy_sched.gif)

#### Schedule: Templates
Saved schedules (a.k.a. templates) may be deployed to Tracker or edited under the Schedule: Custom tab. 

[Schedule: Templates gif](https://github.com/cyrusmaz/prodman/blob/master/gifs/template.gif)

#### Schedule: Multi-Template Analysis
Under this tab the user may plan for several sessions. The user is provided with several numerical and graphical analytics tools that aggregate the task/focus/time allocations for multiple templates.

[Schedule: Multi-Template Analysis gif](https://github.com/cyrusmaz/prodman/blob/master/gifs/multi_temp.gif)

### History
This is where the user can view analyze saved sessions. The user may choose to analyze an individual session, or multiple sessions. Various numerical and graphical analytics tools are provided. 

[History: Individual gif](https://github.com/cyrusmaz/prodman/blob/master/gifs/history_individual.gif)

[History: Multiple gif](https://github.com/cyrusmaz/prodman/blob/master/gifs/history_multi.gif)

## Command-line:
TODO

# File Structure
1. PM_config.py
1. PM_main.py
1. PM_backend.py
1. PM_db_init.py
1. applaud.aiff
1. glass.aiff

**PM_config.py** contains the configuration parameters. The following paths **must** be set by the user: 
- applause_sound_location 
- ding_sound_location 
- database_location

**PM_main.py** contains the front-end of the application. 

**PM_backend.py** contains the backend functionality of the application including keeping track of schedule/user progress, as well as interacting with the database. PM_backend.py may be used independently of the front-end visualization/analytics features. 

**PM_db_init.py** contains the code to initialize the database for the application. Only needs to be run once. 

**applaud.aiff** is the applaud sound effect. Replace with your own sound effect if desired.

**glass.aiff** is the ding sound effect. Replace with your own sound effect if desired.

# Installation
prodman is written entirely in Python. Furthermore, prodman stores historical records and saved templates on a Postgres server in a Docker container. Thus, using prodman requires the Python interpreter (I use 3.7) and several dependencies, as well as Docker and Postgres. 

### Python & Dependencies
Install Python: https://www.python.org/downloads/

Install the Python dependencies: (numpy, pandas, plotly, dash, matplotplib, sqlalchemy, psycopg2)

Installing *psycopg2* will require an installation of *postgresql* first, which is a little tricky on OS X, but Homebrew (https://brew.sh/) has made it convenient. 

To install Homebrew, type the following in Terminal:

> /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

Once, you have Homebrew, install *postgresql* by typing the following in Terminal:

> brew install postgresql

Then, proceed to install *psycopg2* in Terminal:

> pip3 install psycopg2)

### Docker
Install Docker: https://docs.docker.com/docker-for-mac/install/

Then, install Postgres for Docker, by typing the following in Terminal:

> docker pull postgres

### Configuring PM_config.py
Set **database_location** to be equal to the path where you want your prodman database to be stored. If the directory does not exist, the database initialization script (PM_db_init.py) will create it. 

Set **applause_sound_location** to be equal to the path where applause.aiff (or an applause sound file of your choice) is stored.
Set **ding_sound_location** to be equal to the path where glass.aiff (or a ding sound effect file of your choice) is stored.

### Database Initialization
First, double check that **database_location** is set to your liking. See above for details.

In Terminal, traverse to where *PM_db_init.py* is saved, and type the following: 

> python3 PM_db_init.py

You will get an error the first time you run the script because it both starts a Postgres server in a Docker container, AND initializes the database; moreover firing up the Docker container takes a bit of time, and the initialization cannot take place until the Postgres server is fully fired up in the container. Hence, wait a minute or so and run the same command again. If you encounter the same error, wait a few moments and try again. Once the command runs without error, you are all set!

# Starting Up The Application

### In Terminal:

In Terminal, traverse to where *PM_main.py* is saved, and type the following: 

> python3 PM_main.py

then copy the link that it provides (default is: http://127.0.0.1:8080/), and paste it in your browser. Et voilà!

### As Clickable Bash Script:
Edit *prodman_startup* so that the path to *PM_main.py* is correct. Then, make the bash script exectutable by typing the following in Terminal: 

>chmod 755 /path/to/prodman_startup

The steps above need to be completed only once. 

Now you may click *prodman_startup*, copy the link that it provides (default is: http://127.0.0.1:8080/), and paste it in your browser. Et voilà!

# Caveats
Currently, unable to jump to next block while paused. 

Currently, the docker container continues to run even after prodman has been exited. 

# Acknowledgement
This application was inspired by the works of James Clear (https://jamesclear.com/habit-tracker) and Scott Young (https://www.scotthyoung.com/blog/ultralearning). 
