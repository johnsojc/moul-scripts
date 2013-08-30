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
Module: xAgeSDLIntRespList.py
Age: Global
Date: March, 2003
Author: Adam Van Ornum
"""

from Plasma import *
from PlasmaTypes import *
import re

# define the attributes that will be entered in max1

# NOTE: The Responder name format string should be the name of the responder with a %d somewhere in there
#            that will specify which responder runs at the received state.  All of the responders
#            must be named similarly (like below).
#            I.E:  Three responders named Resp01, Resp02, Resp03 so the format string would be "Resp0%d"

stringSDLVarName = ptAttribString(1, "Age SDL Variable")
respList = ptAttribResponderList(2, "ResponderList", byObject=1)
stringFormat = ptAttribString(3, "Responder name format string")
intMaxState = ptAttribInt(4, "Max state value", 2)
boolStartFF = ptAttribBoolean(5, "F-Forward on start", 0)
boolVltMgrFF = ptAttribBoolean(6, "F-Forward on VM notify", 1)
intDefault = ptAttribInt(7, "Default setting", 0)


class xAgeSDLIntRespList(ptResponder):
    def __init__(self):
        ptModifier.__init__(self)
        self.id = 5307
        version = 2
        minor = 0
        self.version = "{}.{}".format(version, minor)
        PtDebugPrint("__init__: xAgeSDLIntRespList v{}".format(self.version))

    def OnFirstUpdate(self):
        if type(stringSDLVarName.value) is not str or stringSDLVarName.value == "":
            PtDebugPrint("xAgeSDLIntRespList.OnFirstUpdate():  ERROR: missing SDL var name in max file")
            pass

        elif type(stringFormat.value) is not str or stringFormat.value == "":
            PtDebugPrint("xAgeSDLIntRespList.OnFirstUpdate():  ERROR: missing responder name format string in max file")
            pass

    def OnServerInitComplete(self):
        ageSDL = PtGetAgeSDL()
        PtDebugPrint("xAgeSDLIntRespList.OnServerInitComplete():  DEBUG: Processing")
        ageSDL.setNotify(self.key, stringSDLVarName.value, 0.0)
        try:
            SDLvalue = ageSDL[stringSDLVarName.value][0]
        except:
            PtDebugPrint("xAgeSDLIntRespList.OnServerInitComplete():  ERROR: age sdl read failed, SDLvalue = {} by default. stringSDLVarName = {}".format(intDefault.value, stringSDLVarName.value))
            SDLvalue = intDefault.value

        respName = (stringFormat.value % SDLvalue)

        if 0 <= SDLvalue <= intMaxState.value:
            for key in respList.byObject.keys():
                if key == respName:  # match:
                    PtDebugPrint("xAgeSDLIntRespList.OnServerInitComplete():  DEBUG: Running responder - {}".format(stringFormat.value % SDLvalue))
                    respList.run(self.key, avatar=None, objectName=respName, fastforward=boolStartFF.value)
                    break

    def OnSDLNotify(self, VARname, SDLname, PlayerID, tag):
        if VARname != stringSDLVarName.value:
            return

        ageSDL = PtGetAgeSDL()
        # is state change from player or vault manager?
        if PlayerID:  # non-zero means it's a player
            objAvatar = ptSceneobject(PtGetAvatarKeyFromClientID(PlayerID), self.key)
            fastforward = 0
        else:  # invalid player aka Vault Manager
            objAvatar = None
            fastforward = boolVltMgrFF.value  # we need to skip any one-shots
        if tag == "fastforward":
            objAvatar = None
            fastforward = 1
        PtDebugPrint("xAgeSDLIntRespList.OnSDLNotify():  DEBUG: notification from PlayerID: {}".format(PlayerID))

        SDLvalue = ageSDL[stringSDLVarName.value][0]

        PtDebugPrint("xAgeSDLIntRespList.OnSDLNotify():  DEBUG: received: {} = {}".format(VARname, SDLvalue))

        respName = (stringFormat.value % SDLvalue)

        if 0 <= SDLvalue <= intMaxState.value:
            for key in respList.byObject.keys():
                if key == respName:  # match:
                    PtDebugPrint("xAgeSDLIntRespList.OnSDLNotify():  DEBUG: Running responder - {}".format(stringFormat.value % SDLvalue))
                    respList.run(self.key, avatar=objAvatar, objectName=respName, fastforward=fastforward)
                    break
