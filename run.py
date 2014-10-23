from twisted.internet import reactor, task, defer, protocol
from twisted.python import log
from twisted.words.protocols import irc
from twisted.application import internet, service

import yaml, sys, datetime, ago, json

with open('config.yml') as f:
    config = yaml.load(f.read())
HOST, PORT = config['host'], config['port']

tasks = {}
archive = []

def say(info, msg):
    info["msg"](info["channel"], msg)
    log.msg("{}: {}".format(info["channel"], msg))

def u_clockin(info, msg):
    global tasks
    if info["nick"] in tasks:
        say(info, "Clocking out of existing task first" + (": " + msg if msg else ""))
        u_clockout(info, msg)
    tasks[info["nick"]] = {"nickname": info["nick"], "summary": (" for " + msg if msg else ""), "timestarted": datetime.datetime.now()}
    say(info, info["nick"] + " has clocked in successfully" + (" for " + msg if msg else ""))

def u_clockout(info, msg):
    global tasks
    global archive
    if not info["nick"] in tasks:
        say(info, "You aren't clocked in!")
    else:
        tasks[info["nick"]]["timestopped"] = datetime.datetime.now();
        tasks[info["nick"]]["duration"] = ago.human(tasks[info["nick"]]["timestopped"] - tasks[info["nick"]]["timestarted"], past_tense='{}', future_tense='{}')
        say(info, "{nickname} has clocked out{summary}. Time spent: {duration}".format(**tasks[info["nick"]]))
        tasks[info["nick"]]["timestarted"] = tasks[info["nick"]]["timestarted"].ctime()
        tasks[info["nick"]]["timestopped"] = tasks[info["nick"]]["timestopped"].ctime()
        archive.append(tasks[info["nick"]])
        with open("archive.json", "w") as f:
            json.dump(archive, f)
        del tasks[info["nick"]]

class JobClockProtocol(irc.IRCClient):
    nickname = config['nick']
    password = config['password'] if 'password' in config else None
    username = config['nick']
    versionName = "JobClock"
    versionNum = "v0.0.1"
    realname = config['nick'] + " https://github.com/blha303/JobClockBot"
    global archive
    try:
        with open("archive.json") as f:
            archive = json.load(f)
    except:
        archive = []

    def signedOn(self):
        if "nickserv" in config:
            self.msg("NickServ", "identify {}".format(config["nickserv"]))
        for channel in self.factory.channels:
            self.join(channel)

    def privmsg(self, user, channel, message):
        nick, _, host = user.partition('!')
        if not channel in self.factory.channels:
            return
#        log.msg("{} <{}> {}".format(channel, nick, message))
        if message[0][0] == "!":
            message = message.strip().split(" ")
            msginfo = {'nick': nick, 'host': host, 'channel': channel, 'message': message, 'notice': self.notice, 'msg': self.msg}
            if channel == self.nickname:
                channel = nick
            try:
                log.msg("{} used {}".format(nick, " ".join(message)))
                globals()["u_" + message[0][1:]](msginfo, " ".join(message[1:]) if len(message) > 1 else "")
            except KeyError:
                log.msg("Command not found, probably for another bot")

class JobClockFactory(protocol.ReconnectingClientFactory):
    protocol = JobClockProtocol
    channels = config["channels"]

if __name__ == '__main__':
    reactor.connectTCP(HOST, PORT, JobClockFactory())
    log.startLogging(sys.stdout)
    reactor.run()

elif __name__ == '__builtin__':
    application = service.Application('JobClock')
    ircService = internet.TCPClient(HOST, PORT, JobClockFactory())
    ircService.setServiceParent(application)
