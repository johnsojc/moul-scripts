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
"""Module: xSimpleImager
Age: global
Author: Mark DeForest
Date: Sept. 17, 2002
A simple imager, excepts images in AgeKI folder
version 1.6
March 2003 - Bill - added ability to post text notes to imagers
"""

from Plasma import *
from PlasmaTypes import *
from PlasmaKITypes import *
from PlasmaVaultConstants import *
import string

import xCensor

# vault callback contexts
kAddingDevice = 1
kSettingDeviceInbox = 2

#=============================================================
# define the attributes that will be entered in max
#=============================================================
ImagerName = ptAttribString(1, "Name of the Imager")
ImagerMap = ptAttribDynamicMap(2, "The Dynamic Texture Map")
ImagerRegion = ptAttribActivator(3, "The activate region")
ImagerTime = ptAttribInt(4, "Number of seconds on each image", default=60)
ImagerMembersOnly = ptAttribBoolean(5, "Members Only", 1)
ImagerObject = ptAttribSceneobject(6, "Imager Object (for ownership test)")
ImagerMax = ptAttribInt(7, "Maximum number of images", default=5)
ImagerButtonResp = ptAttribResponder(8, "start or stop the button animation", ['buttonOn', 'buttonOff'])
ImagerInboxVariable = ptAttribString(9, "Inbox SDL variable (optional)")
ImagerPelletUpload = ptAttribBoolean(10, "Pellet Score Imager?", 0)
#----------
# globals
#----------
ImagerContents = []
CurrentContentIdx = 0
kTextFontSize = 18
kTextFontFace = "arial"
kTextXStart = 100
kTextYStart = 100
kTextWrapWidth = 550
kTextWrapHeight = 400

theCensorLevel = 0

CurrentDisplayedElementID = -1
RegionMembers = 0

AgeStartedIn = None

#----------
# Timer
#----------
kFlipImagesTimerStates = 5
kFlipImagesTimerCurrent = 0

#====================================

Instance = None


