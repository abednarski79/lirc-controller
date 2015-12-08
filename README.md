# lirc-controller
Double click extension for lirc

## Introduction:
The aim of the project is to create wrapper for the LIRC remote daemon functionality to allow intercepting and executing scripts / python code on double click and hold event from the remote controller. Standard Linux remote controller daemon LIRC does not allows for intercepting any other event then signle click.

## Current status
This project is not fully finished. Code works but should be probably properly refactored. Main change which I would like to introduce remove dependency on the LIRC deamon during the tests.

## Configuration
Number of configuration files, from the most basic ones to the fully covering all required functionalities are stored in 2 folders:

- *./resources/configuration/dev* - contains configuration files used during the development, it represents simplified set of features easy to debug and change
- *./resources/configuration/prod* - these are 5 sets of configuration, from the most basic one called "basic", more advanced called "advanced", to "menu" and finally "full" and "full_2" which contains all the features that I wanted to use to control mpd daemon

## Running the wrapper
In the folder *./resources/scripts/* there are 2 folders containing scripts which are used to star the wrapper, *dev* contains scripts starting wrapper in development mode, and *prod* contains number of scripts starting wrapper with different number of functionalities enabled.

## Configuration
There are 3 categories of files which are used to configure wrapper. They are read just once at the start of the wrapper. File categories: lirc configuration file CFG - format of this file is exactly this same as the standard LIRC remote configuration file (please refer to LIRC man or web page). The important part of this file allowing wrapper to interact with LIRC is the string in *config* part of the file, this is later used in XML file bellow wrapper configuration file XML - this file contains wrapper specific configuration, file is separated on 2 sections, general configuration:
```
<?xml version="1.0"?>
<configuration>
...
        <properties>
                <property id="blocking">0</property>
                <property id="gapDuration">10</property>
        </properties>
...
```
this part is responsible for general wrapper settings. Another section contains configuration for each button:
```
...
        <buttons>
...
                <button id="PLUS_ID">
                        <action id="VOLUME_UP" type="CLICK">
                                <task>
                                        <module>main.controller.shell.shell_controller</module>
                                        <class>ShellController</class>
                                        <method>executeCommand</method>
                                        <parameter>sh /root/scripts/mpd_v2/commands/volumeUp/volumeUp_v2.sh</parameter>
                                </task>
                                <isCancelable>False</isCancelable>
                        </action>
                </button>
...
```
the link between the lirc configuration file and wrapper file is the button *id*.

Each button can have up to 3 actions marked with unique "type" value, possible values are:
- "CLICK" - task will be executed when "single click" event will be received by LIRC daemon
- "DOUBLE_CLICK" - same as above but LIRC needs to receive two click on this same button in short period of time
- "HOLD" - same as above but LIRC needs to receive more then 2 click on this same button

In each action contains task, each task describes python class which will be executed. If "isCancelable" is set to "True" and LIRC will received another action for this same button id then task will be not executed. For example if button VOLUME_UP was clicked once and short after that LIRC will intercept another click for this button wrapper will treat it as double click and execution of the single click taks will never happen, instead task linked with double click event will be run.

## Implementation details
The code of the wrapper runs in 3 separated threads:
- generator - it's task is just to retrieve the signals from LIRC daemon and store them in generator queue, this queue contains information which button was clicked and how many times it was repeated
- processor - listens on the new elements in the generator queue, process them using configuration and based on this information stores tasks (click / double click / hold) to be executed in worker queue
- worker - listens on the new elements in the worker queue and each time new item is found starts new thread in which task is being executed

Above approach allows on executing tasks even if their run time is relatively long in comparation with the process of intercepting click, double click and hold events.

Logs are stored in 3 separated log files reflecting action of the 3 threads above.

## TODO
Currently all actions which can run from wrapper are executed using bash scripts, this is not very efficient and wrapper has option in configuration to use python class instead of scripts, those classes are pre-loaded at the start of the application, each class is loaded only once and are cached. As result calling functions from remote using python classes rather then bash scripts should be more efficient. This project does not have to be used in conjunction with MPD daemon and could be used for any type of task in as universal way as LIRC is currently used (for example to control tv card).

## Emulating remote controller events

To test software dependent on signals coming from LIRC daemon without having physical remote receiver LIRC daemon needs to be run in the mode that allows to simulate signals, there are 2 options to do that:

- kill currently running daemon:

> service lirc stop

- run daemon from command line:

> lircd --nodaemon --allow-simulate /etc/lirc/lircrc

OR

edit file:

> /etc/lirc/hardware.conf

and change line containing LIRCD_ARGS to: 

> LIRCD_ARGS="--allow-simulate"
  

- restart LIRC daemon

> service lirc restart

After introducing those changes scripts methods for simulating LIRC events can be used: 
```
./resources/script/dev/simulate-lirc_FORWARD-CLICK.sh
./resources/script/dev/simulate-lirc_FORWARD-DOUBLE_CLICK.sh
 ./resources/script/dev/simulate-lirc_FORWARD-HOLD-x5.sh
 ./resources/script/dev/simulate-lirc_MENU-CLICK.sh
 ./resources/script/dev/simulate-lirc_MINUS-CLICK.sh
 ./resources/script/dev/simulate-lirc_MINUS-DOUBLE_CLICK.sh
 ./resources/script/dev/simulate-lirc_MINUS-HOLD-x5.sh
 ./resources/script/dev/simulate-lirc_PLAY-CLICK.sh
 ./resources/script/dev/simulate-lirc_PLUS-CLICK.sh
 ./resources/script/dev/simulate-lirc_PLUS-DOUBLE_CLICK.sh
 ./resources/script/dev/simulate-lirc_PLUS-HOLD-x5.sh
 ./resources/script/dev/simulate-lirc_REVERSE-CLICK.sh
 ./resources/script/dev/simulate-lirc_REVERSE-DOUBLE_CLICK.sh
 ./resources/script/dev/simulate-lirc_REVERSE-HOLD-x5.sh
 ```
 
Above commands are suitable for Apple remote. 
To create scripts for your remote you need to have actual remote receiver and LIRC daemon configured and running :

- run command:

> irw

- click button for which you would like to create script
- copy output of the command to your script
Next time you will be able to generate LIRC event on your development environment without have physical remote receiver.

## Useful commands.
During development following commands were very useful:

- sending termination SIGTERM signal to the main application thread

>  ps -aef | grep python | grep conf

- find the one with lowest PID number (main thread) and use it to send termination signal 

> kill -s TERM <MAIN_THREAD_PID>  

Also source contains number of utility commands:

- ./resources/script/dev/run-app.sh - runs application with development version of configuration files
- ./resources/script/dev/simulate-lirc_NNN-MMM.sh - generates LIRC event, more details in section "Emulating remote controller events"
- ./resources/script/prod/run-app_basic.sh - runs application with most basic configuration (single click events only)
- ./resources/script/prod/run-app_advanced.sh - runs application with more advanced configuration (double click events added)
- ./resources/script/prod/run-app_full.sh - runs application with full configuration (hold events added)
- ./resources/script/prod/run-app_menu.sh - runs application with support for menu functionality (switching sets of commands)
- ./resources/script/prod/run-app_full_2.sh - runs application with full configuration as it will be run in production server
- ./resources/script/prod/lirc-controller.sh - init script for Debian system

## Links
- [LIRC daemon](http://www.lirc.org/)
- [great explanation how select.select works in Python](http://pymotw.com/2/select/index.html#module-select)
