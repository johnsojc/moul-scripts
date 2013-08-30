# -*- coding: utf-8 -*-
""" *==LICENSE==*

CyanWorlds.com Engine - MMOG client, server and tools
Copyright (C) 2011  Cyan Worlds, Inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Additional permissions under GNU GPL version 3 section 7

If you modify this Program, or any covered work, by linking or
combining it with any of RAD Game Tools Bink SDK, Autodesk 3ds Max SDK,
NVIDIA PhysX SDK, Microsoft DirectX SDK, OpenSSL library, Independent
JPEG Group JPEG library, Microsoft Windows Media SDK, or Apple QuickTime SDK
(or a modified version of those libraries),
containing parts covered by the terms of the Bink SDK EULA, 3ds Max EULA,
PhysX SDK EULA, DirectX SDK EULA, OpenSSL and SSLeay licenses, IJG
JPEG Library README, Windows Media SDK EULA, or QuickTime SDK EULA, the
licensors of this Program grant you additional
permission to convey the resulting work. Corresponding Source for a
non-source form of such a combination shall include the source code for
the parts of OpenSSL and IJG JPEG Library used as well as that of the covered
work.

You can contact Cyan Worlds, Inc. by email legal@cyan.com
 or by snail mail at:
      Cyan Worlds, Inc.
      14617 N Newport Hwy
      Mead, WA   99021

 *==LICENSE==* """
"""
Module: nglnTreeMonkey
Age: Negilahn
Date: December 2003
Author: Doug McBride
HaX0r3d: Derek Odell
Controls the appearance and behavior of the Negilahn Tree Monkey
"""

from Plasma import *
from PlasmaTypes import *
import random

# define the attributes that will be entered in max
respSpawnPt = ptAttribResponder(1, "resp: Spawn Point", ['0', '1', '2'], netForce=1)
respMonkeyAct = ptAttribResponder(2, "resp: Monkey Actions", ['Alarmed', 'Up', 'Eat', 'Idle', 'Vocalize'])
respMonkeySfx = ptAttribNamedResponder(3, "resp: Monkey SFX", ['Alarmed', 'Up', 'Eat', 'Idle', 'Off', 'Vocalize'], netForce=1)
respMonkeyOff = ptAttribResponder(4, "resp: Monkey Off")

# define globals
kDayLengthInSeconds = 56585  # Length of a Negilahn day in seconds Must match value in Negilahn.age file
kMinimumTimeBetweenSpawns = 300  # 5 minutes
kMaximumTimeBetweenSpawns = 18000  # 5 hours

# Chance in 100 that monkey will:
IdlePct = 30
EatPct = 20
VocalizePct = 20
AlarmedPct = 10
OffPct = 20
stackList = []

#====================================


