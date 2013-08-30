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
"""Module: nb01DRCImager
Age: neighborhood
Author: Adam Van Ornum
Date: March 2003
"""

from Plasma import *
from PlasmaTypes import *
import string

#=============================================================
# define the attributes that will be entered in max
#=============================================================
ImagerMap = ptAttribDynamicMap(1, "The Dynamic Texture Map")
ImagerTime = ptAttribInt(2, "Number of seconds on each image", default=10)
ImagerObject = ptAttribSceneobject(3, "Imager Object (for ownership test)")

AgeStartedIn = None


def doneSettingDeviceInbox(node, nodeRef, resultCode):
    "once inbox has been set, turns the imager on."
    PtDebugPrint("nb01DRCImager.doneSettingDeviceInbox():  result code = {}".format(resultCode))

    # Update the inbox reference in the class
    nb01DRCImager.Instance.ChangeInbox()
    PtAtTimeCallback(nb01DRCImager.Instance.key, 0, nb01DRCImager.Instance.current_state)


def doneAddingDevice(node, nodeRef, resultCode):
    "initializes new imager device with default inbox folder."
    PtDebugPrint("nb01DRCImager.doneAddingDevice():  result code = {}".format(resultCode))


#====================================
class nb01DRCImager(ptModifier):
    Instance = None

    def __init__(self):
        ptModifier.__init__(self)
        self.id = 5305
        version = 2
        minor = 0
        self.version = "{}.{}".format(version, minor)
        PtDebugPrint("__init__: nb01DRCImager v{}".format(self.version))
        self.current_state = 0
        self.current_image = 0
        self.number_of_images = 0
        self.inbox = None
        nb01DRCImager.Instance = self

    def ChangeInbox(self):
        PtDebugPrint("nb01DRCImager.ChangeInbox():  Attempting to get the inbox")
        self.inbox = ptAgeVault().getDeviceInbox("DRCImager")

    def SetImage(self, id):

        if self.inbox is not None:
            PtDebugPrint("nb01DRCImager.SetImage():  inbox {} id = {}".format(self.inbox.folderGetName(), self.inbox.getID()))

            if self.number_of_images > 0:
                fcontents = self.inbox.getChildNodeRefList()
                for element in fcontents:
                    image = element.getChild()
                    if image.getID() == id:
                        image = image.upcastToImageNode()
                        PtDebugPrint("nb01DRCImager.SetImage():  now showing image {}".format(image.imageGetTitle()))
                        try:
                            ImagerMap.textmap.drawImage(0, 0, image.imageGetImage(), 0)
                            ImagerMap.textmap.flush()
                        except:
                            PtDebugPrint("nb01DRCImager.SetImage():  couldn't draw image...")
                            pass
                        return

    def OnFirstUpdate(self):
        global AgeStartedIn
        AgeStartedIn = PtGetAgeName()

    def OnServerInitComplete(self):
        if AgeStartedIn == PtGetAgeName():
            ageSDL = PtGetAgeSDL()
            ageSDL.setNotify(self.key, "nb01DRCImagerState", 0.0)

            self.current_state = ageSDL["nb01DRCImagerState"][0]

            PtDebugPrint("nb01DRCImager.OnServerInitComplete():  Adding device")
            ptAgeVault().addDevice("DRCImager", doneAddingDevice)
            PtDebugPrint("nb01DRCImager.OnServerInitComplete():  Setting device inbox - DRCImagerState{}".format(self.current_state))
            ptAgeVault().setDeviceInbox("DRCImager", "DRCImagerState{}".format(self.current_state), doneSettingDeviceInbox)

    def OnTimer(self, id):
        PtDebugPrint("nb01DRCImager.OnTimer():  executing")

        if id == self.current_state:

            self.number_of_images = self.inbox.getChildNodeCount()

            if self.number_of_images > 0:
                self.current_image = (self.current_image + 1) % self.number_of_images

                if ImagerObject.sceneobject.isLocallyOwned():

                    folder = self.inbox.getChildNodeRefList()
                    element = folder[self.current_image].getChild()
                    if element is not None:
                        nextID = element.getID()
                    else:
                        nextID = -1

                    selfnotify = ptNotify(self.key)
                    selfnotify.clearReceivers()
                    selfnotify.addReceiver(self.key)
                    selfnotify.netPropagate(1)
                    selfnotify.netForce(1)
                    selfnotify.setActivate(1.0)
                    sname = "dispID={}".format(nextID)
                    selfnotify.addVarNumber(sname, 1.0)
                    selfnotify.send()

                    PtAtTimeCallback(self.key, ImagerTime.value, self.current_state)

    def OnNotify(self, state, id, events):
        PtDebugPrint("nb01DRCImager.OnNotify():  executing")
        for event in events:
            if event[0] == kVariableEvent:
                if event[1][:7] == "dispID=":
                    newID = string.atoi(event[1][7:])
                    if newID != self.current_image:
                        self.SetImage(newID)

    def OnSDLNotify(self, VARname, SDLname, playerID, tag):
        global boolCurrentValue

        if AgeStartedIn == PtGetAgeName():
            ageSDL = PtGetAgeSDL()
            if VARname == "nb01DRCImagerState":
                self.current_state = ageSDL["nb01DRCImagerState"][0]

                PtDebugPrint("nb01DRCImager.OnSDLNotify():  VARname:{}, SDLname:{}, tag:{}, value:{}".format(VARname, SDLname, tag, self.current_state))

                ImagerMap.textmap.clearToColor(ptColor(0, 0, 0, 0))
                ImagerMap.textmap.flush()

                ptAgeVault().setDeviceInbox("DRCImager", "DRCImagerState{}".format(self.current_state), doneSettingDeviceInbox)
