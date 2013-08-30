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
Module: xAgeSDLBoolAndRespond
Age: global
Date: April 2003
Author: Bill Slease
Detects changes of 2 age SDL bools, ANDs them and runs
one of two responders depending on true/false
"""

from Plasma import *
from PlasmaTypes import *
import string

# ---------
# max wiring
# ---------

stringVar1Name = ptAttribString(1, "Age SDL Var #1")
stringVar2Name = ptAttribString(2, "Age SDL Var #2")
respBoolTrue = ptAttribResponder(3, "Run if bool true:")
respBoolFalse = ptAttribResponder(4, "Run if bool false:")
boolVltMgrFastForward = ptAttribBoolean(5, "F-Forward on VM notify", 1)
boolFFOnInit = ptAttribBoolean(6, "F-Forward on Init", 1)
boolDefault = ptAttribBoolean(7, "Default setting", 0)

# ---------
# globals
# ---------
boolCurrentState = false


class xAgeSDLBoolAndRespond(ptResponder):

    def __init__(self):
        ptResponder.__init__(self)
        self.id = 5039
        version = 1
        minor = 0
        self.version = "{}.{}".format(version, minor)
        PtDebugPrint("__init__: xAgeSDLBoolAndRespond v{}".format(self.version))

    def OnFirstUpdate(self):
        if not(type(stringVar1Name.value) is str and stringVar1Name.value != ""):
            PtDebugPrint("xAgeSDLBoolAndRespond.OnFirstUpdate():  ERROR: missing SDL var1 name in max file")
        if not(type(stringVar2Name.value) is str and stringVar2Name.value != ""):
            PtDebugPrint("xAgeSDLBoolAndRespond.OnFirstUpdate():  ERROR: missing SDL var2 name in max file")

    def OnServerInitComplete(self):
        global boolCurrentState

        try:
            ageSDL = PtGetAgeSDL()
            ageSDL.setNotify(self.key, stringVar1Name.value, 0.0)
            ageSDL.setNotify(self.key, stringVar2Name.value, 0.0)
            if ageSDL[stringVar1Name.value][0] and ageSDL[stringVar2Name.value][0]:
                PtDebugPrint("xAgeSDLBoolAndRespond.OnServerInitComplete():  DEBUG: Running true responder on {}, fastforward={}".format(self.sceneobject.getName(), boolFFOnInit.value))
                respBoolTrue.run(self.key, fastforward=boolFFOnInit.value)
                boolCurrentState = true
            else:
                PtDebugPrint("xAgeSDLBoolAndRespond.OnServerInitComplete():  DEBUG: Running false responder on {}, fastforward={}".format(self.sceneobject.getName(), boolFFOnInit.value))
                respBoolFalse.run(self.key, fastforward=boolFFOnInit.value)
                boolCurrentState = false
        except:
            self.runDefault()

    def runDefault(self):
        PtDebugPrint("xAgeSDLBoolAndRespond.runDefault():  running internal default")
        if boolDefault.value:
            respBoolTrue.run(self.key, fastforward=boolFFOnInit.value)
            boolCurrentState = true
        else:
            respBoolFalse.run(self.key, fastforward=boolFFOnInit.value)
            boolCurrentState = false

    def OnSDLNotify(self, VARname, SDLname, playerID, tag):
        global boolCurrentState

        # is it a var we care about?
        if VARname != stringVar1Name.value and VARname != stringVar2Name.value:
            return

        ageSDL = PtGetAgeSDL()
        PtDebugPrint("xAgeSDLBoolAndRespond.OnSDLNotify():  DEBUG: VARname:{}, SDLname:{}, tag:{}, value:{}".format(VARname, SDLname, tag, ageSDL[VARname][0]))

        # is state change from player or vault manager?
        if playerID:  # non-zero means it's a player
            objAvatar = ptSceneobject(PtGetAvatarKeyFromClientID(playerID), self.key)
            fastforward = 0
        else:  # invalid player aka Vault Manager
            objAvatar = None
            fastforward = boolVltMgrFastForward.value  # we need to skip any one-shots
        PtDebugPrint("xAgeSDLBoolAndRespond.OnSDLNotify():  DEBUG: notification from playerID: {}".format(playerID))

        # does the change change our current state?
        if boolCurrentState == false and (ageSDL[stringVar1Name.value][0] and ageSDL[stringVar2Name.value][0]):
            boolCurrentState = true
        elif boolCurrentState == true and not (ageSDL[stringVar1Name.value][0] and ageSDL[stringVar2Name.value][0]):
            boolCurrentState = false
        else:
            PtDebugPrint("xAgeSDLBoolAndRespond.OnSDLNotify():  DEBUG: {} ANDed state didn't change.".format(self.sceneobject.getName()))
            return
        PtDebugPrint("xAgeSDLBoolAndRespond.OnSDLNotify():  DEBUG: state changed to {}".format(boolCurrentState))

        # run the appropriate responder!
        if boolCurrentState:
            PtDebugPrint("xAgeSDLBoolAndRespond.OnSDLNotify():  DEBUG: Running true responder on {}, fastforward={}".format(self.sceneobject.getName(), fastforward))
            respBoolTrue.run(self.key, avatar=objAvatar, fastforward=fastforward)
        else:
            PtDebugPrint("xAgeSDLBoolAndRespond.OnSDLNotify():  DEBUG: Running false responder on {}, fastforward={}".format(self.sceneobject.getName(), fastforward))
            respBoolFalse.run(self.key, avatar=objAvatar, fastforward=fastforward)
