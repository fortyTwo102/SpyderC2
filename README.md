**This is the beginning of a python based C2 framework**

## Initial Goal
- Have a python based stager which when executed on windows will give out the current directory information.
- Have a python based http listener, which will print the information


## Current Condition
- Previously
	- Running the program will make a stager exe, start a server. The actual files in the directory where the stager.exe is run will be passed to the C2 server.
	- The flask server now runs as a separate process and the server is killed whenever the main script exits.
	- The stager now beacons continuously for commands, when commands given it sends all files in current directory
	- Added mongodb for communication between server and main script.
	- Victim now sends identifier as b64 cookie, server stores in  victims collection.

- 08.08.2021
	- Now victim goes through staging phase, where it gives OS info(STAGE-0) to server
	- In stage 0, server responds with 200 OK menaing successful staging, 302 meaning Victim already registered and 400 for bad request. If 200 OK recieved then it will move on to beaconing
	- Server UI now has use command to interact with a victim, where new victim specific commands can be issued
	- Added info command for victim to show the victim ID and OS info.

- 13.08.2021
	- Now the victim has a last seen and a DEAD or alive status shown with the info command.
	- The time after which victim is considered dead is 60 secs

- 12.09.2021
	- Added modules for powershell and python browser_history and screenshot
	- Linux screenshot and windows browser history works right now.


## Add these
- Status of victim whether dead or alive
- Show on main screen, new victim has joined
- Cant send commands if dead
- Kill victim
- Funny names of victims
- Logs of commands/ Proper logging system
- Modules to be modular. Plug and play
- Use victim to be called with first few letters of victim ID
- Last used command/Proper console for interaction
- Idenitfication of admin privelges