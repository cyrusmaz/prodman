# Introduction 

prodman is a time management tool I wrote to optimize my own productivity. In some sense, it can be thought of as a Pomodoro technique (https://en.wikipedia.org/wiki/Pomodoro_Technique) timer on steroids. prodman is written entirely in Python; its visualization features rely heavily on dash (https://plotly.com/dash/), but it has a fully functional commandline interface. Since I primarily work on a Mac, prodman's vocal cues are written for OS X - but can easily be adapted to other operating systems. 

# Usage:

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

# Installation

# Caveats
