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
# Include Plasma code
from Plasma import *
from PlasmaTypes import *
from PlasmaKITypes import *

# for save/load
#import cPickle  # not used

## COMMENTED OUT by Jeff due to the re-write in the garrison wall

##############################################################
# define the attributes/parameters that we need from the 3dsMax scene
##############################################################

northPanelClick = ptAttribActivator(1, "North Panel Clickables")
southPanelClick = ptAttribActivator(2, "South Panel Clickables")

northPanel = ptAttribSceneobjectList(3, "North Panel Objects", byObject=1)
southPanel = ptAttribSceneobjectList(4, "South Panel Objects", byObject=1)

# if northWall = 5 and southWall = 6 then your control panel
# controls the wall that YOU climb on (useful for debugging)
# just remember to switch them back before going live...
northWall = ptAttribSceneobjectList(5, "North Wall", byObject=1)
southWall = ptAttribSceneobjectList(6, "South Wall", byObject=1)

northChair = ptAttribActivator(7, "North Chair")
southChair = ptAttribActivator(8, "South Chair")

northLights = ptAttribSceneobjectList(9, "North Panel Lights", byObject=1)
southLights = ptAttribSceneobjectList(10, "South Panel Lights", byObject=1)

northCountLights = ptAttribSceneobjectList(11, "North Count Lights", byObject=1)
southCountLights = ptAttribSceneobjectList(12, "South Count Lights", byObject=1)

upButtonS = ptAttribActivator(13, "S up count button")
dnButtonS = ptAttribActivator(14, "S down count button")
readyButtonS = ptAttribActivator(15, "S ready button")

upButtonN = ptAttribActivator(18, "N up count button")
dnButtonN = ptAttribActivator(19, "N down count button")
readyButtonN = ptAttribActivator(20, "N ready button")

goButtonN = ptAttribActivator(21, "N Go Button activator")
goButtonS = ptAttribActivator(22, "S Go Button activator")

goBtnNObject = ptAttribSceneobject(23, "N Go Button object")
goBtnSObject = ptAttribSceneobject(24, "S Go Button object")

nChairSit = ptAttribActivator(25, "N sit component")
sChairSit = ptAttribActivator(26, "S sit component")

fiveBtnN = ptAttribActivator(27, "5 btn N")
tenBtnN = ptAttribActivator(28, "10 btn N")
fifteenBtnN = ptAttribActivator(29, "15 btn N")

fiveBtnS = ptAttribActivator(30, "5 btn S")
tenBtnS = ptAttribActivator(31, "10 btn S")
fifteenBtnS = ptAttribActivator(32, "15 btn S")

sTubeOpen = ptAttribNamedResponder(33, "S tube open", netForce=1)
nTubeOpen = ptAttribNamedResponder(34, "N tube open", netForce=1)

sTubeClose = ptAttribNamedResponder(35, "S tube close", netForce=1)
nTubeClose = ptAttribNamedResponder(36, "N tube close", netForce=1)

sTubeEntry = ptAttribNamedActivator(37, "S tube entry trigger")
nTubeEntry = ptAttribNamedActivator(38, "N tube entry trigger")

sTubeMulti = ptAttribBehavior(43, "s tube entry multi", netForce=0)
nTubeMulti = ptAttribBehavior(44, "n tube entry multi", netForce=0)

sTubeExclude = ptAttribExcludeRegion(45, "s tube exclude")
nTubeExclude = ptAttribExcludeRegion(46, "n tube exclude")

sTeamWarpPt = ptAttribSceneobject(47, "s team warp point")
nTeamWarpPt = ptAttribSceneobject(48, "n team warp point")

sTeamWin = ptAttribActivator(49, "s team win")
nTeamWin = ptAttribActivator(50, "n team win")

sTeamQuit = ptAttribActivator(51, "s team quit")
nTeamQuit = ptAttribActivator(52, "n team quit")

sTeamWinTeleport = ptAttribSceneobject(53, "s team win point")
nTeamWinTeleport = ptAttribSceneobject(54, "n team win point")

nQuitBehavior = ptAttribBehavior(55, "s quit behavior")
sQuitBehavior = ptAttribBehavior(56, "n quit behavior")

# sfx responders

nPanelSound = ptAttribResponder(57, "n panel sound", ['main', 'up', 'down', 'select', 'blockerOn', 'blockerOff', 'gameStart', 'denied'], netForce=1)
sPanelSound = ptAttribResponder(58, "s panel sound", ['main', 'up', 'down', 'select', 'blockerOn', 'blockerOff', 'gameStart', 'denied'], netForce=1)


##############################################################
# grsnWallPython
##############################################################

## globals

## for team light responders
kTeamLightsOn = 0
kTeamLightsOff = 1
kRedOn = 3
kRedOff = 4
kRedFlash = 2

## for go button light states
kDim = 0
kBright = 1
kPulse = 2
##

## game states

kWaiting = 0
kNorthSit = 1
kSouthSit = 2
kNorthSelect = 3
kSouthSelect = 4
kNorthReady = 5
kSouthReady = 6
kNorthPlayerEntry = 7
kSouthPlayerEntry = 8
kGameInProgress = 9
kNorthWin = 10
kSouthWin = 11
kNorthQuit = 12
kSouthQuit = 13

## sdl replacements
"""
SouthState = ptClimbingWallMsgState.kWaiting
NorthState = ptClimbingWallMsgState.kWaiting
"""

# uncomment to enable wall code using ageSDLs
"""
SouthState = kWaiting
NorthState = kWaiting
"""

NorthCount = 0
BlockerCountLimit = 0
SouthCount = 0
NorthWall = [-1]*20
SouthWall = [-1]*20
ReceiveInit = false
NorthBlockers = []
SouthBlockers = []


class grsnWallPython(ptResponder):

    def __init__(self):
        "construction"
        ptResponder.__init__(self)
        self.id = 52392
        version = 4
        minor = 0
        self.version = "{}.{}".format(version, minor)
        PtDebugPrint("__init__: grsnWallPython v{}".format(self.version))

