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
Module: nglnUrwinBrain
Age: Negilahn
Date: January 2004
Author: Doug McBride
HaX0r3d: Derek Odell
Controls the appearance and behavior of the Negilahn Urwin Bird
"""

from Plasma import *
from PlasmaTypes import *
import random

# define the attributes that will be entered in max
UrwinMasterAnim = ptAttribAnimation(1, "Urwin Master Anim", netForce=1)

respUrwinVocalize = ptAttribResponder(2, "resp: Urwin Vocalize")
respUrwinIdle = ptAttribResponder(3, "resp: Urwin Idles")
respUrwinIdleToWalk = ptAttribResponder(4, "resp: Urwin Idle To Walk")
respUrwinWalkLoop = ptAttribResponder(5, "resp: Urwin Walk Loop")
respUrwinWalkToIdle = ptAttribResponder(6, "resp: Urwin Walk To Idle")
respUrwinEat = ptAttribResponder(7, "resp: Urwin Eats")

respUrwinSfx = ptAttribNamedResponder(8, "resp: Urwin SFX", ['Eat', 'Idle', 'IdleToWalk', 'WalkLoop', 'WalkToIdle', 'Vocalize', 'Distance', 'Appear'], netForce=1)

actUrwinPathEnd = ptAttribActivator(9, "act: Urwin Path End")

# define globals
kDayLengthInSeconds = 56585  # Length of a Negilahn day in seconds Must match value in Negilahn.age file
kMinimumTimeBetweenSpawns = 3600  # 1 hour
kMaximumTimeBetweenSpawns = 25200  # 7 hours
# We need the first random spawn time in the first 5 hours of the day
# which is in the first 44.5 percent of the day. So we're
# generating a number from 0 to 445 and later we divide by 1000 to get
# something roughly in that timeframe.
kFirstMorningSpawn = 445

minsteps = 3
maxsteps = 10

StepsToTake = 0
stackList = []


class nglnUrwinBrain(ptResponder):

    ############################
    def __init__(self):
        ptResponder.__init__(self)
        self.id = 5244
        version = 4
        minor = 0
        self.version = "{}.{}".format(version, minor)
        PtDebugPrint("__init__: nglnUrwinBrain v{}".format(self.version))
        random.seed()

    ############################
    def OnServerInitComplete(self):
        try:
            ageSDL = PtGetAgeSDL()
        except:
            PtDebugPrint("nglnUrwinBrain.OnServerInitComplete():  ERROR: Cannot find the Negilahn Age SDL")
            self.InitNewSDLVars()

        ageSDL.sendToClients("UrwinLastUpdated")
        ageSDL.sendToClients("UrwinSpawnTimes")
        ageSDL.sendToClients("UrwinOnTheProwl")
        ageSDL.setFlags("UrwinLastUpdated", 1, 1)
        ageSDL.setFlags("UrwinSpawnTimes", 1, 1)
        ageSDL.setFlags("UrwinOnTheProwl", 1, 1)
        ageSDL.setFlags("nglnPodLights", 1, 1)
        ageSDL.setNotify(self.key, "UrwinLastUpdated", 0.0)
        ageSDL.setNotify(self.key, "UrwinSpawnTimes", 0.0)
        ageSDL.setNotify(self.key, "UrwinOnTheProwl", 0.0)
        ageSDL.setNotify(self.key, "nglnPodLights", 0.0)

        thisDay = int(PtGetDniTime() / kDayLengthInSeconds)
        lastDay = int(ageSDL["UrwinLastUpdated"][0] / kDayLengthInSeconds)

        if (thisDay - lastDay) > 0:
            PtDebugPrint("nglnUrwinBrain.OnServerInitComplete():  It's been at least a day since the last update, running new numbers now.")
            self.InitNewSDLVars()
        else:
            PtDebugPrint("nglnUrwinBrain.OnServerInitComplete():  It's been less than a day since the last update, doing nothing")
            self.SetUrwinTimers()

        if not len(PtGetPlayerList()):
            UrwinMasterAnim.animation.skipToBegin()

    ###########################
    def OnSDLNotify(self, VARname, SDLname, playerID, tag):
        if VARname == "UrwinSpawnTimes":
            self.SetUrwinTimers()

        # Had to wire this to stop SFX if the lights go off....
        elif VARname == "nglnPodLights":
            ageSDL = PtGetAgeSDL()
            if not ageSDL[VARname][0] and ageSDL["UrwinOnTheProwl"][0]:
                respUrwinSfx.run(self.key, state="Idle")

   ############################
    def OnNotify(self, state, id, events):
        global StepsToTake
        global stackList

        ageSDL = PtGetAgeSDL()
        PtDebugPrint("nglnUrwinBrain.OnNotify():  state={:f} id={} owned={} prowl={} events={}".format(state, id, self.sceneobject.isLocallyOwned(), ageSDL["UrwinOnTheProwl"][0], events))

        if id == (-1):
            PtDebugPrint("nglnUrwinBrain.OnNotify():  Need to store event: {}".format(events[0][1]))
            stackList.append(events[0][1])
            PtDebugPrint("nglnUrwinBrain.OnNotify():  New list is: {}".format(stackList))
            if len(stackList) == 1:
                PtDebugPrint("nglnUrwinBrain.OnNotify():  List is only one command long, so I'm playing it")
                code = stackList[0]
                PtDebugPrint("nglnUrwinBrain.OnNotify():  - Playing command: {}".format(code))
                self.ExecCode(code)

        elif state and self.sceneobject.isLocallyOwned() and ageSDL["UrwinOnTheProwl"][0]:
            if id == respUrwinSfx.id:
                PtDebugPrint("nglnUrwinBrain.OnNotify():  Callback was from Appearance SFX, and I own the age, so start walking")
                self.StartToWalk()

            else:
                PtDebugPrint("nglnUrwinBrain.OnNotify():  Callback was from responder, and I own the age, so Logic Time")
                old = stackList.pop(0)
                PtDebugPrint("nglnUrwinBrain.OnNotify():  Popping off: {}".format(old))
                boolBatteryChargedAndOn = ageSDL["nglnPodLights"][0]

                if id == respUrwinIdleToWalk.id:
                    self.StartToWalk()

                elif id == respUrwinWalkLoop.id:
                    StepsToTake = StepsToTake - 1
                    if StepsToTake:
                        # 90% chance of continuing walk loop
                        if random.randint(0, 9):
                            PtDebugPrint("nglnUrwinBrain.OnNotify():  Urwin will take {} more steps...".format(StepsToTake))
                            self.SendNote("respUrwinWalkLoop")
                            if boolBatteryChargedAndOn:
                                respUrwinSfx.run(self.key, state="WalkLoop")
                        # 10% to eat
                        else:
                            PtDebugPrint("nglnUrwinBrain.OnNotify():  Urwin is hungry and decides to eat")
                            self.SendNote("respUrwinEat")
                            if boolBatteryChargedAndOn:
                                respUrwinSfx.run(self.key, state="Eat")
                    else:
                        PtDebugPrint("nglnUrwinBrain.OnNotify():  Urwin is tired and stops walking")
                        PtAtTimeCallback(self.key, 0.666, 3)
                        self.SendNote("respUrwinWalkToIdle")
                        if boolBatteryChargedAndOn:
                            respUrwinSfx.run(self.key, state="WalkToIdle")

                elif id == respUrwinEat.id:
                    PtDebugPrint("nglnUrwinBrain.OnNotify():  Urwin is done eating and continues walking")
                    self.SendNote("respUrwinWalkLoop")
                    if boolBatteryChargedAndOn:
                        respUrwinSfx.run(self.key, state="WalkLoop")

                elif id == respUrwinWalkToIdle.id:
                    self.RandomBehavior()

                elif id == respUrwinIdle.id or id == respUrwinVocalize.id:
                    # 66% chance of picking another random behaviour
                    if random.randint(0, 2):
                        self.RandomBehavior()
                    # 33% to go back to walking
                    else:
                        PtDebugPrint("nglnUrwinBrain.OnNotify():  Urwin is rested and goes back to walking")
                        self.SendNote("respUrwinIdleToWalk")
                        UrwinMasterAnim.animation.resume()
                        if boolBatteryChargedAndOn:
                            respUrwinSfx.run(self.key, state="IdleToWalk")

                elif id == actUrwinPathEnd.id:
                    PtDebugPrint("nglnUrwinBrain.OnNotify():  End of the line, Urwin!")
                    UrwinMasterAnim.animation.stop()
                    UrwinMasterAnim.animation.skipToTime(0)
                    ageSDL["UrwinOnTheProwl"] = (0,)
                    if boolBatteryChargedAndOn:
                        respUrwinSfx.run(self.key, state="Distance")

        elif id in range(2, 8) and not self.sceneobject.isLocallyOwned():
            PtDebugPrint("nglnUrwinBrain.OnNotify():  Callback was from responder, and I DON'T own the age, so I'll try playing the next item in list")
            old = stackList.pop(0)
            PtDebugPrint("nglnUrwinBrain.OnNotify():  Popping off: {}".format(old))
            if len(stackList):
                PtDebugPrint("nglnUrwinBrain.OnNotify():  List has at least one item ready to play")
                code = stackList[0]
                PtDebugPrint("nglnUrwinBrain.OnNotify():  - Playing command: {}".format(code))
                self.ExecCode(code)

        else:
            PtDebugPrint("nglnUrwinBrain.OnNotify():  Callback from something else?")

    ############################
    def RandomBehavior(self):
        ageSDL = PtGetAgeSDL()

        boolBatteryChargedAndOn = ageSDL["nglnPodLights"][0]

        # 66% chance of idling
        if random.randint(0, 2):
            PtDebugPrint("nglnUrwinBrain.RandomBehavior():  Urwin is being lazy and just idling")
            self.SendNote("respUrwinIdle")
            if boolBatteryChargedAndOn:
                respUrwinSfx.run(self.key, state="Idle")
        # 33% to vocalize
        else:
            PtDebugPrint("nglnUrwinBrain.RandomBehavior():  Urwin is calling home.")
            self.SendNote("respUrwinVocalize")
            if boolBatteryChargedAndOn:
                respUrwinSfx.run(self.key, state="Vocalize")

    ############################
    def StartToWalk(self):
        global StepsToTake

        ageSDL = PtGetAgeSDL()
        boolBatteryChargedAndOn = ageSDL["nglnPodLights"][0]

        StepsToTake = random.randint(minsteps, maxsteps)
        PtDebugPrint("nglnUrwinBrain.StartToWalk():  Urwin has decided to take {} steps.".format(StepsToTake))

        self.SendNote("respUrwinWalkLoop")
        UrwinMasterAnim.animation.resume()
        if boolBatteryChargedAndOn:
            respUrwinSfx.run(self.key, state="WalkLoop")

    ############################
    def OnTimer(self, TimerID):
        global UrwinOnTheProwl

        ageSDL = PtGetAgeSDL()
        boolBatteryChargedAndOn = ageSDL["nglnPodLights"][0]
        if self.sceneobject.isLocallyOwned():
            if TimerID == 1:
                PtDebugPrint("nglnUrwinBrain.OnTimer():  Time for the Urwin to return.")
                ageSDL["UrwinOnTheProwl"] = (1,)
                if ageSDL["nglnPodLights"][0]:
                    respUrwinSfx.run(self.key, state="Appear")
                else:
                    self.StartToWalk()
            elif TimerID == 2:
                PtDebugPrint("nglnUrwinBrain.OnTimer():  New day, let's renew the timers.")
                self.InitNewSDLVars()
            elif TimerID == 3:
                UrwinMasterAnim.animation.stop()

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
    def InitNewSDLVars(self):
        ageSDL = PtGetAgeSDL()

        ageSDL["UrwinLastUpdated"] = (PtGetDniTime(),)

        beginningOfToday = PtGetDniTime() - int(PtGetAgeTimeOfDayPercent() * kDayLengthInSeconds)
        endOfToday = int(kDayLengthInSeconds / 2) + beginningOfToday

        # We need a random times in the first 5 hours of the day
        # which is in the first 44.5 percent of the day. So we're
        # generating a number from 0 to 445 and dividing by 1000 to get
        # something roughly in that timeframe.
        randnum = float(random.randint(0, kFirstMorningSpawn))
        firstTime = int((randnum / 1000.0) * kDayLengthInSeconds) + beginningOfToday
        PtDebugPrint("nglnUrwinBrain.InitNewSDLVars():  Generated a valid spawn time: {}".format(firstTime))
        spawnTimes = [firstTime]

        while type(spawnTimes[-1]) == type(long(1)):
            randnum = random.randint(kMinimumTimeBetweenSpawns, kMaximumTimeBetweenSpawns)
            newTime = spawnTimes[-1] + randnum
            if newTime < endOfToday:
                PtDebugPrint("nglnUrwinBrain.InitNewSDLVars():  Generated a valid spawn time: {}".format(newTime))
                spawnTimes.append(newTime)
            else:
                PtDebugPrint("nglnUrwinBrain.InitNewSDLVars():  Generated a spawn time after dusk, exiting loop: {}".format(newTime))
                break
        else:
            PtDebugPrint("nglnUrwinBrain.InitNewSDLVars():  ERROR: Tried to add a spawn time that's not a number: {}".format(spawnTimes))
            spawnTimes = [0]

        while len(spawnTimes) < 20:
            spawnTimes.append(0)

        ageSDL["UrwinSpawnTimes"] = tuple(spawnTimes)

    ###########################
    def SetUrwinTimers(self):
        PtClearTimerCallbacks(self.key)
        ageSDL = PtGetAgeSDL()
        if ageSDL["UrwinSpawnTimes"][0]:
            for timer in ageSDL["UrwinSpawnTimes"]:
                if timer:
                    timeTillSpawn = timer - PtGetDniTime()
                    PtDebugPrint("nglnUrwinBrain.SetUrwinTimers():  timer: {}    time: {}    timeTillSpawn: {}".format(timer, PtGetDniTime(), timeTillSpawn))
                    if timeTillSpawn > 0:
                        PtDebugPrint("nglnUrwinBrain.SetUrwinTimers():  Setting timer for {} seconds".format(timeTillSpawn))
                        PtAtTimeCallback(self.key, timeTillSpawn, 1)

            # precision error FTW!
            timeLeftToday = kDayLengthInSeconds - int(PtGetAgeTimeOfDayPercent() * kDayLengthInSeconds)
            timeLeftToday += 1  # because we want it to go off right AFTER the day flips
            PtDebugPrint("nglnUrwinBrain.SetUrwinTimers():  Setting EndOfDay timer for {} seconds".format(timeLeftToday))
            PtAtTimeCallback(self.key, timeLeftToday, 2)
        else:
            PtDebugPrint("nglnUrwinBrain.SetUrwinTimers():  Timer array was empty!")

    ###########################
    def OnBackdoorMsg(self, target, param):
        global kMinimumTimeBetweenSpawns
        global kMaximumTimeBetweenSpawns
        global kFirstMorningSpawn

        ageSDL = PtGetAgeSDL()
        if target == "urwin":
            if self.sceneobject.isLocallyOwned():
                PtDebugPrint("nglnUrwinBrain.OnBackdoorMsg():  Backdoor!")
                if param == "walk":
                    ageSDL["UrwinOnTheProwl"] = (1,)
                    if ageSDL["nglnPodLights"][0]:
                        PtAtTimeCallback(self.key, 1, 1)
                    else:
                        self.StartToWalk()

                elif param == "restore":
                    kMinimumTimeBetweenSpawns = 3600  # 1 hour
                    kMaximumTimeBetweenSpawns = 25200  # 7 hours
                    kFirstMorningSpawn = 445
                    self.InitNewSDLVars()

                elif type(param) is str:
                    newTimes = param.split(";")
                    kMinimumTimeBetweenSpawns = int(newTimes[0])
                    kMaximumTimeBetweenSpawns = int(newTimes[1])
                    kFirstMorningSpawn = 1
                    self.InitNewSDLVars()

    def ExecCode(self, code):
        global stackList
        if code == "respUrwinIdle":
            respUrwinIdle.run(self.key)
        elif code == "respUrwinIdleToWalk":
            respUrwinIdleToWalk.run(self.key)
        elif code == "respUrwinWalkLoop":
            respUrwinWalkLoop.run(self.key)
        elif code == "respUrwinWalkToIdle":
            respUrwinWalkToIdle.run(self.key)
        elif code == "respUrwinEat":
            respUrwinEat.run(self.key)
        elif code == "respUrwinVocalize":
            respUrwinVocalize.run(self.key)
        else:
            PtDebugPrint("nglnUrwinBrain.ExecCode():  ERROR: Invalid code '{}'.".format(code))
            stackList.pop(0)