class xSimpleImager(ptModifier):

    def __init__(self):
        global Instance
        ptModifier.__init__(self)
        Instance = self
        self.id = 196
        version = 3
        minor = 2
        self.version = "{}.{}".format(version, minor)
        PtDebugPrint("__init__: xSimpleImager v{}".format(self.version))

    def vaultOperationStarted(self, context):
        PtDebugPrint("xSimpleImager.vaultOperationStarted():  ({})".format(context), level=kDebugDumpLevel)

    def vaultOperationComplete(self, context, args, resultCode):
        PtDebugPrint("xSimpleImager.vaultOperationComplete():  ({},{})".format(context, resultCode), level=kDebugDumpLevel)
        if context == kAddingDevice:
            PtDebugPrint("xSimpleImager.vaultOperationComplete():  kAddingDevice", level=kDebugDumpLevel)
            if resultCode >= 0:
                node = args[0].upcastToTextNoteNode()
                if node:
                    PtDebugPrint("xSimpleImager.vaultOperationComplete():  Added device: {}".format(ImagerName.value), level=kDebugDumpLevel)
                    name = ""
                    if type(ImagerInboxVariable.value) is str and ImagerInboxVariable.value != "":
                        ageSDL = PtGetAgeSDL()
                        tempValue = ageSDL[ImagerInboxVariable.value]
                        if (len(tempValue) >= 1):
                            name = ageSDL[ImagerInboxVariable.value][0]
                        else:
                            name = node.noteGetTitle()
                    else:
                        name = node.noteGetTitle()
                    PtDebugPrint("xSimpleImager.vaultOperationComplete():  Setting device inbox: {}".format(name), level=kDebugDumpLevel)
                    node.setDeviceInbox(name, self, kSettingDeviceInbox)
                else:
                    PtDebugPrint("xSimpleImager.vaultOperationComplete():  ERROR! device node not found", level=kErrorLevel)

        elif context == kSettingDeviceInbox:
            # "once inbox has been set, turns the imager on."
            PtDebugPrint("xSimpleImager.vaultOperationComplete():  SettingDeviceInbox", level=kDebugDumpLevel)
            global kFlipImagesTimerStates
            global kFlipImagesTimerCurrent
            global CurrentContentIdx

            if resultCode >= 0:
                CurrentContentIdx = 0
                Instance.IRefreshImagerFolder()
                Instance.IChangeCurrentContent()
                # set up our timer callback
                # set the current timer value to
                kFlipImagesTimerCurrent = (kFlipImagesTimerCurrent + 1) % kFlipImagesTimerStates
                PtAtTimeCallback(Instance.key, ImagerTime.value, kFlipImagesTimerCurrent)
                # turn button animation off
                ImagerButtonResp.run(Instance.key, state='buttonOff')

    def OnFirstUpdate(self):

        global AgeStartedIn
        AgeStartedIn = PtGetAgeName()
        if ImagerMap.textmap is None:
            PtDebugPrint("xSimpleImager.OnFirstUpdate():  ERROR: simpleImager[{}]: Dynamic textmap is broken!".format(ImagerName.value), level=kErrorLevel)
            return
        if ImagerObject.sceneobject is None:
            PtDebugPrint("xSimpleImager.OnFirstUpdate():  ERROR: simpleImager[{}]: ImagerObject not specified!".format(ImagerName.value), level=kErrorLevel)
            return
        # initialize age devices
        if type(ImagerName.value) is str and ImagerName.value != "":
            ageVault = ptAgeVault()
            # will only add if not already there.
            ageVault.addDevice(ImagerName.value, self, kAddingDevice)
        else:
            PtDebugPrint("xSimpleImager.OnFirstUpdate():  There was no imager name!", level=kErrorLevel)

    def OnServerInitComplete(self):
        if AgeStartedIn == PtGetAgeName():
            ageSDL = PtGetAgeSDL()
            ageSDL.setNotify(self.key, ImagerInboxVariable.value, 0.0)
            if type(ImagerInboxVariable.value) is str and ImagerInboxVariable.value != "":
                ageVault = ptAgeVault()

                inbox = ""

                try:
                    inbox = ageSDL[ImagerInboxVariable.value][0]
                except:
                    PtDebugPrint("xSimpleImager.OnServerInitComplete():  Problem reading the inbox from SDL")

                if inbox == "":
                    ageVault.setDeviceInbox(ImagerName.value, ImagerName.value, self, kSettingDeviceInbox)
                else:
                    ageVault.setDeviceInbox(ImagerName.value, inbox, self, kSettingDeviceInbox)

            PtSendKIRegisterImagerMsg(ImagerName.value, self.key)

    def IDetermineCensorLevel(self):
        "Set the CensorLevel"
        global theCensorLevel
        # assume that they have none...
        theCensorLevel = xCensor.xRatedPG
        vault = ptVault()
        entry = vault.findChronicleEntry(kChronicleCensorLevel)
        if entry is None:
            # not found... add current level chronicle
            vault.addChronicleEntry(kChronicleCensorLevel, kChronicleCensorLevelType, "{:d}".format(theCensorLevel))
        else:
            theCensorLevel = string.atoi(entry.chronicleGetValue())
        PtDebugPrint("xSimpleImager.IDetermineCensorLevel():  the censor level is {}".format(theCensorLevel), level=kWarningLevel)

    def OnTimer(self, id):
        "Timer event, for the fade stuff"
        global ImagerContents
        global CurrentContentIdx
        global kFlipImagesTimerCurrent

        if id == kFlipImagesTimerCurrent:
            if len(ImagerContents) > 0:
                CurrentContentIdx += 1
                if CurrentContentIdx >= len(ImagerContents):
                    CurrentContentIdx = 0
            self.IChangeCurrentContent()
            PtAtTimeCallback(self.key, ImagerTime.value, kFlipImagesTimerCurrent)

    def OnVaultEvent(self, event, tupdata):
        "An AgeKI event received"
        PtDebugPrint("xSimpleImager.OnVaultEvent():  [{}]: event = {} tupdata = {}".format(ImagerName.value, event, tupdata), level=kDebugDumpLevel)

        # Sometimes, we randomly get None... O.o
        if tupdata[0] is None:
            PtDebugPrint("xSimpleImager.OnVaultEvent():  nil ptVaultNode", level=kErrorLevel)
            return None

        # Cyan's servers sometimes spam us with updates to the public city AgeInfo node
        # We don't want to waste time updating for crap like that.
        if isinstance(tupdata[0], ptVaultNode):
            type = tupdata[0].getType()
        elif isinstance(tupdata[0], ptVaultNodeRef):
            type = tupdata[0].getChild().getType()
        else:
            PtDebugPrint("xSimpleImager.OnVaultEvent():  tupdata[0] has unhandled object type", level=kWarningLevel)
            return None

        if not (type == PtVaultNodeTypes.kImageNode or type == PtVaultNodeTypes.kTextNoteNode):
            PtDebugPrint("xSimpleImager.OnVaultEvent():  ... but we don't care!", level=kDebugDumpLevel)
            return None

        # make sure that the bigKI dialog is loaded before trying to update it
        if event == PtVaultCallbackTypes.kVaultConnected:
            # tupdata is ()
            pass
        if event == PtVaultCallbackTypes.kVaultDisconnected:
            # tupdata is ()
            pass
        elif event == PtVaultCallbackTypes.kVaultNodeAdded:
            PtDebugPrint("xSimpleImager.OnVaultEvent():  kVaultNodeAdded event (id={}, type={})".format(tupdata[0].getID(), tupdata[0].getType()), level=kDebugDumpLevel)
            # tupdata is ( ptVaultNode )
            self.IRefreshImagerFolder()
            self.IRefreshImagerElement(tupdata[0])
        elif event == PtVaultCallbackTypes.kVaultNodeSaved:
            PtDebugPrint("xSimpleImager.OnVaultEvent():  kVaultNodeSaved event (id={}, type={})".format(tupdata[0].getID(), tupdata[0].getType()), level=kDebugDumpLevel)
            # tupdata is ( ptVaultNode )
            self.IRefreshImagerFolder()
            self.IRefreshImagerElement(tupdata[0])
        elif event == PtVaultCallbackTypes.kVaultNodeRefAdded:
            PtDebugPrint("xSimpleImager.OnVaultEvent():  kVaultNodeRefAdded event (childID={}, parentID={})".format(tupdata[0].getChildID(), tupdata[0].getParentID()), level=kDebugDumpLevel)
            # tupdata is ( ptVaultNodeRef )
            self.IRefreshImagerFolder()
            self.IRefreshImagerContent(tupdata[0])
        elif event == PtVaultCallbackTypes.kVaultRemovingNodeRef:
            # tupdata is ( ptVaultNodeRef )
            pass
        elif event == PtVaultCallbackTypes.kVaultNodeRefRemoved:
            PtDebugPrint("xSimpleImager.OnVaultEvent():  kVaultNodeRefRemoved event (childID,parentID) {}".format(tupdata), level=kDebugDumpLevel)
            # tupdata is ( childID, parentID )
            self.IRefreshImagerFolder()
            pass
        elif event == PtVaultCallbackTypes.kVaultOperationFailed:
            #tupdata is ( operation, resultCode )
            pass
        else:
            pass

    def OnNotify(self, state, id, events):
        "They've entered into the imager's region... inform them thru the KI"
        global CurrentDisplayedElementID
        global RegionMembers

        # is this our activator notifying us?
        if id == ImagerRegion.id:
            if PtWasLocallyNotified(self.key):
                ageMgr = ptVault()
                if PtIsInternalRelease() or (not ImagerMembersOnly.value or ageMgr.amOwnerOfCurrentAge()):
                    if id == ImagerRegion.id:
                        for event in events:
                            if event[0] == kCollisionEvent:
                                kiLevel = PtDetermineKILevel()
                                if (kiLevel < kNormalKI):
                                    return
                                if ImagerPelletUpload.value:
                                    messagetoki = str(ImagerName.value) + "<p>"
                                else:
                                    messagetoki = ImagerName.value
                                if event[1]:
                                    PtDebugPrint("xSimpleImager.OnNotify():  add imager {}".format(ImagerName.value), level=kDebugDumpLevel)
                                    PtSendKIMessage(kAddPlayerDevice, messagetoki)
                                    RegionMembers = RegionMembers + 1
                                    if (RegionMembers == 1):
                                        ImagerButtonResp.run(self.key, state='buttonOn')

                                else:
                                    PtDebugPrint("xSimpleImager.OnNotify():  remove imager {}".format(ImagerName.value), level=kDebugDumpLevel)
                                    PtSendKIMessage(kRemovePlayerDevice, messagetoki)
                                    RegionMembers = RegionMembers - 1
                                    if (RegionMembers == -1):
                                        RegionMembers = 0
                                    if (RegionMembers == 0):
                                        ImagerButtonResp.run(self.key, state='buttonOff')

        else:
            # else it must be a notification back to ourselves...
            # ...telling us to display a certain element
            for event in events:
                if event[0] == kVariableEvent:
                    if event[1][:7] == "dispID=":
                        newID = string.atoi(event[1][7:])
                        if newID != CurrentDisplayedElementID:
                            CurrentDisplayedElementID = newID
                            self.IShowCurrentContent()
                    elif event[1][:7] == "Update=":
                        newID = string.atoi(event[1][7:])
                        if not self.sceneobject.isLocallyOwned():
                            PtForceVaultNodeUpdate(newID)
                            self.IShowCurrentContent()
                        if newID == CurrentDisplayedElementID:
                            self.IShowCurrentContent()
                    elif event[1][:9] == "Uploaded=":
                        newID = string.atoi(event[1][9:])
                        if not ImagerObject.sceneobject.isLocallyOwned():
                            ageVault = ptAgeVault()
                            folder = ageVault.getDeviceInbox(ImagerName.value)
                            if folder:
                                PtVaultDownload(folder.getID())
                        if newID == CurrentDisplayedElementID:
                            self.IShowCurrentContent()
                    elif event[1][:7] == "Upload=":
                        deviceName = event[1][7:]
                        nodeId = int(event[3])
                        if deviceName == ImagerName.value and ImagerObject.sceneobject.isLocallyOwned():
                            ageVault = ptAgeVault()
                            folder = ageVault.getDeviceInbox(ImagerName.value)
                            if folder:
                                folder.linkToNode(nodeId)

                                PtForceVaultNodeUpdate(nodeId)

                                selfnotify = ptNotify(self.key)
                                selfnotify.clearReceivers()
                                selfnotify.addReceiver(self.key)
                                selfnotify.netPropagate(1)
                                selfnotify.netForce(1)
                                selfnotify.setActivate(1.0)
                                sname = "Uploaded={:d}".format(nodeId)
                                selfnotify.addVarNumber(sname, 1.0)
                                selfnotify.send()

    def IRefreshImagerFolder(self):
        "Refresh the folder contents"
        global ImagerContents
        global CurrentContentIdx
        ageVault = ptAgeVault()
        folder = ageVault.getDeviceInbox(ImagerName.value)
        if folder is not None:
            prevsize = len(ImagerContents)
            ImagerContents = folder.getChildNodeRefList()
            # check to make sure we are not over budget... but only on the master
            if ImagerObject.sceneobject.isLocallyOwned():
                if len(ImagerContents) > ImagerMax.value:
                    # time to get rid of one... find oldest
                    # for now... just get rid of the first one in the list
                    relem = ImagerContents[0].getChild()
                    PtDebugPrint("xSimpleImager.IRefreshImagerFolder():  [{}]: removing element {}".format(ImagerName.value, relem.getID()), level=kDebugDumpLevel)
                    folder.removeNode(relem)
            # if we went from none to some, then display one now
            if prevsize == 0 and len(ImagerContents):
                self.IChangeCurrentContent()
        else:
            # there is no folders
            ImagerContents = []

    def IRefreshImagerContent(self, updated_content):
        "Refresh a content of the Imager (if being displayed)"
        global CurrentDisplayedElementID
        if updated_content is not None:
            updated_element = updated_content.getChild()
            if updated_element is not None:
                if updated_element.getID() == CurrentDisplayedElementID:
                    self.IShowCurrentContent()
                else:
                    if not updated_content.beenSeen():
                        self.IChangeCurrentContent(updated_element.getID())

    def IRefreshImagerElement(self, updated_element):
        "Refresh an element of the Imager (if being displayed)"
        global CurrentDisplayedElementID
        if updated_element is not None:
            if updated_element.getID() == CurrentDisplayedElementID:
                self.IShowCurrentContent()
            else:
                ageVault = ptAgeVault()
                folder = ageVault.getDeviceInbox(ImagerName.value)
                if folder is not None:
                    frefs = folder.getChildNodeRefList()
                    for ref in frefs:
                        elem = ref.getChild()
                        if elem is not None and elem.getID() == updated_element.getID():
                            if not ref.beenSeen():
                                self.IChangeCurrentContent(updated_element.getID())
                                return

    def IChangeCurrentContent(self, next=None):
        "send a message to ourselves to say what the next"
        global ImagerContents
        global CurrentContentIdx
        global CurrentDisplayedElementID
        # only the owner of the imager changes the images
        if ImagerObject.sceneobject.isLocallyOwned():
            nextID = -1
            if next is None:
                try:
                    element = ImagerContents[CurrentContentIdx].getChild()
                    if element is not None:
                        nextID = element.getID()
                except LookupError:
                    pass
            else:
                nextID = next
            selfnotify = ptNotify(self.key)
            selfnotify.clearReceivers()
            selfnotify.addReceiver(self.key)
            selfnotify.netPropagate(1)
            selfnotify.netForce(1)
            selfnotify.setActivate(1.0)
            sname = "dispID={:d}".format(nextID)
            selfnotify.addVarNumber(sname, 1.0)
            selfnotify.send()
        else:
            pass

    def IShowCurrentContent(self):
        # show the contents on the dyna-map
        global CurrentDisplayedElementID
        global theCensorLevel
        if CurrentDisplayedElementID != -1:
            ageVault = ptAgeVault()
            folder = ageVault.getDeviceInbox(ImagerName.value)
            if folder is not None:
                fcontents = folder.getChildNodeRefList()
                for content in fcontents:
                    element = content.getChild()
                    if element is not None and element.getID() == CurrentDisplayedElementID:
                        # set that we've seen this... at least once
                        content.setSeen()
                        elemType = element.getType()
                        if elemType == PtVaultNodeTypes.kImageNode:
                            element = element.upcastToImageNode()
                            PtDebugPrint("xSimpleImager.IShowCurrentContent():  now showing image {}".format(element.imageGetTitle()), level=kDebugDumpLevel)
                            ImagerMap.textmap.drawImage(0, 0, element.imageGetImage(), 0)
                            ImagerMap.textmap.flush()
                        elif elemType == PtVaultNodeTypes.kTextNoteNode:
                            element = element.upcastToTextNoteNode()
                            textbody = element.noteGetText()
                            if textbody == "cleardaImager":
                                PtDebugPrint("xSimpleImager.IShowCurrentContent():  [{}]: clearing the imager of images".format(ImagerName.value), level=kWarningLevel)
                                folder.removeAllNodes()
                            else:
                                self.IDetermineCensorLevel()
                                ImagerMap.textmap.clearToColor(ptColor().black())
                                ImagerMap.textmap.setTextColor(ptColor().white())
                                ImagerMap.textmap.setWrapping(kTextWrapWidth, kTextWrapHeight)
                                ImagerMap.textmap.setFont(kTextFontFace, kTextFontSize)
                                try:
                                    textfrom = content.getSaver().playerGetName()
                                except:
                                    textfrom = "System"
                                try:
                                    textsubject = element.noteGetTitle()
                                except:
                                    textsubject = "Imager Transmission"
                                PtDebugPrint("xSimpleImager.IShowCurrentContent():  now showing textnote {}".format(textsubject), level=kDebugDumpLevel)
                                message = PtGetLocalizedString("Neighborhood.Messages.Imager", [textfrom, textsubject, textbody])
                                message = xCensor.xCensor(message, theCensorLevel)
                                ImagerMap.textmap.drawTextW(kTextXStart, kTextYStart, message)
                                ImagerMap.textmap.flush()
                        else:
                            PtDebugPrint("xSimpleImager.IShowCurrentContent():  [{}]: Can't display element type {}".format(ImagerName.value, elemType), level=kWarningLevel)
                            pass
                        return
            else:
                PtDebugPrint("xSimpleImager.IShowCurrentContent():  [{}]: Inbox for imager is None".format(ImagerName.value), level=kWarningLevel)
        else:
            # undisplaying all images... to be done later...
            ImagerMap.textmap.clearToColor(ptColor(0, 0, 0, 0))
            ImagerMap.textmap.flush()
            PtDebugPrint("xSimpleImager.IShowCurrentContent():  [{}]: no current element id to display".format(ImagerName.value), level=kDebugDumpLevel)

    def OnSDLNotify(self, VARname, SDLname, playerID, tag):
        if VARname != ImagerInboxVariable.value:
            return

        if AgeStartedIn == PtGetAgeName():
            ageSDL = PtGetAgeSDL()
            ageVault = ptAgeVault()
            inbox = ageSDL[ImagerInboxVariable.value][0]

            if inbox == "":
                ageVault.setDeviceInbox(ImagerName.value, ImagerName.value, self, kSettingDeviceInbox)
            else:
                ageVault.setDeviceInbox(ImagerName.value, ageSDL[ImagerInboxVariable.value][0], self, kSettingDeviceInbox)

    def OnBackdoorMsg(self, target, param):
        if target == "imager" and param == "refresh" and ImagerName.value == "D'ni  Imager Right":
            PtDebugPrint("xSimpleImager.OnBackdoorMsg():  Manual refresh requested", level=kWarningLevel)
            CurrentDisplayedElementID = 12459
            self.IShowCurrentContent()
