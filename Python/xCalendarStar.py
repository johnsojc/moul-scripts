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
Module: xCalendarStar
Age: global
Date: November 2006
Author: Chris Doyle
wiring for calendar stars which appear in various ages (aka "blue sparky")
"""

from Plasma import *
from PlasmaTypes import *
from PlasmaKITypes import *
import string
from xPsnlVaultSDL import *

# ---------
# max wiring
# ---------

rgnCalStar = ptAttribActivator(1, "rgn sns: calendar star")
# sdlCalPage = ptAttribString(2, "SDL: calendar YeeshaPage")
sdlCalStar = ptAttribString(3, "SDL: cal stone in Relto")
respCalStar = ptAttribResponder(4, "resp: get star")
boolFirstUpdate = ptAttribBoolean(5, "Eval On First Update?", 0)

# ---------
# globals
# ---------

boolCalStar = false
AgeStartedIn = None


class xCalendarStar(ptResponder):

    def __init__(self):
        ptResponder.__init__(self)
        self.id = 225
        version = 1
        minor = 0
        self.version = "{}.{}".format(version, minor)
        PtDebugPrint("__init__: xCalendarStar v{}".format(self.version))

    def OnFirstUpdate(self):
        global AgeStartedIn
        global boolCalStar

        AgeStartedIn = PtGetAgeName()
        if not (type(sdlCalStar.value) is str and sdlCalStar.value != ""):
            PtDebugPrint("xCalendarStar.OnFirstUpdate():  ERROR: missing SDL var name")
            pass

        if boolFirstUpdate.value:
            if AgeStartedIn == PtGetAgeName():
                psnlSDL = xPsnlVaultSDL()
                try:
                    boolCalStar = psnlSDL[sdlCalStar.value][0]
                except:
                    PtDebugPrint("xCalendarStar.OnFirstUpdate():  ERROR: Error reading age SDL")
                    pass
                PtDebugPrint("xCalendarStar.OnFirstUpdate():  DEBUG: {} = {}".format(sdlCalStar.value, boolCalStar))

    def OnServerInitComplete(self):
        global boolCalStar

        if not boolFirstUpdate.value:
            if AgeStartedIn == PtGetAgeName():
                psnlSDL = xPsnlVaultSDL()
                try:
                    boolCalStar = psnlSDL[sdlCalStar.value][0]
                except:
                    PtDebugPrint("xCalendarStar.OnServerInitComplete():  ERROR: Error reading age SDL")
                    pass
                PtDebugPrint("xCalendarStar.OnServerInitComplete():  DEBUG: {} = {}".format(sdlCalStar.value, boolCalStar))

    def OnNotify(self, state, id, events):
        PtDebugPrint("xCalendarStar.OnNotify():  state = {}, id = {}".format(state, id))
        global boolCalStar

        if not state or id != rgnCalStar.id:
            return

        if PtFindAvatar(events) != PtGetLocalAvatar():
            PtDebugPrint("xCalendarStar.OnNotify():  DEBUG: received notify from non-local player, ignoring...")
            return
        else:
            PtDebugPrint("xCalendarStar.OnNotify():  DEBUG: local player requesting {} change via {}".format(sdlCalStar.value, rgnCalStar.value[0].getName()))

        if not self.GotPage():
            PtDebugPrint("xCalendarStar.OnNotify():  do NOT have YeeshaPage20 (the Calendar Pinnacle) yet")
            return
        else:
            PtDebugPrint("xCalendarStar.OnNotify():  have YeeshaPage20 (the Calendar Pinnacle)")

            if AgeStartedIn == PtGetAgeName():
                psnlSDL = xPsnlVaultSDL()
            if not boolCalStar:
                PtDebugPrint("xCalendarStar.OnNotify():  getting star's stone: {}".format(sdlCalStar.value))
                psnlSDL[sdlCalStar.value] = (1,)
                respCalStar.run(self.key)
                boolCalStar = 1
                PtSendKIMessageInt(kStartBookAlert, 0)
            else:
                PtDebugPrint("xCalendarStar.OnNotify():  already have the stone: {}".format(sdlCalStar.value))

    def GotPage(self):
        vault = ptVault()
        if vault:  # is the Vault online?
            psnlSDL = xPsnlVaultSDL()
            psnlSDL = vault.getPsnlAgeSDL()
            if psnlSDL:
                ypageSDL = psnlSDL.findVar("YeeshaPage20")
                if ypageSDL:
                    size, state = divmod(ypageSDL.getInt(), 10)
                    PtDebugPrint("xCalendarStar.OnNotify():  YeeshaPage20 = {}".format(state))
                    if state:
                        return 1
            return 0
