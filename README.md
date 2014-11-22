JobClockBot
===========

Python/Twisted bot for tracking time spent on tasks/jobs

Installation
------------

1. Install Python 2.7
2. Install Virtualenv
3. `git clone https://github.com/blha303/JobClockBot`
4. `cd JobClockBot; virtualenv env`
5. `env/bin/pip install -r requirements.txt`
6. `cp config.yml.sample config.yml; vim config.yml` and edit to your needs
7. `env/bin/twistd -y run.py`
