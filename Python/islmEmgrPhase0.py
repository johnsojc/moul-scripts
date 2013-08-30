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
Module: islmEmgrPhase0.py
Age: The D'ni City
Date: January 2002
Event Manager interface for the City Phase 0 content
"""

from Plasma import *
from PlasmaTypes import *
import string

# globals
variable = None

BooleanVARs = [
    ]

AgeStartedIn = None

###########################################
# These functions deal with the specific "State" (i.e. Non-boolean) cases. Each is of type INT in the neighborhood.sdl file
#
#Note that the following functions have to be outside of the main class
#in order for the dictionary StateVARs (below) to point to the proper values
###########################################

# This identifies the maximum valid value for INT Variables
# The range is always from 00 to the value specified here
islmDRCStageStateMaxINT = 02


def OutOfRange(VARname, NewSDLValue, myMaxINT):
    PtDebugPrint("islmEmgrPhase0.OutOfRange():  ERROR: Variable {} expected range from  0 - {}. Received value of {}".format(VARname, NewSDLValue, myMaxINT))


def DRCStageState(VARname, NewSDLValue):

    if NewSDLValue > islmDRCStageStateMaxINT:
        OutOfRange(VARname, NewSDLValue, islmDRCStageStateMaxINT)

    elif NewSDLValue == 0:
        PtDebugPrint("islmEmgrPhase0.DRCStageState():  paging out DRC stage")
        PtPageOutNode("islmDRCStageState01")
        PtPageOutNode("islmDRCStageState02")

    elif NewSDLValue == 1:
        PtDebugPrint("islmEmgrPhase0.DRCStageState():  paging in DRC stage")
        PtPageOutNode("islmDRCStageState02")
        PtPageInNode("islmDRCStageState01")

    elif NewSDLValue == 2:
        PtDebugPrint("islmEmgrPhase0.DRCStageState():  paging in deco DRC stage")
        PtPageInNode("islmDRCStageState01")
        PtPageInNode("islmDRCStageState02")

    else:
        PtDebugPrint("islmEmgrPhase0.DRCStageState():  ERROR: Unexpected value. VARname: {} NewSDLValue: {}".format(VARname, NewSDLValue))

StateVARs = {'islmDRCStageState': DRCStageState}


class islmEmgrPhase0(ptResponder):

    def __init__(self):
        ptResponder.__init__(self)
        self.id = 5223

        version = 2
        minor = 0
        self.version = "{}.{}".format(version, minor)
        PtDebugPrint("__init__: islmEmgrPhase0 v{}".format(self.version))

    def OnFirstUpdate(self):
        global AgeStartedIn
        AgeStartedIn = PtGetAgeName()

    def OnServerInitComplete(self):
        if AgeStartedIn == PtGetAgeName():
            ageSDL = PtGetAgeSDL()

            for variable in BooleanVARs:
                PtDebugPrint("islmEmgrPhase0.OnServerInitComplete():  tying together {}".format(variable))
                ageSDL.setNotify(self.key, variable, 0.0)
                self.IManageBOOLs(variable, "")

            for variable in StateVARs.keys():
                PtDebugPrint("islmEmgrPhase0.OnServerInitComplete():  setting notify on {}".format(variable))
                ageSDL.setNotify(self.key, variable, 0.0)
                StateVARs[variable](variable, ageSDL[variable][0])

    def OnSDLNotify(self, VARname, SDLname, PlayerID, tag):
        global variable
        global sdlvalue

        if AgeStartedIn == PtGetAgeName():
            ageSDL = PtGetAgeSDL()
            PtDebugPrint("islmEmgrPhase0.OnSDLNotify():  name = {}, SDLname = {}".format(VARname, SDLname))

            if VARname in BooleanVARs:
                PtDebugPrint("islmEmgrPhase0.OnSDLNotify():  {} is a BOOLEAN Variable".format(VARname))
                self.IManageBOOLs(VARname, SDLname)

            elif VARname in StateVARs.keys():
                PtDebugPrint("islmEmgrPhase0.OnSDLNotify():  {} is a STATE variable".format(VARname))

                NewSDLValue = ageSDL[VARname][0]

                StateVARs[VARname](VARname, NewSDLValue)

            else:
                PtDebugPrint("islmEmgrPhase0.OnSDLNotify():  ERROR: Variable {} was not recognized as a Boolean, Performance, or State Variable.".format(VARname))
                pass

    def IManageBOOLs(self, VARname, SDLname):
        if AgeStartedIn == PtGetAgeName():
            ageSDL = PtGetAgeSDL()
            if ageSDL[VARname][0] == 1:  # are we paging things in?
                PtDebugPrint("islmEmgrPhase0.IManageBOOLs():  Paging in room {}".format(VARname))
                PtPageInNode(VARname)
            elif ageSDL[VARname][0] == 0:  # are we paging things out?
                PtDebugPrint("islmEmgrPhase0.IManageBOOLs():  variable = {}".format(VARname))
                PtDebugPrint("islmEmgrPhase0.IManageBOOLs():  Paging out room {}".format(VARname))
                PtPageOutNode(VARname)
            else:
                sdlvalue = ageSDL[VARname][0]
                PtDebugPrint("islmEmgrPhase0.IManageBOOLs():  ERROR: Variable {} had unexpected SDL value of {}".format(VARname, sdlvalue))