class nglnTreeMonkey(ptResponder):
    ###########################
    def __init__(self):
        ptResponder.__init__(self)
        self.id = 5241
        version = 3
        minor = 0
        self.version = "{}.{}".format(version, minor)
        PtDebugPrint("__init__: nglnTreeMonkey v{}".format(self.version))
        random.seed()

    ###########################
    def OnServerInitComplete(self):
        try:
            ageSDL = PtGetAgeSDL()
        except:
            PtDebugPrint("nglnTreeMonkey.OnServerInitComplete():  ERROR: Cannot find the Negilahn Age SDL")
            self.InitNewSDLVars()

        ageSDL.sendToClients("MonkeyLastUpdated")
        ageSDL.sendToClients("MonkeySpawnTimes")
        ageSDL.setFlags("MonkeyLastUpdated", 1, 1)
        ageSDL.setFlags("MonkeySpawnTimes", 1, 1)
        ageSDL.setNotify(self.key, "MonkeyLastUpdated", 0.0)
        ageSDL.setNotify(self.key, "MonkeySpawnTimes", 0.0)

        thisDay = int(PtGetDniTime() / kDayLengthInSeconds)
        lastDay = int(ageSDL["MonkeyLastUpdated"][0] / kDayLengthInSeconds)

        if (thisDay - lastDay) > 0:
            PtDebugPrint("nglnTreeMonkey.OnServerInitComplete():  It's been at least a day since the last update, running new numbers now.")
            self.InitNewSDLVars()
        else:
            PtDebugPrint("nglnTreeMonkey.OnServerInitComplete():  It's been less than a day since the last update, doing nothing")
            self.SetMonkeyTimers()

        if not len(PtGetPlayerList()):
            respMonkeyOff.run(self.key, fastforward=1)

    ###########################
    def OnSDLNotify(self, VARname, SDLname, playerID, tag):
        if VARname == "MonkeySpawnTimes":
            self.SetMonkeyTimers()

    ###########################
    def OnNotify(self, state, id, events):
        global stackList
        PtDebugPrint("nglnTreeMonkey.OnNotify():  state={:f} id={} events={}".format(state, id, events))

        if id == (-1):
            PtDebugPrint("nglnTreeMonkey.OnNotify():  Need to store event: {}".format(events[0][1]))
            stackList.append(events[0][1])
            PtDebugPrint("nglnTreeMonkey.OnNotify():  New list is: {}".format(stackList))
            if len(stackList) == 1:
                PtDebugPrint("nglnTreeMonkey.OnNotify():  List is only one command long, so I'm playing it")
                code = stackList[0]
                PtDebugPrint("nglnTreeMonkey.OnNotify():  - Playing command: {}".format(code))
                self.ExecCode(code)

        elif id == respMonkeyAct.id and self.sceneobject.isLocallyOwned():
            PtDebugPrint("nglnTreeMonkey.OnNotify():  Callback was from responder, and I own the age, so Logic Time")
            old = stackList.pop(0)
            PtDebugPrint("\tPopping off: {}".format(old))
            self.RandomBehavior()

        elif id == respMonkeyOff.id and self.sceneobject.isLocallyOwned():
            PtDebugPrint("nglnTreeMonkey.OnNotify():  Callback was from 'Off' responder")
            old = stackList.pop(0)
            PtDebugPrint("\tPopping off: {}".format(old))

        elif (id == respMonkeyAct.id or id == respMonkeyOff.id) and not self.sceneobject.isLocallyOwned():
            PtDebugPrint("nglnTreeMonkey.OnNotify():  Callback was from responder, and I DON'T own the age, so I'll try playing the next item in list")
            old = stackList.pop(0)
            PtDebugPrint("\tPopping off: {}".format(old))
            if len(stackList):
                PtDebugPrint("\tList has at least one item ready to play")
                code = stackList[0]
                PtDebugPrint("\tPlaying command: {}".format(code))
                self.ExecCode(code)

        else:
            PtDebugPrint("nglnTreeMonkey.OnNotify():  Callback from something else?")

    ###########################
    def RandomBehavior(self):
        ageSDL = PtGetAgeSDL()
        PickABehavior = random.randint(1, 100)
        LightsOn = ageSDL["nglnPodLights"][0]
        posMonkeyStates = ['Idle', 'Eat', 'Alarmed', 'Vocalize', 'Off']
        Cumulative = 0

        for MonkeyState in posMonkeyStates:
            NewCumulative = eval("Cumulative + " + MonkeyState + "Pct")
            if PickABehavior > Cumulative and PickABehavior <= NewCumulative:
                if MonkeyState == "Off":
                    self.SendNote("respMonkeyOff")
                else:
                    respString = ("respMonkeyAct;{}".format(MonkeyState))
                    self.SendNote(respString)

                PtDebugPrint("nglnTreeMonkey.RandomBehavior():  Attempting Tree Monkey Anim: {}".format(MonkeyState))
                if LightsOn:
                    respMonkeySfx.run(self.key, state=str(MonkeyState))
                    PtDebugPrint("nglnTreeMonkey.RandomBehavior():  Attempting Tree Monkey SFX: {}".format(MonkeyState))
                return

            Cumulative = eval("Cumulative + " + MonkeyState + "Pct")

    ###########################
    def SendNote(self, ExtraInfo):
        notify = ptNotify(self.key)
        notify.clearReceivers()

        notify.addReceiver(self.key)

        notify.netPropagate(1)
        notify.netForce(1)
        notify.setActivate(1.0)

        notify.addVarNumber(str(ExtraInfo), 1.0)

        notify.send()

    ###########################
    def MonkeyAppears(self):
        whichtree = random.randint(0, 2)
        respSpawnPt.run(self.key, state=str(whichtree))
        self.SendNote("respMonkeyAct;Up")
        PtDebugPrint("nglnTreeMonkey.MonkeyAppears():  Tree Monkey is climbing Tree: {}".format(whichtree))

    ###########################
    def OnTimer(self, TimerID):
        PtDebugPrint("nglnTreeMonkey.OnTimer():  callback id={}".format(TimerID))
        if self.sceneobject.isLocallyOwned():
            if TimerID == 1:
                self.MonkeyAppears()
            elif TimerID == 2:
                self.InitNewSDLVars()

    ###########################
    def InitNewSDLVars(self):
        ageSDL = PtGetAgeSDL()

        ageSDL["MonkeyLastUpdated"] = (PtGetDniTime(),)

        beginningOfToday = PtGetDniTime() - int(PtGetAgeTimeOfDayPercent() * kDayLengthInSeconds)
        endOfToday = int(kDayLengthInSeconds / 2) + beginningOfToday

        # We need a random times in the first 5 hours of the day
        # which is in the first 31.8 percent of the day. So we're
        # generating a number from 0 to 318 and dividing by 1000 to get
        # something roughly in that timeframe.
        randnum = float(random.randint(0, 318))
        firstTime = int((randnum / 1000.0) * kDayLengthInSeconds) + beginningOfToday
        PtDebugPrint("nglnTreeMonkey.InitNewSDLVars():  Generated a valid spawn time: {}".format(firstTime))
        spawnTimes = [firstTime]

        while type(spawnTimes[-1]) == type(long(1)):
            randnum = random.randint(kMinimumTimeBetweenSpawns, kMaximumTimeBetweenSpawns)
            newTime = spawnTimes[-1] + randnum
            if newTime < endOfToday:
                PtDebugPrint("nglnTreeMonkey.InitNewSDLVars():  Generated a valid spawn time: {}".format(newTime))
                spawnTimes.append(newTime)
            else:
                PtDebugPrint("nglnTreeMonkey.InitNewSDLVars():  Generated a spawn time after dusk, exiting loop: {}".format(newTime))
                break
        else:
            PtDebugPrint("nglnTreeMonkey.InitNewSDLVars():  ERROR: Tried to add a spawn time that's not a number: {}".format(spawnTimes))
            spawnTimes = [0]

        while len(spawnTimes) < 20:
            spawnTimes.append(0)

        ageSDL["MonkeySpawnTimes"] = tuple(spawnTimes)

    ###########################
    def SetMonkeyTimers(self):
        PtClearTimerCallbacks(self.key)
        ageSDL = PtGetAgeSDL()
        if ageSDL["MonkeySpawnTimes"][0]:
            for timer in ageSDL["MonkeySpawnTimes"]:
                if timer:
                    timeTillSpawn = timer - PtGetDniTime()
                    PtDebugPrint("nglnTreeMonkey.SetMonkeyTimers():  {}    time: {}    timeTillSpawn: {}".format(timer, PtGetDniTime(), timeTillSpawn))
                    if timeTillSpawn > 0:
                        PtDebugPrint("nglnTreeMonkey.SetMonkeyTimers():  Setting timer for {} seconds".format(timeTillSpawn))
                        PtAtTimeCallback(self.key, timeTillSpawn, 1)

            # precision error FTW!
            timeLeftToday = kDayLengthInSeconds - int(PtGetAgeTimeOfDayPercent() * kDayLengthInSeconds)
            timeLeftToday += 1  # because we want it to go off right AFTER the day flips
            PtDebugPrint("nglnTreeMonkey.SetMonkeyTimers():  Setting EndOfDay timer for {} seconds".format(timeLeftToday))
            PtAtTimeCallback(self.key, timeLeftToday, 2)
        else:
            PtDebugPrint("nglnTreeMonkey.SetMonkeyTimers():  Timer array was empty!")

    ###########################
    def OnBackdoorMsg(self, target, param):
        if target == "monkey":
            if self.sceneobject.isLocallyOwned():
                PtDebugPrint("nglnTreeMonkey.OnBackdoorMsg():  Work!")
                if param == "up":
                    self.SendNote("respMonkeyAct;Up")
                elif param == "tree":
                    self.MonkeyAppears()

    def ExecCode(self, code):
        if code == "respMonkeyOff":
            respMonkeyOff.run(self.key)
        elif code.find("respMonkeyAct") != -1:
            try:
                chunks = code.split(';')
                ecMonkeyState = chunks[1]
                respMonkeyAct.run(self.key, state=ecMonkeyState)
            except:
                PtDebugPrint("nglnTreeMonkey.ExecCode():  ERROR: Invalid code '{}'.".format(code))
                stackList.pop(0)
        else:
            PtDebugPrint("nglnTreeMonkey.ExecCode():  ERROR: Invalid code '{}'.".format(code))
            stackList.pop(0)
