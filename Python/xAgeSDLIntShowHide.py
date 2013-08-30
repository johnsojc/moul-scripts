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
Module: xAgeSDLIntShowHide
Age: Global
Date: March 2003
Author: Adam Van Ornum
Detects age SDL variable change and shows (on unspecified states) or hides (on unspecified states) the object it's attached to
Enter in the states you wish the item to be visible in as a comma separated list
"""

from Plasma import *
from PlasmaTypes import *
import string

stringVarName = ptAttribString(1, "Age SDL Var Name")
stringShowStates = ptAttribString(2, "States in which shown")
intDefault = ptAttribInt(3, "Default setting", 0)
boolFirstUpdate = ptAttribBoolean(4, "Eval On First Update?", 0)


class xAgeSDLIntShowHide(ptMultiModifier):

    def __init__(self):
        ptMultiModifier.__init__(self)
        self.id = 5304
        version = 2
        minor = 0
        self.version = "{}.{}".format(version, minor)
        PtDebugPrint("__init__: xAgeSDLIntShowHide v{}".format(self.version))
        self.enabledStateList = []

    def OnFirstUpdate(self):
        if not (type(stringVarName.value) is str and stringVarName.value != ""):
            PtDebugPrint("xAgeSDLIntShowHide.OnFirstUpdate():  ERROR: missing SDL var name")
            pass

        if boolFirstUpdate.value:
            self.Initialize()

    def OnServerInitComplete(self):
        if not boolFirstUpdate.value:
            self.Initialize()

    def Initialize(self):
        ageSDL = PtGetAgeSDL()
        if type(stringVarName.value) is str and stringVarName.value != "":
            ageSDL.setFlags(stringVarName.value, 1, 1)
            ageSDL.sendToClients(stringVarName.value)
            try:
                self.enabledStateList = stringShowStates.value.split(",")
                for i in range(len(self.enabledStateList)):
                    self.enabledStateList[i] = int(self.enabledStateList[i].strip())
            except:
                PtDebugPrint("xAgeSDLIntShowHide.Initialize():  ERROR: couldn't process start state list")
                pass

            ageSDL.setNotify(self.key, stringVarName.value, 0.0)
            try:
                SDLvalue = ageSDL[stringVarName.value][0]
            except:
                PtDebugPrint("xAgeSDLIntShowHide.Initialize():  ERROR: age sdl read failed, SDLvalue = {} by default. stringVarName = {}".format(intDefault.value, stringVarName.value))
                SDLvalue = intDefault.value

            try:
                if SDLvalue in self.enabledStateList:
                    PtDebugPrint("xAgeSDLIntShowHide.Initialize():  DEBUG: Attempting to enable drawing and collision on {}...".format(self.sceneobject.getName()))
                    self.sceneobject.draw.enable()
                    self.sceneobject.physics.suppress(false)
                else:
                    PtDebugPrint("xAgeSDLIntShowHide.Initialize():  DEBUG: Attempting to disable drawing and collision on {}...".format(self.sceneobject.getName()))
                    self.sceneobject.draw.disable()
                    self.sceneobject.physics.suppress(true)
            except:
                PtDebugPrint("xAgeSDLIntShowHide.Initialize():  ERROR: Error enabling/disabling object {}".format(self.sceneobject.getName()))
                self.runDefault()
        else:
            PtDebugPrint("xAgeSDLIntShowHide.Initialize():  ERROR: missing SDL var name")
            self.runDefault()

    def runDefault(self):
        PtDebugPrint("xAgeSDLIntShowHide.runDefault():  running internal default")
        if intDefault.value in self.enabledStateList:
            PtDebugPrint("xAgeSDLIntShowHide.runDefault():  DEBUG: Attempting to enable drawing and collision on {}...".format(self.sceneobject.getName()))
            self.sceneobject.draw.enable()
            self.sceneobject.physics.suppress(false)
        else:
            PtDebugPrint("xAgeSDLIntShowHide.runDefault():  DEBUG: Attempting to disable drawing and collision on {}...".format(self.sceneobject.getName()))
            self.sceneobject.draw.disable()
            self.sceneobject.physics.suppress(true)

    def OnSDLNotify(self, VARname, SDLname, playerID, tag):
        if VARname != stringVarName.value:
            return

        ageSDL = PtGetAgeSDL()
        SDLvalue = ageSDL[stringVarName.value][0]
        if SDLvalue in self.enabledStateList:
            self.EnableObject()
        else:
            self.DisableObject()

    def EnableObject(self):
        PtDebugPrint("xAgeSDLIntShowHide.EnableObject():  DEBUG: Attempting to enable drawing and collision on {}...".format(self.sceneobject.getName()))
        self.sceneobject.draw.enable()
        self.sceneobject.physics.suppress(false)

    def DisableObject(self):
        PtDebugPrint("xAgeSDLIntShowHide.DisableObject():  DEBUG: Attempting to disable drawing and collision on {}...".format(self.sceneobject.getName()))
        self.sceneobject.draw.disable()
        self.sceneobject.physics.suppress(true)

    def OnBackdoorMsg(self, target, param):
        if type(stringVarName.value) is not None and stringVarName.value != "":
            if target == stringVarName.value:
                if int(param) in self.enabledStateList:
                    self.EnableObject()
                else:
                    self.DisableObject()
