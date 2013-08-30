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
"""Module: xDialogToggle
Age: global
Date: April 18, 2002
This is the handler for the standard dialog popup
"""

"""
Module: xDialogToggle
Age: global
Date: June 2002
Author: Pete Gage
reusable handler for a pop-up GUI item like a note on a desk
"""

from Plasma import *
from PlasmaTypes import *
import PlasmaControlKeys

# define the attributes that will be entered in max
Activate = ptAttribActivator(1, " clickable ", netForce=1)
Vignette = ptAttribString(4, "Toggle dialog - by Name")

# ---------
# globals

# Key mapping from control input to what the camera wants
KeyMap = {}
KeyMap[PlasmaControlKeys.kKeyMoveForward] = PlasmaControlKeys.kKeyCamPanUp
KeyMap[PlasmaControlKeys.kKeyMoveBackward] = PlasmaControlKeys.kKeyCamPanDown
KeyMap[PlasmaControlKeys.kKeyRotateLeft] = PlasmaControlKeys.kKeyCamPanLeft
KeyMap[PlasmaControlKeys.kKeyRotateRight] = PlasmaControlKeys.kKeyCamPanRight

LocalAvatar = None
kExit = 99


class xDialogToggle(ptModifier):
    "Standard Dialog Toggle"

    def __init__(self):
        ptModifier.__init__(self)
        self.id = 5104
        version = 1
        minor = 0
        self.version = "{}.{}".format(version, minor)
        PtDebugPrint("__init__: xDialogToggle v{}".format(self.version))

    def IGetAgeFilename(self):
        "returns the .age file name of the age"
        ageInfo = PtGetAgeInfo()
        if ageInfo is not None:
            return ageInfo.getAgeFilename()
        else:
            return "GUI"  # use default GUI age if we can't find the age name for some reason

    def OnFirstUpdate(self):
        PtLoadDialog(Vignette.value, self.key, self.IGetAgeFilename())

    def __del__(self):
        "unload the dialog that we loaded"
        PtUnloadDialog(Vignette.value)

    def OnNotify(self, state, id, events):
        "Activated... "
        global LocalAvatar
        if state and id == Activate.id and PtWasLocallyNotified(self.key):
            LocalAvatar = PtFindAvatar(events)
            self.IStartDialog()

    def OnGUINotify(self, id, control, event):
        "Notifications from the vignette"
        if event == kAction:
            if control.getTagID() == kExit:  # off
                self.IQuitDialog()
        elif event == kExitMode:
            self.IQuitDialog()

    def OnControlKeyEvent(self, controlKey, activeFlag):
        "Control key events... anything we're interested in?"
        PtDebugPrint("xDialogToggle.OnGUINotify():  Got controlKey event {} and its activeFlag is {}".format(controlKey, activeFlag), level=kDebugDumpLevel)
        if controlKey == PlasmaControlKeys.kKeyExitMode:
            self.IQuitDialog()

    def IStartDialog(self):
        "Start the Dialog"
        global LocalAvatar
        Activate.disable()  # disable the activator
        PtLoadDialog(Vignette.value, self.key, self.IGetAgeFilename())
        if PtIsDialogLoaded(Vignette.value):
            PtShowDialog(Vignette.value)
            PtDebugPrint("xDialogToggle.OnGUINotify():  dialog: {} goes up".format(Vignette.value))
        # get control key events
        PtGetControlEvents(true, self.key)

    def IQuitDialog(self):
        "Disengage and exit"
        global LocalAvatar
        # exit every thing
        if Vignette.value:
            PtHideDialog(Vignette.value)
            PtDebugPrint("xDialogToggle.OnGUINotify():  Dialog: {} goes down".format(Vignette.value))
        else:
            PtDebugPrint("xDialogToggle.OnGUINotify():  WTH!!!")
        # disable the Control key events
        PtGetControlEvents(false, self.key)
        # re-enable the dialog for someone else to use
        Activate.enable()
