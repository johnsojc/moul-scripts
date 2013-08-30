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
Module: xSitAugment
Age: global
Date: May 2002
Author: Pete Gage
allows user to select what sit component messages get passed on to another script
"""

from Plasma import *
from PlasmaTypes import *
import PlasmaControlKeys

# define the attributes that will be entered in max
SitAct = ptAttribActivator(1, " Sit Component ", netForce=1)
Camera = ptAttribSceneobject(2, " Sit Camera ")
trig0 = ptAttribBoolean(3, "Trigger at Start Sit", 0)
trig1 = ptAttribBoolean(4, "Trigger at End Sit", 1)
trig2 = ptAttribBoolean(5, "Trigger at Start Stand", 0)
trig3 = ptAttribBoolean(6, "Trigger at End Stand", 0)
untrig0 = ptAttribBoolean(7, "Untrigger at Start Sit", 0)
untrig1 = ptAttribBoolean(8, "Untrigger at End Sit", 0)
untrig2 = ptAttribBoolean(9, "Untrigger at Start Stand", 1)
untrig3 = ptAttribBoolean(10, "Untrigger at End Stand", 0)
resp0 = ptAttribResponder(11, "optional responder @ start sit")
resp1 = ptAttribResponder(12, "optional responder @ end sit")
resp2 = ptAttribResponder(13, "opt. responder @ start stand")
resp3 = ptAttribResponder(14, "opt. responder @ end stand")

# ---------
# globals

LocalAvatar = None


class xSitAugment(ptModifier):
    def __init__(self):
        ptModifier.__init__(self)
        self.id = 5116

        version = 1
        minor = 0
        self.version = "{}.{}".format(version, minor)
        PtDebugPrint("__init__: xSitAugment v{}".format(self.version))

    def OnFirstUpdate(self):
        pass

    def OnNotify(self, state, id, events):
        "Activated... "
        global LocalAvatar
        if state and id == SitAct.id:

            callback = 0  # which stage are we at.

            virtCam = ptCamera()

            checktrig = "trig{}".format(callback)
            if checktrig.value:  # checkbox is true, set camera
                virtCam.save(Camera.sceneobject.getKey())

            checkuntrig = "untrig{}".format(callback)
            if checkuntrig.value:  # checkbox is true, unset camera
                virtCam.restore(Camera.sceneobject.getKey())

            checkresp = "resp{}".format(callback)
            if checkresp.value is not None:  # responder for this stage. Play it.
                checkresp.run(self.key)

### below is scrap
    def OnGUINotify(self, id, control, event):
        "Notifications from the vignette"
        PtDebugPrint("xSitAugment.OnGUINotify():  GUI Notify id={}, event={} control={}".format(id, event, control))
        if control.getTagID() == kExit:  # off
            self.IQuitDialog()

    def OnControlKeyEvent(self, controlKey, activeFlag):
        "Control key events... anything we're interested in?"
        PtDebugPrint("xSitAugment.OnControlKeyEvent():  Got controlKey event {} and its activeFlag is {}".format(controlKey, activeFlag))
        if controlKey == PlasmaControlKeys.kKeyExitMode:
            self.IQuitDialog()

    def IStartDialog(self):
        "Start the Dialog"
        global LocalAvatar
        Activate.disable()  # disable the activator
        PtLoadDialog(Vignette.value, self.key)
        if PtIsDialogLoaded(Vignette.value):
            PtShowDialog(Vignette.value)
            PtDebugPrint("xSitAugment.IStartDialog():  dialog: {} goes up".format(Vignette.value))
        # get control key events
        PtEnableControlKeyEvents(self.key)

    def IQuitSitting(self):
        "Disengage and exit"
        global LocalAvatar
        # exit every thing
        if Vignette.value and Vignette.value != "":
            PtHideDialog(Vignette.value)
            PtDebugPrint("xSitAugment.IQuitSitting():  Dialog: {} goes down".format(Vignette.value))
        else:
            PtDebugPrint("xSitAugment.IQuitSitting():  WTH!!!")
        #disable the Control key events
        PtDisableControlKeyEvents(self.key)
        # re-enable the dialog for someone else to use
        Activate.enable()
