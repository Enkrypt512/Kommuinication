# Kommuinication
Minimalist End-To-End Python-Based Encrypted Chat
# How to run
Firstly,you need Python 3+ Installed on your system,then download the files and open a terminal where you extracted the files,then run ``python -m venv .venv``,then depending on your operating system (OS) either run ``source .venv/bin/activate`` for MacOS/Linux and in Windows,you either run ``.venv\Scripts\activate.bat`` if your using CMD/Command promt or run `` .venv\Scripts\Activate.ps1`` if your using Powershell,then run ``pip install cryptography``,if you want to run a server to host Kommuinication (Note:servers are only for local network currently,if you want it to be on the internet,you can probably port forward or something the IP with something like cloudflared and modify the client.py so it recieves the stuff from that IP,keep that in mind) run ``python server.py``,and if you want to connect to a Kommuinications server,run ``python client.py yourusernamehere``
# Limitations
- The server is only hosted in your local network
- Anybody can impersonate anybody by just changing their username
- Kommuinications is a Group chat/server based chat,so there isnt any DM's like in discord
