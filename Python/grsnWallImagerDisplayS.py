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

# for save/load
#import cPickle  # not used

## COMMENTED OUT by Jeff due to the re-write in the garrison wall

##############################################################
# define the attributes/parameters that we need from the 3dsMax scene
##############################################################
southWall = ptAttribSceneobjectList(2, "South Wall", byObject=1)
##############################################################
# grsnWallImagerDisplayS
##############################################################

ReceiveInit = false

## for team light responders
kTeamLightsOn = 0
kTeamLightsOff = 1

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


class grsnWallImagerDisplayS(ptResponder):

    def __init__(self):
        "construction"
        ptResponder.__init__(self)
        self.id = 52397
        version = 1
        minor = 0
        self.version = "{}.{}".format(version, minor)
        PtDebugPrint("__init__: grsnWallImagerDisplayS v{}".format(self.version))

# uncomment to enable wall code using ageSDLs
"""
    def RequestGameState(self):
        PtDebugPrint("grsnWallImagerDisplayS.RequestGameState():  set blocker lights")
        ageSDL = PtGetAgeSDL()

        for blocker in ageSDL["southWall"]:
            if blocker >= 0:
                southWall.value[blocker].runAttachedResponder(kTeamLightsOn)

    def OnServerInitComplete(self):
        global ReceiveInit

        ageSDL = PtGetAgeSDL()
        PtDebugPrint("grsnWallPython::OnServerInitComplete():  running...")
        solo = true
        if len(PtGetPlayerList()):
            solo = false
            ReceiveInit = true
            self.RequestGameState()
            return
        else:
            PtDebugPrint("grsnWallPython::OnServerInitComplete():  solo in climbing wall")

        ageSDL.setNotify(self.key, "nState", 0.0)
        ageSDL.setNotify(self.key, "sState", 0.0)
        ageSDL.setNotify(self.key, "NumBlockers", 0.0)
        ageSDL.setNotify(self.key, "nBlockerChange", 0.0)
        ageSDL.setNotify(self.key, "sBlockerChange", 0.0)

    def OnSDLNotify(self, VARname, SDLname, playerID, tag):
        global NorthState
        global SouthState

        ageSDL = PtGetAgeSDL()
        value = ageSDL[VARname][0]
        state = value
        PtDebugPrint("grsnWallImagerDisplayS.OnSDLNotify:  VARname = {} SDLname = {} playerID = {} value = {}".format(VARname, SDLname, playerID, value))

        if VARname == "nState" or VARname == "sState":
            if value == kSouthSit or value == kNorthSit:
                i = 0
                while (i < 171):
                    # clear wall settings
                    southWall.value[i].runAttachedResponder(kTeamLightsOff)
                    i = i + 1

        elif VARname == "sBlockerChange":
            index = value
            on = ageSDL[VARname][1]
            if (on):
                southWall.value[state].runAttachedResponder(kTeamLightsOn)
                PtDebugPrint("grsnWallImagerDisplayD.OnSDLNotify:  drawing n wall index".format(state))
            else:
                southWall.value[state].runAttachedResponder(kTeamLightsOff)
                PtDebugPrint("grsnWallImagerDisplayS.OnSDLNotify:  clearing n wall index".format(state))
"""
