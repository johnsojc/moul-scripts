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
Module: clftNpcZandi
Age: Cleft
Date: September 2002
Author: Doug McBride
Controls Zandi for Phase0 dialog
"""

from Plasma import *
from PlasmaTypes import *
import random
import time
import PlasmaControlKeys
import xEnum

# define the attributes that will be entered in max
Activate = ptAttribActivator(1, "Region Sensor")
MultiStage01 = ptAttribBehavior(2, "NPC Multistage behavior", netForce=1)
NpcSpawner = ptAttribActivator(3, "NPC Spawn point")

respBrakeNotReleased = ptAttribResponder(10, "Brake not released", ["1", "2"])
respWindmillNotTurning = ptAttribResponder(11, "Windmill not turning", ["1", "2"])
respVisionNotSeen = ptAttribResponder(12, "Vision not seen", ["1", "2"])
respNoTrailerJC = ptAttribResponder(13, "No trailer JC", ["1", "2"])
respNoImagerJC = ptAttribResponder(14, "No imager room JC", ["1", "2"])
respNoBedroomJC = ptAttribResponder(15, "No bedroom JC", ["1", "2"])
respNoWahrkJC = ptAttribResponder(16, "No wahrk JC", ["1", "2"])
respNoSignJC = ptAttribResponder(17, "No sign JC", ["1", "2"])
respNoBucketJC = ptAttribResponder(18, "No bucket JC", ["1", "2"])
respNoDoorJC = ptAttribResponder(19, "No door JC", ["1", "2"])
respDoorNotOpen = ptAttribResponder(20, "Tree door not opened", ["1", "2"])

respZandiSayings = ptAttribResponder(21, "Zandi sayings", ["welcome", "dryheat", "pizza", "keepexploring", "interrupt", "steak", "welcome2"])
actZandiClick = ptAttribActivator(22, "Zandi clickable")

# globals
IgnoreTime = 120
PageTurnInterval = 120

TimerID = xEnum.Enum("IgnoreFinished = 10, TurnPage")

JC = xEnum.Enum("Trailer, Imager, Bedroom, Wahrk, Sign, Bucket, Door")
jcDict = {
    JC.Trailer: 'c', JC.Imager: 'd', JC.Bedroom: 'e', JC.Wahrk: 'b', JC.Sign: 'a', JC.Bucket: 'g', JC.Door: 'f'}


class clftNpcZandi(ptModifier):
    def __init__(self):
        ptModifier.__init__(self)
        self.id = 5217
        version = 7
        minor = 0
        self.version = "{}.{}".format(version, minor)
        PtDebugPrint("__init__: clftNpcZandi v{}".format(self.version))
        self.NpcName = None
        self.ZandiFace = None
        random.seed()

    def OnFirstUpdate(self):
        self.AlreadyPlayed = 0
        self.IsTalking = 0
        self.IsIgnoring = 0
        self.DoingBehavior = 0
        self.NearZandi = 0
        self.PlayWelcome2 = 0
        self.LastSpeech = -1
        self.PlayOnFinish = 0

        vault = ptVault()

        entry = vault.findChronicleEntry("YeeshaVisionViewed")
        if entry is None:
            vault.addChronicleEntry("YeeshaVisionViewed", 0, "0")

        PtAtTimeCallback(self.key, PageTurnInterval, TimerID.TurnPage)

    def OnNotify(self, state, id, events):
        PtDebugPrint("clftNpcZandi.OnNotify():  id = {}".format(id))
        if id == NpcSpawner.id:  # Causes Zandi to Ilde even before avatar visits
            self.NpcName = PtFindAvatar(events)
            MultiStage01.run(self.NpcName)

        elif id == actZandiClick.id:
            PtDebugPrint("clftNpcZandi.OnNotify():  Zandi was clicked")
            if not self.IsTalking:
                PtDebugPrint("clftNpcZandi.OnNotify():  Zandi will talk")
                self.ZandiSpeaks(1)
            else:
                PtDebugPrint("clftNpcZandi.OnNotify():  Zandi is already talking")

        elif id == Activate.id:
            # Zandi himself will activate the region when he spawns...
            # So, only let the avatar who enters do this. Zandi != local avatar, so win
            if PtFindAvatar(events) != PtGetLocalAvatar():
                return

            for event in events:
                if event[0] == 1 and event[1] == 1:  # avatar physically approached Zandi
                    self.NearZandi = 1
                    if not (self.IsTalking or self.IsIgnoring):
                        self.ZandiSpeaks()

                elif event[0] == 1 and event[1] == 0:  # avatar physically stepped away from Zandi
                    self.NearZandi = 0
                    self.PlayWelcome2 = 0

        elif id == MultiStage01.id:
            PtDebugPrint("clftNpcZandi.OnNotify():  notified by behavior")
            for event in events:
                if event[0] == 10 and event[2] == 3:  # A Zandi behavior just finished. Returning to idle animation.
                    PtDebugPrint("clftNpcZandi.OnNotify():  zandi is done doing a behavior")
                    self.DoingBehavior = 0
                    break

        elif id in (respBrakeNotReleased.id, respWindmillNotTurning.id, respVisionNotSeen.id, respNoTrailerJC.id,
                    respNoImagerJC.id, respNoBedroomJC.id, respNoWahrkJC.id, respNoSignJC.id, respNoBucketJC.id,
                    respNoDoorJC.id, respDoorNotOpen.id, respZandiSayings.id):
            PtDebugPrint("clftNpcZandi.OnNotify():  zandi finished talking")
            if self.PlayOnFinish:
                PtDebugPrint("clftNpcZandi.OnNotify():  zandi has more to say")
                self.PlayOnFinish = 0
                self.ZandiSpeaks()
            else:
                PtDebugPrint("clftNpcZandi.OnNotify():  zandi really is done and is ready to say more")
                self.IsTalking = 0

    def OnTimer(self, id):
        if id < 10:
            PtDebugPrint("clftNpcZandi.OnTimer():  attempt behavior {}".format(id))
            if not self.DoingBehavior:
                PtDebugPrint("clftNpcZandi.OnTimer():  doing behavior {}".format(id))
                self.DoingBehavior = 1
                MultiStage01.gotoStage(self.NpcName, id, dirFlag=1, isForward=1)
            if type(self.ZandiFace) is str:
                PtDebugPrint("clftNpcZandi.OnTimer():  using zandi face anim: {}".format(self.ZandiFace))
                self.NpcName.avatar.playSimpleAnimation(self.ZandiFace)

        elif id == TimerID.TurnPage:
            PtDebugPrint("clftNpcZandi.OnTimer():  attempt turn page")
            if not self.DoingBehavior:
                PtDebugPrint("clftNpcZandi.OnTimer():  do turn page")
                self.DoingBehavior = 1
                MultiStage01.gotoStage(self.NpcName, 2, dirFlag=1, isForward=1)  # turn page
                PtAtTimeCallback(self.key, PageTurnInterval, TimerID.TurnPage)

        elif id == TimerID.IgnoreFinished:
            PtDebugPrint("clftNpcZandi.OnTimer():  timer ignorefinished")
            if self.NearZandi:
                if self.IsTalking:
                    PtDebugPrint("clftNpcZandi.OnTimer():  zandi's talking, play on finish")
                    self.PlayOnFinish = 1
                else:
                    "clftNpcZandi.OnTimer():  speak zandi speak!"
                    self.ZandiSpeaks()
            else:
                PtDebugPrint("clftNpcZandi.OnTimer():  zandi's done ignoring")
                self.IsIgnoring = 0

    def GetJCProgress(self):
        vault = ptVault()
        chron = vault.findChronicleEntry("JourneyClothProgress")
        jcProgress = ""
        if chron:
            ageChronRefList = chron.getChildNodeRefList()
            for ageChron in ageChronRefList:
                ageChild = ageChron.getChild()

                ageChild = ageChild.upcastToChronicleNode()

                if ageChild.chronicleGetName() == "Cleft":
                    return ageChild.chronicleGetValue()

        return ""

    def CheckForJC(self, progress, jc):
        PtDebugPrint("clftNpcZandi.CheckForJC():  check for jc")
        if jcDict[jc] in progress:
            return 1
        else:
            return 0

    def BahroDoorStillClosed(self, sdl):
        PtDebugPrint("clftNpcZandi.BahroDoorStillClosed():  in bahro door still closed")
        if sdl["clftBahroDoorClosed"][0]:
            return 1
        else:
            return 0

    def BrakeNotReleased(self, sdl):
        PtDebugPrint("clftNpcZandi.BrakeNotReleased():  in brake not released")
        if sdl["clftAgeSDLWindmillLocked"][0]:
            return 1
        else:
            return 0

    def WindmillNotTurning(self, sdl):
        PtDebugPrint("clftNpcZandi.WindmillNotTurning():  in windmill not turning")
        if sdl["clftAgeSDLWindmillRunning"][0]:
            return 0
        else:
            return 1

    def HaventSeenImagerMessage(self):
        PtDebugPrint("clftNpcZandi.HaventSeenImagerMessage():  in haven't seen imager message")
        vault = ptVault()
        entry = vault.findChronicleEntry("YeeshaVisionViewed")
        if entry is None:
            PtDebugPrint("ERROR: clftNpcZandi.HaventSeenImagerMessage():  cannot find YeeshaVisionViewed chronicle entry")
            return 1

        if entry.chronicleGetValue() == "1":
            return 0
        else:
            return 1

    def NeedsWelcome(self, clicked=0):
        PtDebugPrint("clftNpcZandi.NeedsWelcome():  in needs welcome")
        if self.LastSpeech < 0 and clicked:
            PtDebugPrint("clftNpcZandi.NeedsWelcome():  last speech less than 0 and clicked")
            return 1

        vault = ptVault()
        entry = vault.findChronicleEntry("ZandiWelcome")
        if entry is None:
            if not clicked:
                vault.addChronicleEntry("ZandiWelcome", 0, "1")
            return 1

        if entry.chronicleGetValue() == "1":
            return 0
        else:
            if not clicked:
                entry.chronicleSetValue("1")
                entry.save()
            return 1

    def PlaySecondWelcome(self):
        # we're not actually playing the second welcome, but I don't want to break the logic
        respZandiSayings.run(self.key, state="welcome")
        self.ZandiFace = "ZandiOpen01Face"

    def ZandiSpeaks(self, clicked=0):

        # Multistage numbers:
        # 0 Idle
        # 1 ScratchHead
        # 2 TurnPage
        # 3 Directions
        # 4 CrossLegs
        # 5 RubNose

        useSpeech = "2"

        PtDebugPrint("clftNpcZandi.ZandiSpeaks():  last speech: {}".format(self.LastSpeech))

        self.IsTalking = 1
        stage = random.randint(1, 5)
        sdl = PtGetAgeSDL()

        if self.PlayWelcome2 and clicked:
            if self.LastSpeech >= 0:
                PtDebugPrint("clftNpcZandi.ZandiSpeaks():  we've moved past the welcome, so don't play welcome 2")
                self.PlayWelcome2 = 0
            else:
                PtDebugPrint("clftNpcZandi.ZandiSpeaks():  let's play welcome2")
                self.PlaySecondWelcome()
                stage = 4

        if self.NeedsWelcome(clicked):
            PtDebugPrint("clftNpcZandi.ZandiSpeaks():  zandi playes the welcome")
            respZandiSayings.run(self.key, state="welcome")
            self.ZandiFace = "ZandiOpen01Face"
            self.PlayWelcome2 = 1
            stage = 4

        elif self.BrakeNotReleased(sdl):
            if self.LastSpeech != 0:
                useSpeech = "1"
                self.AlreadyPlayed = 0
                self.LastSpeech = 0
            else:
                if not clicked:
                    self.AlreadyPlayed = 1
                else:
                    if self.AlreadyPlayed:
                        useSpeech = "2"
                    else:
                        useSpeech = "1"

            PtDebugPrint("clftNpcZandi.ZandiSpeaks():  playing brake not released, speech = {}".format(useSpeech))
            respBrakeNotReleased.run(self.key, useSpeech)
            if useSpeech == "1":
                self.ZandiFace = "ZandiRes01aFace"
            else:
                self.ZandiFace = "ZandiRes01bFace"

        elif self.WindmillNotTurning(sdl):
            if self.LastSpeech != 1:
                useSpeech = "1"
                self.AlreadyPlayed = 0
                self.LastSpeech = 1
            else:
                if not clicked:
                    self.AlreadyPlayed = 1
                else:
                    if self.AlreadyPlayed:
                        useSpeech = "2"
                    else:
                        useSpeech = "1"
            PtDebugPrint("clftNpcZandi.ZandiSpeaks():  playing no windmill, speech = {}".format(useSpeech))
            respWindmillNotTurning.run(self.key, useSpeech)
            if useSpeech == "1":
                self.ZandiFace = "ZandiRes02aFace"
            else:
                self.ZandiFace = "ZandiRes02bFace"

        elif self.HaventSeenImagerMessage():
            if self.LastSpeech != 2:
                useSpeech = "1"
                self.AlreadyPlayed = 0
                self.LastSpeech = 2
            else:
                if not clicked:
                    self.AlreadyPlayed = 1
                else:
                    if self.AlreadyPlayed:
                        useSpeech = "2"
                    else:
                        useSpeech = "1"
            PtDebugPrint("clftNpcZandi.ZandiSpeaks():  playing no imager message, speech = {}".format(useSpeech))
            respVisionNotSeen.run(self.key, useSpeech)
            if useSpeech == "1":
                self.ZandiFace = "ZandiRes03aFace"
            else:
                self.ZandiFace = "ZandiRes03bFace"

        else:
            jcProgress = self.GetJCProgress()
            if not self.CheckForJC(jcProgress, JC.Trailer):
                if self.LastSpeech != 3:
                    useSpeech = "1"
                    self.AlreadyPlayed = 0
                    self.LastSpeech = 3
                else:
                    if not clicked:
                        self.AlreadyPlayed = 1
                    else:
                        if self.AlreadyPlayed:
                            useSpeech = "2"
                        else:
                            useSpeech = "1"
                PtDebugPrint("clftNpcZandi.ZandiSpeaks():  playing no trailer jc, speech = {}".format(useSpeech))
                respNoTrailerJC.run(self.key, useSpeech)

                if useSpeech == "1":
                    self.ZandiFace = "ZandiJC01aFace"
                else:
                    self.ZandiFace = "ZandiJC01bFace"

            elif not self.CheckForJC(jcProgress, JC.Imager):
                if self.LastSpeech != 4:
                    useSpeech = "1"
                    self.AlreadyPlayed = 0
                    self.LastSpeech = 4
                else:
                    if not clicked:
                        self.AlreadyPlayed = 1
                    else:
                        if self.AlreadyPlayed:
                            useSpeech = "2"
                        else:
                            useSpeech = "1"
                PtDebugPrint("clftNpcZandi.ZandiSpeaks():  playing no imager jc, speech = {}".format(useSpeech))
                respNoImagerJC.run(self.key, useSpeech)
                if useSpeech == "1":
                    self.ZandiFace = "ZandiJC02aFace"
                else:
                    self.ZandiFace = "ZandiJC02bFace"

            elif not self.CheckForJC(jcProgress, JC.Bedroom):
                if self.LastSpeech != 5:
                    useSpeech = "1"
                    self.AlreadyPlayed = 0
                    self.LastSpeech = 5
                else:
                    if not clicked:
                        self.AlreadyPlayed = 1
                    else:
                        if self.AlreadyPlayed:
                            useSpeech = "2"
                        else:
                            useSpeech = "1"
                PtDebugPrint("clftNpcZandi.ZandiSpeaks():  playing no bedroom jc, speech = {}".format(useSpeech))
                respNoBedroomJC.run(self.key, useSpeech)
                if useSpeech == "1":
                    self.ZandiFace = "ZandiJC03aFace"
                else:
                    self.ZandiFace = "ZandiJC03bFace"

            elif not self.CheckForJC(jcProgress, JC.Wahrk) and not PtIsDemoMode():
                if self.LastSpeech != 6:
                    useSpeech = "1"
                    self.AlreadyPlayed = 0
                    self.LastSpeech = 6
                else:
                    if not clicked:
                        self.AlreadyPlayed = 1
                    else:
                        if self.AlreadyPlayed:
                            useSpeech = "2"
                        else:
                            useSpeech = "1"
                PtDebugPrint("clftNpcZandi.ZandiSpeaks():  playing no whark jc, speech = {}".format(useSpeech))
                respNoWahrkJC.run(self.key, useSpeech)
                if useSpeech == "1":
                    self.ZandiFace = "ZandiJC04aFace"
                else:
                    self.ZandiFace = "ZandiJC04bFace"

            elif not self.CheckForJC(jcProgress, JC.Sign) and not PtIsDemoMode():
                if self.LastSpeech != 7:
                    useSpeech = "1"
                    self.AlreadyPlayed = 0
                    self.LastSpeech = 7
                else:
                    if not clicked:
                        self.AlreadyPlayed = 1
                    else:
                        if self.AlreadyPlayed:
                            useSpeech = "2"
                        else:
                            useSpeech = "1"
                PtDebugPrint("clftNpcZandi.ZandiSpeaks():  playing no sign jc, speech = {}".format(useSpeech))
                respNoSignJC.run(self.key, useSpeech)
                if useSpeech == "1":
                    self.ZandiFace = "ZandiJC05aFace"
                else:
                    self.ZandiFace = "ZandiJC05bFace"

            elif not self.CheckForJC(jcProgress, JC.Bucket):
                if self.LastSpeech != 8:
                    useSpeech = "1"
                    self.AlreadyPlayed = 0
                    self.LastSpeech = 8
                else:
                    if not clicked:
                        self.AlreadyPlayed = 1
                    else:
                        if self.AlreadyPlayed:
                            useSpeech = "2"
                        else:
                            useSpeech = "1"
                PtDebugPrint("clftNpcZandi.ZandiSpeaks():  playing no bucket jc, speech = {}".format(useSpeech))
                respNoBucketJC.run(self.key, useSpeech)
                if useSpeech == "1":
                    self.ZandiFace = "ZandiJC06aFace"
                else:
                    self.ZandiFace = "ZandiJC06bFace"

            elif not self.CheckForJC(jcProgress, JC.Door):
                if self.LastSpeech != 9:
                    useSpeech = "1"
                    self.AlreadyPlayed = 0
                    self.LastSpeech = 9
                else:
                    if not clicked:
                        self.AlreadyPlayed = 1
                    else:
                        if self.AlreadyPlayed:
                            useSpeech = "2"
                        else:
                            useSpeech = "1"
                PtDebugPrint("clftNpcZandi.ZandiSpeaks():  playing no door jc, speech = {}".format(useSpeech))
                respNoDoorJC.run(self.key, useSpeech)
                if useSpeech == "1":
                    self.ZandiFace = "ZandiJC07aFace"
                else:
                    self.ZandiFace = "ZandiJC07bFace"

            elif self.BahroDoorStillClosed(sdl):
                if self.LastSpeech != 10:
                    useSpeech = "1"
                    self.AlreadyPlayed = 0
                    self.LastSpeech = 10
                else:
                    if not clicked:
                        self.AlreadyPlayed = 1
                    else:
                        if self.AlreadyPlayed:
                            useSpeech = "2"
                        else:
                            useSpeech = "1"
                PtDebugPrint("clftNpcZandi.ZandiSpeaks():  playing door not open speech")
                respDoorNotOpen.run(self.key)
                self.ZandiFace = "ZandiAllFace"
            else:
                self.LastSpeech = 11
                sayings = ["welcome", "welcome2", "dryheat", "keepexploring", "steak", "pizza", "interrupt"]
                usesaying = random.randint(2, 6)
                useSpeech = sayings[usesaying]

                self.ZandiFace = "ZandiRand0" + str(usesaying - 1) + "Face"

                if useSpeech != "":
                    PtDebugPrint("clftNpcZandi.ZandiSpeaks():  playing misc, speech = {}".format(useSpeech))
                    respZandiSayings.run(self.key, state=useSpeech)

        PtAtTimeCallback(self.key, 2, stage)

        if not clicked:
            PtAtTimeCallback(self.key, IgnoreTime, TimerID.IgnoreFinished)
            self.IsIgnoring = 1