# uncomment to enable wall code using ageSDLs
"""
    def LookupIndex(self, index, north):
        global NorthWall
        global SouthWall
        global BlockerCountLimit

        i = 0
        PtDebugPrint("grsnWallPython.LookupIndex():  index = {}, north = {}".format(index, north))
        if north:
            while i < BlockerCountLimit:
                if NorthWall[i] == index:
                    PtDebugPrint("grsnWallPython.LookupIndex():  index found in north list in slot {}".format(i))
                    return true
                PtDebugPrint("grsnWallPython.LookupIndex():  north wall [{}] = {}".format(i, NorthWall[i]))
                i = i + 1
        else:
            while i < BlockerCountLimit:
                if (SouthWall[i] == index):
                    PtDebugPrint("grsnWallPython.LookupIndex():  index found in south list in slot {}".format(i))
                    return true
                PtDebugPrint("grsnWallPython.LookupIndex():  south wall [{}] = {}".format(i, SouthWall[i]))
                i = i + 1

        PtDebugPrint("grsnWallPython.LookupIndex():  index not found")
        return false

    def SetWallIndex(self, index, value, north):
        PtDebugPrint("grsnWallPython.SetWallIndex():  index = {}, value = {}, north = {}".format(index, value, north))
        global NorthWall
        global SouthWall
        global SouthCount
        global NorthCount

        ageSDL = PtGetAgeSDL()

        i = 0
        if value:
            if north:
                while NorthWall[i] >= 0:
                    i = i + 1
                    if i == 20:
                        PtDebugPrint("grsnWallPython.SetWallIndex():  yikes - somehow overran the array!")
                        return
                NorthWall[i] = index
                ageSDL.setIndex("northWall", i, index)
                NorthCount = NorthCount + 1
                PtDebugPrint("grsnWallPython.SetWallIndex():  set north wall index {} in slot {} to true".format(index, i))
            else:
                while SouthWall[i] >= 0:
                    i = i + 1
                    if (i == 20):
                        PtDebugPrint("grsnWallPython.SetWallIndex():  yikes - somehow overran the array!")
                        return
                SouthWall[i] = index
                ageSDL.setIndex("southWall", i, index)
                SouthCount = SouthCount + 1
                PtDebugPrint("grsnWallPython.SetWallIndex():  set south wall index {} in slot {} to true".format(index, i))
        else:
            if north:
                while NorthWall[i] != index:
                    i = i + 1
                    if i == 20:
                        PtDebugPrint("grsnWallPython.SetWallIndex():  this should not get hit - looked for non-existent NorthWall entry!")
                        return
                NorthWall[i] = -1
                ageSDL.setIndex("northWall", i, -1)
                NorthCount = NorthCount - 1
                PtDebugPrint("grsnWallPython.SetWallIndex():  removed index {} from list slot {}".format(index, i))
            else:
                while SouthWall[i] != index:
                    i = i + 1
                    if i == 20:
                        PtDebugPrint("grsnWallPython.SetWallIndex():  this should not get hit - looked for non-existent SouthWall entry!")
                        return
                SouthWall[i] = -1
                ageSDL.setIndex("southWall", i, -1)
                SouthCount = SouthCount - 1
                PtDebugPrint("grsnWallPython.SetWallIndex():  removed index {} from list slot {}".format(index, i))

    def ClearIndices(self, north):
        global NorthWall
        global SouthWall
        global NorthCount
        global SouthCount
        i = 0
        while (i < 171):
            if (i < 20):
                if north:
                    NorthWall[i] = -1
                else:
                    SouthWall[i] = -1

            if north:
                northLights.value[i].runAttachedResponder(kTeamLightsOff)
            else:
                southLights.value[i].runAttachedResponder(kTeamLightsOff)
            i = i + 1

        if north:
            PtDebugPrint("grsnWallPython.ClearIndices():  cleared north indices")
            NorthCount = 0
        else:
            PtDebugPrint("grsnWallPython.ClearIndices():  cleared south indices")
            SouthCount = 0

    def SetSPanelMode(self, state):
        global NorthState
        global SouthState
        global NorthCount
        global SouthCount
        global BlockerCountLimit
        global NorthWall
        global SouthWall

        PtDebugPrint("grsnWallPython.SetSPanelMode():  called with state {}".format(state))
        if state == kWaiting:
            PtDebugPrint("grsnWallPython.SetSPanelMode():  Waiting for south player")
            # turn everything off
            self.ResetSouthPanel(false)
            self.ClearIndices(false)
            sTubeExclude.clear(self.key)
            sTubeClose.run(self.key, avatar=PtGetLocalAvatar())

        elif state == kSouthSit:
            PtDebugPrint("grsnWallPython.SetSPanelMode():  Player sat in south chair")
            # set go button to bright
            goBtnSObject.value.runAttachedResponder(kBright)

        elif state == kSouthSelect:
            PtDebugPrint("grsnWallPython.SetSPanelMode():  Enabling south panel")
            self.ClearIndices(false)
            # make all of the counter lights flash
            i = 0
            while i < 20:
                southCountLights.value[i].runAttachedResponder(kRedFlash)
                i = i + 1
            # enable up / down buttons
            upButtonS.enable()
            dnButtonS.enable()
            readyButtonS.enable()
            fiveBtnS.enable()
            tenBtnS.enable()
            fifteenBtnS.enable()

        elif state == kSouthReady:
            PtDebugPrint("grsnWallPython.SetSPanelMode():  South panel set up")
            # turn unselected count lights solid, and turn off the other lights
            i = 0
            while i < BlockerCountLimit:
                southCountLights.value[i].runAttachedResponder(kTeamLightsOff)
                i = i + 1
            i = BlockerCountLimit
            while i < 20:
                southCountLights.value[i].runAttachedResponder(kRedOn)
                i = i + 1
            # disable adjustment buttons
            upButtonS.disable()
            dnButtonS.disable()
            readyButtonS.disable()
            fiveBtnS.disable()
            tenBtnS.disable()
            fifteenBtnS.disable()

        elif state == kSouthPlayerEntry:
            PtDebugPrint("grsnWallPython.SetSPanelMode():  South player waiting to enter tube")
            # disable all panel buttons
            self.EnableSouthButtons(false)
            # run responder to open tube
            if NorthState == kNorthPlayerEntry:
                sTubeOpen.run(self.key, avatar=PtGetLocalAvatar())
                goBtnSObject.value.runAttachedResponder(kBright)
                nTubeOpen.run(self.key, avatar=PtGetLocalAvatar())
                goBtnNObject.value.runAttachedResponder(kBright)
                PtDebugPrint("grsnWallPython.SetSPanelMode():  North player ready... tubes open")

    def SetNPanelMode(self, state):
        global NorthState
        global SouthState
        global NorthCount
        global SouthCount
        global BlockerCountLimit
        global NorthWall
        global SouthWall

        PtDebugPrint("grsnWallPython.SetNPanelMode():  called with state {}".format(state))
        if state == kWaiting:
            PtDebugPrint("grsnWallPython.SetNPanelMode():  Waiting for north player")
            # turn everything off
            self.ResetNorthPanel(false)
            self.ClearIndices(true)
            nTubeExclude.clear(self.key)
            nTubeClose.run(self.key, avatar=PtGetLocalAvatar())
            goBtnNObject.value.runAttachedResponder(kDim)

        elif state == kNorthSit:
            PtDebugPrint("grsnWallPython.SetNPanelMode():  Player sat in north chair")
            # set go button to bright
            goBtnNObject.value.runAttachedResponder(kBright)

        elif state == kNorthSelect:
            PtDebugPrint("grsnWallPython.SetNPanelMode():  Enabling north panel")
            self.ClearIndices(true)
            # make all of the counter lights flash
            i = 0
            while i < 20:
                northCountLights.value[i].runAttachedResponder(kRedFlash)
                i = i + 1
            # enable up / down buttons
            upButtonN.enable()
            dnButtonN.enable()
            readyButtonN.enable()
            fiveBtnN.enable()
            tenBtnN.enable()
            fifteenBtnN.enable()
            goBtnNObject.value.runAttachedResponder(kDim)

        elif state == kNorthReady:
            PtDebugPrint("grsnWallPython.SetNPanelMode():  North panel set up")
            # turn unselected count lights solid, and turn off the other lights
            i = 0
            while i < BlockerCountLimit:
                northCountLights.value[i].runAttachedResponder(kTeamLightsOff)
                i = i + 1
            i = BlockerCountLimit
            while i < 20:
                northCountLights.value[i].runAttachedResponder(kRedOn)
                i = i + 1
            #disable adjustment buttons
            upButtonN.disable()
            dnButtonN.disable()
            readyButtonN.disable()
            fiveBtnN.disable()
            tenBtnN.disable()
            fifteenBtnN.disable()
            goBtnNObject.value.runAttachedResponder(kRedFlash)

        elif state == kNorthPlayerEntry:
            PtDebugPrint("grsnWallPython.SetNPanelMode():  North player waiting to enter tube")
            #disable all panel buttons
            self.EnableNorthButtons(false)
            #run responder to open tube
            if SouthState == kSouthPlayerEntry:
                sTubeOpen.run(self.key, avatar=PtGetLocalAvatar())
                goBtnSObject.value.runAttachedResponder(kBright)
                nTubeOpen.run(self.key, avatar=PtGetLocalAvatar())
                goBtnNObject.value.runAttachedResponder(kBright)
                PtDebugPrint("grsnWallPython.SetNPanelMode():  South player ready... tubes open")

    def IAmMaster(self):
        return (self.sceneobject.isLocallyOwned())

    def ChangeGameState(self, newState):
        PtDebugPrint("grsnWallPython.ChangeGameState():  sending change game state message with state {}".format(newState))
        ageSDL = PtGetAgeSDL()
        if newState in [1, 3, 5, 7, 10, 12]:
            ageSDL["nState"] = (newState,)
        elif newState in [2, 4, 6, 8, 11, 13]:
            ageSDL["sState"] = (newState,)
        else:
            ageSDL["nState"] = (newState,)
            ageSDL["sState"] = (newState,)

    def ChangeBlockerCount(self, newCount):
        PtDebugPrint("grsnWallPython.ChangeBlockerCount():  sending change blocker count message with new count ".format(newCount))
        ageSDL = PtGetAgeSDL()
        ageSDL["NumBlockers"] = (newCount,)

    def ZeroBlockerCount(self):
        ageSDL = PtGetAgeSDL()
        PtDebugPrint("grsnWallPython.ZeroBlockerCount():  sending change blocker count message with new count 0")
        ageSDL["NumBlockers"] = (0,)

    def ChangeBlockerState(self, on, index, north):
        PtDebugPrint("grsnWallPython.ChangeBlockerState():  sending change blocker state message with team {}, index {} and on {}".format(north, index, on))
        ageSDL = PtGetAgeSDL()
        if (north):
            ageSDL["nBlockerChange"] = (index, on,)
        else:
            ageSDL["sBlockerChange"] = (index, on,)

    def RequestGameState(self):
        PtDebugPrint("grsnWallPython.RequestGameState():")
        global NorthState
        global SouthState
        global BlockerCountLimit
        ageSDL = PtGetAgeSDL()

        NorthState = ageSDL["nState"][0]
        SouthState = ageSDL["sState"][0]
        BlockerCountLimit = ageSDL["NumBlockers"][0]
        for blocker in ageSDL["northWall"]:
            if blocker >= 0:
                self.SetWallIndex(blocker, true, true)  # this updates NorthWall and NorthCount for us
                self.ChangeNorthBlocker(blocker)
        for blocker in ageSDL["southWall"]:
            if blocker >= 0:
                self.SetWallIndex(blocker, true, false)  # this updates SouthWall and SouthCount for us
                self.ChangeSouthBlocker(blocker)
        ### synchronise client with current game state ###
        self.SetNPanelMode(NorthState)
        self.SetSPanelMode(SouthState)

    def OnServerInitComplete(self):
        global ReceiveInit

        PtDebugPrint("grsnWallPython.OnServerInitComplete():  running...")
        solo = true
        ageSDL = PtGetAgeSDL()

        if len(PtGetPlayerList()):
            solo = false
            ReceiveInit = true

            sTubeClose.run(self.key, fastforward=true, netForce=0)
            nTubeClose.run(self.key, fastforward=true, netForce=0)
        else:
            PtDebugPrint("grsnWallPython.OnServerInitComplete():  solo in climbing wall")

        i = 0  # reset Wall Physics
        while i < 171:
            southWall.value[i].physics.disable()
            northWall.value[i].physics.disable()
            i = i + 1

        # Set flags, notifies, and tell the clients
        ageSDL.setFlags("nChairOccupant", 0, 1)
        ageSDL.setFlags("sChairOccupant", 0, 1)
        ageSDL.setFlags("nState", 0, 1)
        ageSDL.setFlags("sState", 0, 1)
        ageSDL.setFlags("NumBlockers", 0, 1)
        ageSDL.setFlags("nBlockerChange", 0, 1)
        ageSDL.setFlags("sBlockerChange", 0, 1)
        ageSDL.setFlags("northWall", 0, 1)
        ageSDL.setFlags("southWall", 0, 1)

        ageSDL.setNotify(self.key, "nChairOccupant", 0.0)
        ageSDL.setNotify(self.key, "sChairOccupant", 0.0)
        ageSDL.setNotify(self.key, "nState", 0.0)
        ageSDL.setNotify(self.key, "sState", 0.0)
        ageSDL.setNotify(self.key, "NumBlockers", 0.0)
        ageSDL.setNotify(self.key, "nBlockerChange", 0.0)
        ageSDL.setNotify(self.key, "sBlockerChange", 0.0)

        ageSDL.sendToClients("nChairOccupant")
        ageSDL.sendToClients("sChairOccupant")
        ageSDL.sendToClients("nState")
        ageSDL.sendToClients("sState")
        ageSDL.sendToClients("NumBlockers")
        ageSDL.sendToClients("nBlockerChange")
        ageSDL.sendToClients("sBlockerChange")
        ageSDL.sendToClients("northWall")
        ageSDL.sendToClients("southWall")

        if (solo):
            ageSDL["northWall"] = (-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,)
            ageSDL["southWall"] = (-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,)
            self.ResetSouthPanel(false)
            self.ResetNorthPanel(false)
            sTubeClose.run(self.key)
            nTubeClose.run(self.key)
            ageSDL.setIndex("nChairOccupant", 0, -1)
            ageSDL.setIndex("sChairOccupant", 0, -1)
            ageSDL.setIndex("nWallPlayer", 0, -1)
            ageSDL.setIndex("sWallPlayer", 0, -1)
            ageSDL.setIndex("nState", 0, 0)
            ageSDL.setIndex("sState", 0, 0)
            SouthState = kWaiting
            NorthState = kWaiting
        else:
            PtDebugPrint("grsnWallPython.OnServerInitComplete():  requesting game state message from SDL")
            self.RequestGameState()

    def OnSDLNotify(self, VARname, SDLname, playerID, tag):
        global BlockerCountLimit
        global NorthBlockers
        global SouthBlockers
        global NorthState
        global SouthState

        ageSDL = PtGetAgeSDL()
        value = ageSDL[VARname][0]
        PtDebugPrint("grsnWallPython.OnSDLNotify():  VARname = {} SDLname = {} playerID = {} value = {}".format(VARname, SDLname, playerID, value))
        if VARname == "nState":
            PtDebugPrint("grsnWallPython.OnSDLNotify():  North state changed")
            NorthState = ageSDL[VARname][0]
            if NorthState == kNorthReady:
                if PtGetLocalClientID() == ageSDL["nChairOccupant"][0]:
                    PtDebugPrint("grsnWallPython.OnSDLNotify():  north Player ready... Enable BlockerMarkers for north")
                    self.EnableNorthButtons(True)
            self.SetNPanelMode(NorthState)

        elif VARname == "sState":
            PtDebugPrint("grsnWallPython.OnSDLNotify():  South state changed")
            SouthState = ageSDL[VARname][0]
            if SouthState == kSouthReady:
                if (PtGetLocalClientID() == ageSDL["sChairOccupant"][0]):
                    PtDebugPrint("grsnWallPython.OnSDLNotify():  south Player ready... Enable BlockerMarkers for south")
                    self.EnableSouthButtons(True)
            self.SetSPanelMode(SouthState)

        elif VARname == "NumBlockers":
            PtDebugPrint("grsnWallPython.OnSDLNotify():  Number of Blockers changed")
            BlockerCountLimit = ageSDL[VARname][0]
            self.UpdateBlockerCountDisplay(1)

        elif VARname == "nBlockerChange":
            PtDebugPrint("grsnWallPython.OnSDLNotify():  North blocker changed")
            team = 1
            index = ageSDL[VARname][0]
            on = ageSDL[VARname][1]
            self.SetWallIndex(index, on, team)
            self.ChangeNorthBlocker(index)

        elif VARname == "sBlockerChange":
            PtDebugPrint("grsnWallPython.OnSDLNotify():  South blocker changed")
            team = 0
            index = ageSDL[VARname][0]
            on = ageSDL[VARname][1]
            self.SetWallIndex(index, on, team)
            self.ChangeSouthBlocker(index)

    def UpdateBlockerCountDisplay(self, flash):
        PtDebugPrint("grsnWallPython.UpdateBlockerCountDisplay():  updating Blocker count")
        global BlockerCountLimit

        numSelected = BlockerCountLimit
        i = 0
        while i < numSelected:
            northCountLights.value[i].runAttachedResponder(kTeamLightsOn)
            southCountLights.value[i].runAttachedResponder(kTeamLightsOn)
            i = i + 1
        i = numSelected
        while i < 20:
            northCountLights.value[i].runAttachedResponder(kRedFlash)
            southCountLights.value[i].runAttachedResponder(kRedFlash)
            i = i + 1
        if flash == 0:
            i = 0
            while i < 20:
                northCountLights.value[i].runAttachedResponder(kTeamLightsOff)
                southCountLights.value[i].runAttachedResponder(kTeamLightsOff)
                i = i + 1

    def ChangeSouthBlocker(self, index):
        global BlockerCountLimit
        ageSDL = PtGetAgeSDL()
        # we clicked or un-clicked on a control panel button corresponding to a wall blocker
        wallPicked = southWall.value[index]
        animPicked = southLights.value[index]
        if (self.LookupIndex(index, false)):
            # turn this guy on
            wallPicked.physics.enable()
            if PtGetLocalClientID() == ageSDL["sChairOccupant"][0]:
                animPicked.runAttachedResponder(kTeamLightsOn)
                counterPicked = southCountLights.value[SouthCount - 1]
                counterPicked.runAttachedResponder(kTeamLightsOn)
                sPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='blockerOn')
                PtDebugPrint("grsnWallPython.ChangeSouthBlocker():  turned on south blocker {}".format(index))
        else:
            wallPicked.physics.disable()
            if PtGetLocalClientID() == ageSDL["sChairOccupant"][0]:
                animPicked.runAttachedResponder(kTeamLightsOff)
                counterPicked = southCountLights.value[SouthCount]
                counterPicked.runAttachedResponder(kTeamLightsOff)
                sPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='blockerOff')
                PtDebugPrint("grsnWallPython.ChangeSouthBlocker():  turned off south blocker {}".format(index))
        return

    def ChangeNorthBlocker(self, index):
        global BlockerCountLimit
        ageSDL = PtGetAgeSDL()
        # we clicked or un-clicked on a control panel button corresponding to a wall blocker
        wallPicked = northWall.value[index]
        animPicked = northLights.value[index]
        if (self.LookupIndex(index, true)):
            # turn this guy on
            wallPicked.physics.enable()
            if (PtGetLocalClientID() == ageSDL["nChairOccupant"][0]):
                animPicked.runAttachedResponder(kTeamLightsOn)
                counterPicked = northCountLights.value[NorthCount - 1]
                counterPicked.runAttachedResponder(kTeamLightsOn)
                nPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='blockerOn')
                PtDebugPrint("grsnWallPython.ChangeNorthBlocker():  turned on north blocker {}".format(index))
        else:
            wallPicked.physics.disable()
            if (PtGetLocalClientID() == ageSDL["nChairOccupant"][0]):
                animPicked.runAttachedResponder(kTeamLightsOff)
                counterPicked = northCountLights.value[NorthCount]
                counterPicked.runAttachedResponder(kTeamLightsOff)
                nPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='blockerOff')
                PtDebugPrint("grsnWallPython.ChangeNorthBlocker():  turned off north blocker {}".format(index))
        return

    def EnableSouthButtons(self, enable):

        i = 0
        while i < 171:
            if enable:
                southPanel.value[i].physics.enable()
            else:
                southPanel.value[i].physics.disable()
            i = i + 1

        if enable:
            upButtonS.enable()
            dnButtonS.enable()
            readyButtonS.enable()
            fiveBtnS.enable()
            tenBtnS.enable()
            fifteenBtnS.enable()
            PtDebugPrint("grsnWallPython.EnableSouthButtons():  enabled south buttons")
        else:
            upButtonS.disable()
            dnButtonS.disable()
            readyButtonS.disable()
            fiveBtnS.disable()
            tenBtnS.disable()
            fifteenBtnS.disable()
            PtDebugPrint("grsnWallPython.EnableSouthButtons():  disabled south buttons")

    def EnableNorthButtons(self, enable):

        i = 0
        while i < 171:
            if (enable):
                northPanel.value[i].physics.enable()
            else:
                northPanel.value[i].physics.disable()
            i = i + 1

        if (enable):
            upButtonN.enable()
            dnButtonN.enable()
            readyButtonN.enable()
            fiveBtnN.enable()
            tenBtnN.enable()
            fifteenBtnN.enable()
            PtDebugPrint("grsnWallPython.EnableNorthButtons():  enabled north buttons")
        else:
            upButtonN.disable()
            dnButtonN.disable()
            readyButtonN.disable()
            fiveBtnN.disable()
            tenBtnN.disable()
            fifteenBtnN.disable()
            PtDebugPrint("grsnWallPython.EnableNorthButtons():  disabled north buttons")

    def ResetSouthPanel(self, enable):
        global SouthCount

        self.EnableSouthButtons(enable)
        ageSDL = PtGetAgeSDL()
        PtDebugPrint("grsnWallPython.ResetSouthPanel():  resetting south panel")
        if enable:
            PtDebugPrint("grsnWallPython.ResetSouthPanel():  enabled south wall - this should not happen")
        i = 0
        while i < 171:
            southLights.value[i].runAttachedResponder(kTeamLightsOff)
            if i < 20:
                southCountLights.value[i].runAttachedResponder(kTeamLightsOff)

            if enable == 0:
                southWall.value[i].physics.disable()
            i = i + 1

        self.ZeroBlockerCount()
        SouthCount = 0
        goBtnSObject.value.runAttachedResponder(kDim)

    def ResetNorthPanel(self, enable):
        global NorthCount

        self.EnableNorthButtons(enable)
        ageSDL = PtGetAgeSDL()
        PtDebugPrint("grsnWallPython.ResetNorthPanel():  resetting north panel")
        if enable:
            PtDebugPrint("grsnWallPython.ResetNorthPanel():  enabled north wall - this should not happen")
        i = 0
        while i < 171:
            northLights.value[i].runAttachedResponder(kTeamLightsOff)
            if i < 20:
                northCountLights.value[i].runAttachedResponder(kTeamLightsOff)

            if enable == 0:
                northWall.value[i].physics.disable()
            i = i + 1

        self.ZeroBlockerCount()
        NorthCount = 0
        goBtnNObject.value.runAttachedResponder(kDim)

    def OnTimer(self, id):
        avatar = PtGetLocalAvatar()
        if id == kNorthQuit:
            PtDebugPrint("grsnWallPythom.OnTimer():  north quit")
            PtFakeLinkAvatarToObject(avatar.getKey(), sTeamWinTeleport.value.getKey())
            self.ChangeGameState(kSouthQuit)
            self.ChangeGameState(kNorthWin)
            PtAtTimeCallback(self.key, 2, kNorthWin)
        elif (id == kSouthQuit):
            PtDebugPrint("grsnWallPythom.OnTimer():  south quit")
            PtFakeLinkAvatarToObject(avatar.getKey(), nTeamWinTeleport.value.getKey())
            self.ChangeGameState(kSouthWin)
            self.ChangeGameState(kNorthQuit)
            PtAtTimeCallback(self.key, 2, kSouthWin)
        elif (id == kNorthWin):
            PtDebugPrint("grsnWallPythom.OnTimer():  north wins")
            PtGetLocalAvatar().avatar.exitSubWorld()
        elif (id == kSouthWin):
            PtDebugPrint("grsnWallPythom.OnTimer():  south wins")
            PtGetLocalAvatar().avatar.exitSubWorld()

    def OnNotify(self, state, id, events):
        global NorthState
        global SouthState
        global NorthCount
        global SouthCount
        global BlockerCountLimit
        global NorthWall
        global SouthWall
        global nTrigger
        global sTrigger

        PtDebugPrint("grsnWallPython.OnNotify():   state = {}, id = {}, events = {}".format(state, id, events))
        ageSDL = PtGetAgeSDL()
        avatar = PtFindAvatar(events)
        southState = SouthState
        northState = NorthState
        PtDebugPrint("grsnWallPython.OnNotify():   southState = {}".format(southState))
        PtDebugPrint("grsnWallPython.OnNotify():   northState = {}".format(northState))

        # responder / behavior notifications

        if id == sQuitBehavior.id:
            for event in events:
                if (event[0] == kMultiStageEvent and event[1] == 0 and event[2] == kEnterStage):
                    PtDebugPrint("grsnWallPython.OnNotify():   start touching quit jewel (s), warp out")
                    if (avatar == PtGetLocalAvatar()):
                        PtAtTimeCallback(self.key, 0.8, kSouthQuit)
                    return

        if id == nQuitBehavior.id:
            for event in events:
                if (event[0] == kMultiStageEvent and event[1] == 0 and event[2] == kEnterStage):
                    PtDebugPrint("grsnWallPython.OnNotify():   start touching quit jewel (n), warp out")
                    if (avatar == PtGetLocalAvatar()):
                        PtAtTimeCallback(self.key, 0.8, kNorthQuit)
                    return

        if id == nTubeOpen.id:
            PtDebugPrint("grsnWallPython.OnNotify():   tube finished opening")
            nTubeExclude.release(self.key)

        if id == nTubeMulti.id:
            for event in events:
                PtDebugPrint("grsnWallPython.OnNotify():  got nTubeMulti.id: event[0] = {} event[1] = {} event[2] = {}".format(event[0], event[1], event[2]))
                if event[0] == kMultiStageEvent and event[1] == 0 and event[2] == kEnterStage:
                    PtDebugPrint("grsnWallPython.OnNotify():  Smart seek completed. close tube")
                    nTubeClose.run(self.key, avatar=avatar)
                elif event[0] == kMultiStageEvent and event[1] == 0 and event[2] == kAdvanceNextStage:
                    PtDebugPrint("grsnWallPython.OnNotify():  multistage complete, warp to wall south room with suit")
                    if avatar == PtGetLocalAvatar():
                        PtWearMaintainerSuit(PtGetLocalAvatar().getKey(), true)
                        PtSendKIMessage(kDisableEntireYeeshaBook, 0)
                    avatar.physics.warpObj(sTeamWarpPt.value.getKey())

        if id == sTubeOpen.id:
            PtDebugPrint("grsnWallPython.OnNotify():  tube finished opening")
            sTubeExclude.release(self.key)

        if id == sTubeMulti.id:
            for event in events:
                PtDebugPrint("grsnWallPython.OnNotify():  got nTubeMulti.id: event[0] = {} event[1] = {} event[2] = {}".format(event[0], event[1], event[2]))
                if event[0] == kMultiStageEvent and event[1] == 0 and event[2] == kEnterStage:
                    PtDebugPrint("grsnWallPython.OnNotify():  Smart seek completed. close tube")
                    sTubeClose.run(self.key, avatar=avatar)
                elif event[0] == kMultiStageEvent and event[1] == 0 and event[2] == kAdvanceNextStage:
                    PtDebugPrint("grsnWallPython.OnNotify():  multistage complete, warp to wall north room with suit")
                    if (avatar == PtGetLocalAvatar()):
                        PtWearMaintainerSuit(PtGetLocalAvatar().getKey(), true)
                        PtSendKIMessage(kDisableEntireYeeshaBook, 0)
                    avatar.physics.warpObj(nTeamWarpPt.value.getKey())

        # activator notifications
        if id == sTeamWin.id and PtGetLocalAvatar() == PtFindAvatar(events):
            PtDebugPrint("grsnWallPython.OnNotify():  south wins")
            PtFakeLinkAvatarToObject(avatar.getKey(), sTeamWinTeleport.value.getKey())
            self.ChangeGameState(kSouthWin)
            self.ChangeGameState(kNorthQuit)
            PtAtTimeCallback(self.key, 9, kSouthWin)

        if id == nTeamWin.id and PtGetLocalAvatar() == PtFindAvatar(events):
            PtDebugPrint("grsnWallPython.OnNotify():  north wins")
            PtFakeLinkAvatarToObject(avatar.getKey(), nTeamWinTeleport.value.getKey())
            self.ChangeGameState(kNorthWin)
            self.ChangeGameState(kSouthQuit)
            PtAtTimeCallback(self.key, 9, kNorthWin)

        if id == nTeamQuit.id and state:
            avatar.avatar.runBehaviorSetNotify(nQuitBehavior.value, self.key, nQuitBehavior.netForce)
            self.ChangeGameState(kNorthQuit)
            self.ChangeGameState(kSouthWin)
            nTrigger = avatar
            return

        if id == sTeamQuit.id and state:
            avatar.avatar.runBehaviorSetNotify(sQuitBehavior.value, self.key, sQuitBehavior.netForce)
            self.ChangeGameState(kNorthWin)
            self.ChangeGameState(kSouthQuit)
            sTrigger = avatar
            return

        if id == southChair.id:
            PtDebugPrint("grsnWallPython.OnNotify():  clicked south chair")
            avID = PtGetClientIDFromAvatarKey(avatar.getKey())
            if state:
                occupant = ageSDL["sChairOccupant"][0]
                PtDebugPrint("grsnWallPython.OnNotify():  occupant {}".format(occupant))
                if avID == PtGetClientIDFromAvatarKey(PtGetLocalAvatar().getKey()):
                    PtDebugPrint("grsnWallPython.OnNotify():  sitting down in south chair")
                    southChair.disable()
                    ageSDL.setIndex("sChairOccupant", 0, avID)
                    if (southState == kWaiting or southState == kSouthWin or southState == kSouthQuit):
                        self.ChangeGameState(kSouthSit)
                    return

        if id == sChairSit.id:
            for event in events:
                if event[0] == 6 and event[1] == 1 and state == 0:
                    if (1):
                        PtDebugPrint("grsnWallPython.OnNotify():  standing up from south chair")
                        southChair.enable()
                        ageSDL.setIndex("sChairOccupant", 0, -1)
                    return

        if id == northChair.id:
            PtDebugPrint("grsnWallPython.OnNotify():  clicked north chair")
            avID = PtGetClientIDFromAvatarKey(avatar.getKey())
            if state:
                occupant = ageSDL["nChairOccupant"][0]
                PtDebugPrint("grsnWallPython.OnNotify():  occupant {}".format(occupant))
                if avID == PtGetClientIDFromAvatarKey(PtGetLocalAvatar().getKey()):
                    PtDebugPrint("grsnWallPython.OnNotify():  sitting down in north chair")
                    northChair.disable()
                    ageSDL.setIndex("nChairOccupant", 0, avID)
                    if (northState == kWaiting or northState == kNorthWin or northState == kNorthQuit):
                        self.ChangeGameState(kNorthSit)
                    return

        if id == nChairSit.id:
            for event in events:
                if event[0] == 6 and event[1] == 1 and state == 0:
                    if (1):
                        PtDebugPrint("grsnWallPython.OnNotify():  standing up from north chair")
                        northChair.enable()
                        ageSDL.setIndex("nChairOccupant", 0, -1)
                    return
        elif not state:
            return

        if avatar != PtGetLocalAvatar():
            PtDebugPrint("grsnWallPython.OnNotify():  not activated by me")
            return  # jump out if this is not my event

        if id == nTubeEntry.id:
            nTrigger = PtFindAvatar(events)
            PtDebugPrint("grsnWallPython.OnNotify():  entered team 1 tube, run behavior")
            ageSDL.setIndex("nWallPlayer", 0, PtGetClientIDFromAvatarKey(avatar.getKey()))
            avatar.avatar.runBehaviorSetNotify(nTubeMulti.value, self.key, nTubeMulti.netForce)

        if id == sTubeEntry.id:
            sTrigger = PtFindAvatar(events)
            PtDebugPrint("grsnWallPython.OnNotify():  entered team 2 tube, run behavior")
            ageSDL.setIndex("sWallPlayer", 0, PtGetClientIDFromAvatarKey(avatar.getKey()))
            avatar.avatar.runBehaviorSetNotify(sTubeMulti.value, self.key, sTubeMulti.netForce)

        if id == upButtonS.id:
            PtDebugPrint("grsnWallPython.OnNotify():  up button south")
            if (southState == kSouthSelect):
                PtDebugPrint("grsnWallPython.OnNotify():  correct state, blocker count limit {}".format(BlockerCountLimit))
                if (BlockerCountLimit < 20):
                    self.ChangeBlockerCount(BlockerCountLimit + 1)
                    sPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='up')
                else:
                    PtDebugPrint("grsnWallPython.OnNotify():  somehow think blocker count limit greater than 20?")
            return

        elif id == dnButtonS.id:
            PtDebugPrint("grsnWallPython.OnNotify():  down button south")
            if southState == kSouthSelect:
                if BlockerCountLimit > 0:
                    self.ChangeBlockerCount(BlockerCountLimit - 1)
                    sPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='down')

            return

        elif id == fiveBtnS.id:
            PtDebugPrint("grsnWallPython.OnNotify():  five button south")
            if southState == kSouthSelect:
                self.ChangeBlockerCount(5)
                sPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='up')
            return

        elif id == tenBtnS.id:
            PtDebugPrint("grsnWallPython.OnNotify():  ten button south")
            if southState == kSouthSelect:
                self.ChangeBlockerCount(10)
                sPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='up')
            return

        elif id == fifteenBtnS.id:
            print"fifteen button south"
            if (southState == kSouthSelect):
                self.ChangeBlockerCount(15)
                sPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='up')
            return

        elif id == readyButtonS.id:
            PtDebugPrint("grsnWallPython.OnNotify():  ready button south")
            if southState == kSouthSelect:
                self.ChangeGameState(kSouthReady)
                sPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='select')
                if northState == kNorthSelect:
                    self.ChangeGameState(kNorthReady)
            else:
                sPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='denied')

            return

        elif id == goButtonS.id:
            PtDebugPrint("grsnWallPython.OnNotify():  picked s go button")
            if southState == kSouthSit:
                PtDebugPrint("grsnWallPython.OnNotify():  set state to kSouthSelect")
                self.ClearIndices(false)
                self.ChangeGameState(kSouthSelect)
                sPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='main')
                note = ptNotify(self.key)
                note.clearReceivers()
                note.addReceiver(self.key)
                note.setActivate(1)
                note.netForce(1)
                note.addVarKey('Reset', PtGetLocalAvatar().getKey())
                note.send()  # sending Blocker reset
                if (northState == kWaiting or northState == kNorthSit or northState == kNorthWin or northState == kNorthQuit):
                    PtDebugPrint("grsnWallPython.OnNotify():  force north chair to keep up")
                    self.ChangeGameState(kNorthSelect)

            elif southState == kSouthReady:
                PtDebugPrint("grsnWallPython.OnNotify():  check to see if you've used all your wall blockers")
                numSelected = SouthCount
                maxSelections = BlockerCountLimit
                PtDebugPrint("grsnWallPython.OnNotify():  numSelected = {}, maxSelections = {}".format(numSelected, BlockerCountLimit))
                if numSelected < maxSelections:
                    sPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='denied')
                else:
                    self.ChangeGameState(kSouthPlayerEntry)
                    sPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='gameStart')
            return

        if id == upButtonN.id:
            PtDebugPrint("grsnWallPython.OnNotify():  up button north")
            if (northState == kNorthSelect):
                numSelected = BlockerCountLimit
                if numSelected < 20:
                    numSelected = numSelected + 1
                    self.ChangeBlockerCount(numSelected)
                    nPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='up')
            return

        elif id == dnButtonN.id:
            PtDebugPrint("grsnWallPython.OnNotify():  down button north")
            if northState == kNorthSelect:
                numSelected = BlockerCountLimit
                if numSelected > 0:
                    numSelected = numSelected - 1
                    self.ChangeBlockerCount(numSelected)
                    nPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='down')
            return

        elif id == fiveBtnN.id:
            PtDebugPrint("grsnWallPython.OnNotify():  five button north")
            if northState == kNorthSelect:
                self.ChangeBlockerCount(5)
                nPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='up')
            return

        elif id == tenBtnN.id:
            PtDebugPrint("grsnWallPython.OnNotify():  ten button north")
            if northState == kNorthSelect:
                self.ChangeBlockerCount(10)
                nPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='up')
            return

        elif id == fifteenBtnN.id:
            PtDebugPrint("grsnWallPython.OnNotify():  fifteen button north")
            if northState == kNorthSelect:
                self.ChangeBlockerCount(15)
                nPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='up')
            return

        elif id == readyButtonN.id:
            PtDebugPrint("grsnWallPython.OnNotify():  ready button north")
            if northState == kNorthSelect:
                self.ChangeGameState(kNorthReady)
                nPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='select')
                if southState == kSouthSelect:
                    self.ChangeGameState(kSouthReady)
                    PtDebugPrint("grsnWallPython.OnNotify():  force south chair to keep up")
            else:
                nPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='denied')
            return

        elif id == goButtonN.id:
            PtDebugPrint("grsnWallPython.OnNotify():  picked n go button")
            if northState == kNorthSit:
                PtDebugPrint("grsnWallPython.OnNotify():  set state to kNorthSelect")
                self.ChangeGameState(kNorthSelect)
                self.ClearIndices(true)
                nPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='main')
                note = ptNotify(self.key)
                note.clearReceivers()
                note.addReceiver(self.key)
                note.setActivate(1)
                note.netForce(1)
                note.addVarKey('Reset', PtGetLocalAvatar().getKey())
                note.send()  # sending Blocker reset
                if (southState == kWaiting or southState == kSouthSit or southState == kSouthWin or southState == kSouthWin):
                    self.ChangeGameState(kSouthSelect)
                    PtDebugPrint("grsnWallPython.OnNotify():  force south chair to keep up")

            elif northState == kNorthReady:
                PtDebugPrint("grsnWallPython.OnNotify():  check to see if you've used all your wall blockers")
                numSelected = NorthCount
                maxSelections = BlockerCountLimit
                if numSelected < maxSelections:
                    nPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='denied')
                else:
                    self.ChangeGameState(kNorthPlayerEntry)
                    nPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='gameStart')
            return

        for event in events:
            if event[0] == kPickedEvent and event[1] == 1:
                panelPicked = event[3]
                objName = panelPicked.getName()
                PtDebugPrint("grsnWallPython.OnNotify():  player picked blocker named {}".format(objName))
                north = 0
                if PtGetLocalClientID() == ageSDL["nChairOccupant"][0]:
                    try:
                        index = northPanel.value.index(panelPicked)
                        north = 1
                    except:
                        PtDebugPrint("grsnWallPython.OnNotify():  no wall blocker found")
                        return

                if PtGetLocalClientID() == ageSDL["sChairOccupant"][0]:
                    try:
                        index = southPanel.value.index(panelPicked)
                    except:
                        PtDebugPrint("grsnWallPython.OnNotify():  no wall blocker found")
                        return

                if north:  # you picked something on the north panel
                    if northState != kNorthReady:
                        PtDebugPrint("grsnWallPython.OnNotify():  no blocker picking for you!")
                        nPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='denied')
                        return

                    numSelected = NorthCount
                    PtDebugPrint("grsnWallPython.OnNotify():  numSelected = {}".format(numSelected))
                    maxSelections = BlockerCountLimit

                    if self.LookupIndex(index, true) == 0:
                        if numSelected == maxSelections:
                            PtDebugPrint("grsnWallPython.OnNotify():  you've picked all you can")
                            nPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='denied')
                            return
                        self.ChangeBlockerState(true, index, true)

                    else:
                        numSelected = numSelected - 1
                        if numSelected == -1:
                            PtDebugPrint("grsnWallPython.OnNotify():  what?!?")
                            return
                        self.ChangeBlockerState(false, index, true)

                else:  # you picked one on the south panel
                    if southState != kSouthReady:
                        PtDebugPrint("grsnWallPython.OnNotify():  no blocker picking for you!")
                        sPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='denied')
                        return

                    numSelected = SouthCount
                    PtDebugPrint("grsnWallPython.OnNotify():  numSelected = {}".format(numSelected))
                    maxSelections = BlockerCountLimit

                    if self.LookupIndex(index, false) == 0:
                        if numSelected == maxSelections:
                            PtDebugPrint("grsnWallPython.OnNotify():  you've picked all you can")
                            sPanelSound.run(self.key, avatar=PtGetLocalAvatar(), state='denied')
                            return
                        self.ChangeBlockerState(true, index, false)

                    else:
                        numSelected = numSelected - 1
                        if numSelected == -1:
                            PtDebugPrint("grsnWallPython.OnNotify():  what?!?")
                            return
                        self.ChangeBlockerState(false, index, false)

            elif event[0] == kVariableEvent:
                if event[1] == "Reset":
                    i = 0  # reset Wall Physics
                    while i < 171:
                        northWall.value[i].physics.disable()
                        southWall.value[i].physics.disable()
                        i = i + 1
"""
