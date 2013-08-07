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
Module: nb01RegisterNexusLink
Age: Neighborhood
Date: October, 2002
Author: Bill Slease
"""

from Plasma import *
from PlasmaTypes import *
from PlasmaKITypes import *

# define the attributes that will be entered in max
actClick = ptAttribActivator(1, "Actvtr: click me")
respOneshot = ptAttribResponder(2, "Rspndr: one shot")
respKIGlow = ptAttribResponder(3, "Rspndr: ki glow", netForce=1)

# globals
boolClickerIsMe = false
myID = 0
hoodID = 0
hoodMgr = None
kInviteTitle = ""
kInviteMsg = ""


class nb01RegisterNexusLink(ptModifier):
    def __init__(self):
        ptModifier.__init__(self)
        self.id = 5020
        version = 1
        self.version = version
        PtDebugPrint("__init__nb01RegisterNexusLink v.%d" % (version))

    def OnNotify(self, state, id, events):
        global boolClickerIsMe
        global myID
        global hoodID
        global hoodMgr

        #######################
        ##
        ##  stick your hand in the slot
        ##
        #######################

        if id == actClick.id:
            if not state:
                return
            respOneshot.run(self.key, events=events)
            if PtWasLocallyNotified(self.key):
                boolClickerIsMe = true
                objAvatar = PtFindAvatar(events)
                myID = PtGetClientIDFromAvatarKey(objAvatar.getKey())
            return

        ##################################
        ##
        ##  figure out what to do with the hand in the slot
        ##
        ##################################
        # Udpated to do nothing. -eap.

        if id == respOneshot.id and boolClickerIsMe:
            if not state:
                return
            boolClickerIsMe = false  # done with this var, reset it

            kiLevel = PtDetermineKILevel()
            PtDebugPrint("nb01RegisterNexusLink.OnNotify:\tplayer ki level is %d" % (kiLevel))

            # case 1:  player has no KI
            # ki slot doesn't respond, just return

            if kiLevel < kNormalKI:
                return
