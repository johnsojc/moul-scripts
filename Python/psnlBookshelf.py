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
Module: psnlBookshelf
Age: Personal Age
Date: August 2002
Author: Bill Slease
This is the handler for the standard personal age bookshelf
Interfaces with xLinkingBookGUIPopup.py
"""

from Plasma import *
from PlasmaTypes import *
from PlasmaVaultConstants import *
from PlasmaNetConstants import *
import PlasmaControlKeys
import xLinkingBookDefs
from xPsnlVaultSDL import *

import xVisitorUtils  # For non-subscription based players

# define the attributes that will be entered in max
actBookshelf = ptAttribActivator(3, "Actvtr:Bookshelf")

actBook = ptAttribActivator(4, "Actvtr:Book", byObject=1)
respPresentBook = ptAttribResponder(5, "Rspndr:PresentBook", byObject=1)
respShelveBook = ptAttribResponder(6, "Rspndr:ShelveBook", byObject=1)
objLibrary = ptAttribSceneobjectList(7, "Objct:Books")

objTrays = ptAttribSceneobjectList(8, "Objct:Trays")
respDeleteBook = ptAttribResponder(9, "Rspndr:DeleteBook", byObject=1)
respReturnTray = ptAttribResponder(10, "Rspndr:ReturnTray", byObject=1)
actTray = ptAttribActivator(11, "Actvtr:Tray", byObject=1)

objLocks = ptAttribSceneobjectList(12, "Objct:Locks")
respOpenLock = ptAttribResponder(13, "Rspndr:OpenLock", byObject=1)
respCloseLock = ptAttribResponder(14, "Rspndr:CloseLock", byObject=1)
actLock = ptAttribActivator(15, "Actvtr:Lock", byObject=1)

animLockOpen = ptAttribAnimation(16, "open clasp anim", byObject=1)
animLockClose = ptAttribAnimation(17, "close clasp anim", byObject=1)

SeekBehavior = ptAttribBehavior(18, "Smart seek before GUI")  # used to make user walk in front of shelf before using it
ShelfCamera = ptAttribSceneobject(19, "Bookshelf camera")  # the camera used when engaging the shelf
respRaiseShelfClickable = ptAttribResponder(20, "Rspndr:Raise Clickable (LocalOnly)", netForce=0)  # Bill's sneaky way to: 1) engage the bookshelf, and 2) keep others from using a shelf already in use by making it's movement "LocalOnly" in Maxs user properties
respLowerShelfClickable = ptAttribResponder(21, "Rspndr:Lower Clickable")  # undoes the damage in previous step
actDisengageShelf = ptAttribActivator(22, "Actvtr: Disengage Shelf")  # region detector around the SeekBehavior node (#18 above) which detects when a player walks away from the shelf. Only disengages if "exiter" is the current user
HutCamera = ptAttribSceneobject(23, "Hut circle camera")  # the camera which was used before engaging the shelf

actLinkingBookGUIPopup = ptAttribNamedActivator(24, "Actvr: LinkingBook GUI")  # incoming notifies from the open Linking Book GUI

actBookshelfExit = ptAttribActivator(25, "Actvr: Exit bookshelf")

# globals
#==============

# this array defines which age books are on this shelf and where on the shelf they appear
# to add a book, replace an element with the name of the age, for instance: change Link11 to BillsSuperCoolAge
# to change where a book appears on the shelf, change it's position in the array
linkLibrary = ["Neighborhood", "Nexus", "city", "Link03", "Link04", "Cleft", "Garrison",
               "Teledahn", "Kadish", "Gira", "Garden", "Negilahn", "Dereno", "Payiferen",
               "Tetsonot", "Ercana", "AhnonayCathedral", "Ahnonay", "Minkata", "Jalak",
               "Link21", "Link22", "Link23", "Link24", "Link25", "Link26", "Link27", "Link28",
               "Link29", "Link30", "Link31", "Link32", "Link33", "Link34", "Link35", "Myst"]

objBookPicked = None
objLockPicked = None
boolLinkerIsMe = false
boolPresentAfterLockOpen = false
boolShelfBusy = false
SpawnPointName = None
SpawnPointTitle = None
LocalAvatar = None
ShelfAUserID = -1
ShelfABoolOperated = 0
miniKIrestore = 0
boolShelfInUse = 0
AgeStartedIn = None
IsChildLink = 0

stupidHackForLock = None

kPublicBooks = ("Nexus", "Cleft", "City")  # These books cannot be linked to by guests, and cannot be deleted by the owner

# list of ages that show up in the city book
CityBookAges = {"BaronCityOffice": ["BaronCityOffice", "Default"], "Descent": ["dsntShaftFall"],
                "GreatZero": ["grtzGrtZeroLinkRm"], "spyroom": ["Spyroom", "Default"], "Kveer": ["Kveer", "Default"]}


class psnlBookshelf(ptModifier):

    def __init__(self):
        ptModifier.__init__(self)
        self.id = 5012

        version = 10
        minor = 0
        self.version = "{}.{}".format(version, minor)
        PtDebugPrint("__init__: psnlBookshelf v()".format(self.version))
        PtLoadDialog(xVisitorUtils.kVisitorNagDialog)

    def __del__(self):
        PtUnloadDialog(xVisitorUtils.kVisitorNagDialog)

    def OnFirstUpdate(self):
        global AgeStartedIn
        AgeStartedIn = PtGetAgeName()

        self.initComplete = 0
        self.UsingBook = 0

        global boolShelfBusy

        # hide tray clickables
        for tray in objTrays.value:
            tray.draw.disable()

        # make all books invisible (tagged unclickable by default) then IUpdate to draw/enable appropriate books
        for book in objLibrary.value:
            book.draw.disable()

        boolShelfBusy = false
        return

    def OnServerInitComplete(self):
        global stupidHackForLock

        ageVault = ptAgeVault()
        ageInfoNode = ageVault.getAgeInfo()
        locked = 1

        ageInfoChildren = ageInfoNode.getChildNodeRefList()
        for ageInfoChildRef in ageInfoChildren:
            ageInfoChild = ageInfoChildRef.getChild()
            folder = ageInfoChild.upcastToFolderNode()
            if folder and folder.folderGetName() == "AgeData":
                ageDataChildren = folder.getChildNodeRefList()
                for ageDataChildRef in ageDataChildren:
                    ageDataChild = ageDataChildRef.getChild()
                    chron = ageDataChild.upcastToChronicleNode()
                    if chron and chron.getName() == "AhnonayLocked":
                        locked = bool(int(chron.getValue()))
                break

        vault = ptVault()
        if not vault.inMyPersonalAge():
            if stupidHackForLock is None:
                stupidHackForLock = locked

        self.IUpdateLocksAndTrays()

        # if I'm a visitor to this personal age, don't let me mess with book locks or delete books
        if not vault.inMyPersonalAge():
            actLock.disable()
            actTray.disable()

        solo = true
        if len(PtGetPlayerList()):
            solo = false

        self.IUpdateLinks()

        if AgeStartedIn == PtGetAgeName():
            ageSDL = PtGetAgeSDL()
            ageSDL.setNotify(self.key, "ShelfAUserID", 0.0)

            ageSDL.setFlags("ShelfABoolOperated", 1, 1)
            ageSDL.setFlags("ShelfAUserID", 1, 1)

            ageSDL.sendToClients("ShelfABoolOperated")
            ageSDL.sendToClients("ShelfAUserID")

            ageSDL.setFlags("CurrentPage", 1, 1)
            ageSDL.sendToClients("CurrentPage")

            ShelfABoolOperated = ageSDL["ShelfABoolOperated"][0]
            if not solo and ShelfABoolOperated:
                actBookshelf.disable()
                PtDebugPrint("psnlBookshelf.OnServerInitComplete:  ShelfABoolOperated={}, disabling shelf clickable".format(ShelfABoolOperated))
            else:
                PtDebugPrint("psnlBookshelf.OnServerInitComplete:  ShelfABoolOperated={} but no one else here...correcting".format(ShelfABoolOperated))
                self.IResetShelf()

        self.initComplete = 1

    def AvatarPage(self, avObj, pageIn, lastOut):
        "reset Shelf A accessibility if Shelf A user quits or crashes"
        global boolScopeOperated

        if pageIn:
            return

        avID = PtGetClientIDFromAvatarKey(avObj.getKey())

        if AgeStartedIn == PtGetAgeName():
            try:
                ageSDL = PtGetAgeSDL()
                if avID == ageSDL["ShelfAUserID"][0]:
                    PtDebugPrint("psnlBookshelf.AvatarPage():  Bookshelf A operator paged out, reenabled Bookshelf.")
                    self.IResetShelf()
                else:
                    return
            except:
                # probably couldn't find the age SDL yet..
                pass

    def OnAgeVaultEvent(self, event, tupdata):
        PtDebugPrint("psnlBookshelf.OnAgeVaultEvent():  OnAgeKIEvent recvd. Event= {} and data= {}".format(event, tupdata))
        if event == PtVaultCallbackTypes.kVaultConnected:
            PtDebugPrint("psnlBookshelf.OnAgeVaultEvent():  kVaultConnected event")
            # tupdata is ()
        elif event == PtVaultCallbackTypes.kVaultNodeSaved:
            PtDebugPrint("psnlBookshelf.OnAgeVaultEvent():  kVaultNodeSaved event (id={}, type={})".format(tupdata[0].getID(), tupdata[0].getType()))
            # tupdata is ( ptVaultNode )
        elif event == PtVaultCallbackTypes.kVaultNodeRefAdded:
            PtDebugPrint("psnlBookshelf.OnAgeVaultEvent():  kVaultNodeRefAdded event (childID={}, parentID={})".format(tupdata[0].getChildID(), tupdata[0].getParentID()))
            # tupdata is ( ptVaultNodeRef )
            if self.initComplete:
                self.IUpdateLinks()
                self.IUpdateLocksAndTrays()
        elif event == PtVaultCallbackTypes.kVaultRemovingNodeRef:
            PtDebugPrint("psnlBookshelf.OnAgeVaultEvent():  kVaultRemovingNodeRef event (childID={}, parentID={})".format(tupdata[0].getChildID(), tupdata[0].getParentID()))
            # tupdata is ( ptVaultNodeRef )
        elif event == PtVaultCallbackTypes.kVaultNodeRefRemoved:
            PtDebugPrint("psnlBookshelf.OnAgeVaultEvent():  kVaultNodeRefRemoved event (childID, parentID) {}".format(tupdata))
            # tupdata is ( childID, parentID )
        elif event == PtVaultCallbackTypes.kVaultNodeInitialized:
            PtDebugPrint("psnlBookshelf.OnAgeVaultEvent():  kVaultNodeInitialized event (id={}, type={})".format(tupdata[0].getID(), tupdata[0].getType()))
            # tupdata is ( ptVaultNode )
        elif event == PtVaultCallbackTypes.kVaultOperationFailed:
            PtDebugPrint("psnlBookshelf.OnAgeVaultEvent():  kVaultOperationFailed event  (operation, resultCode) {}".format(tupdata))
            # tupdata is ( operation, resultCode )
        else:
            PtDebugPrint("psnlBookshelf.OnAgeVaultEvent():  unknown event!")

    def OnSDLNotify(self, VARname, SDLname, playerID, tag):
        if VARname == "ShelfAUserID":
            ageSDL = PtGetAgeSDL()
            if ageSDL is not None:
                if ageSDL["ShelfAUserID"][0] == -1:
                    actBookshelf.enable()

    def OnNotify(self, state, id, events):
        global objBookPicked
        global boolLinkerIsMe
        global objLockPicked
        global boolPresentAfterLockOpen
        global boolShelfBusy
        global ShelfAUserID
        global ShelfABoolOperated
        global SpawnPointName
        global SpawnPointTitle
        global miniKIrestore
        global boolShelfInUse
        global stupidHackForLock

        if id == actBookshelfExit.id:
            self.IDisengageShelf()
            return

        vault = ptVault()

        if id == SeekBehavior.id and PtGetLocalAvatar() == PtFindAvatar(events):
            for event in events:
                if event[0] == kMultiStageEvent and event[1] == 0:  # Smart seek completed. Exit multistage, and show GUI.
                    LocalAvatar = PtFindAvatar(events)
                    SeekBehavior.gotoStage(LocalAvatar, -1)
                    PtDebugPrint("psnlBookshelf.OnNotify():  engaging bookshelf")

                    LocalAvatar.draw.disable()
                    # set camera to Shelf Camera
                    virtCam = ptCamera()
                    virtCam.save(ShelfCamera.sceneobject.getKey())

                    if PtIsDialogLoaded("KIMini"):
                        miniKI = PtGetDialogFromString("KIMini")
                        if miniKI.isEnabled():
                            miniKIrestore = 1
                            PtHideDialog("KIMini")

                    PtAtTimeCallback(self.key, .5, 1)

        if id == actLinkingBookGUIPopup.id:

            for event in events:
                if event[0] == kVariableEvent:
                    PtDebugPrint("psnlBookshelf.OnNotify():  Received a message from the Book GUI: {}".format(event[1]))
                    if event[1] == "IShelveBook" and objBookPicked is not None:
                        self.IShelveBook()

                    if event[1].split(",")[0] == "ILink":  # parse the spawn point info off the entire note (which comes through as "ILink, SpawnPointName,SpawnPointTitle")
                        if event[3] < 0:  # legacy check (if > 0 then it's from old code and, therefore, not ours)
                            self.IShelveBook()

                            avatar = PtGetLocalAvatar()
                            #reenable First person before linking out
                            cam = ptCamera()
                            cam.enableFirstPersonOverride()

                            #Un-fade local avatar
                            avatar.draw.enable()

                            #Go back to the hut circle cam to avoid re-fade out nastiness
                            virtCam = ptCamera()
                            virtCam.save(HutCamera.sceneobject.getKey())

                            # don't re-eable the movement keys when we are linking out...
                            PtGetControlEvents(false, self.key)

                            SpawnPointName = event[1].split(",")[1]
                            SpawnPointTitle = event[1].split(",")[2]

                            PtDebugPrint("psnlBookshelf.OnNotify():  SpawnPointName = {}; SpawnPointTitle = {}".format(SpawnPointName, SpawnPointTitle))

                            self.IResetShelf()
                            self.SendNote(0)
                            self.ILink()

        if id == (-1):
            if events[0][1] == 'BookShelfBusy':
                PtDebugPrint("psnlBookshelf.OnNotify():  Notified about bookshelf use.")
                boolShelfInUse = events[0][3]
            else:
                for event in events:
                    if event[0] == kVariableEvent:
                        PtDebugPrint("psnlBookshelf.OnNotify():\tevent[11: {}".format(event[1]))
                        PtDebugPrint("psnlBookshelf.OnNotify():\tevent[3]: {}".format(event[3]))
                        if event[1] == "YesNo" and event[3] == 1:
                            link = self.IGetLinkFromBook()

                            bookAge = self.IGetAgeFromBook()
                            if bookAge == "Ahnonay" or bookAge == "AhnonayCathedral":
                                ageVault = ptAgeVault()
                                ageInfoNode = ageVault.getAgeInfo()
                                ageInfoChildren = ageInfoNode.getChildNodeRefList()
                                for ageInfoChildRef in ageInfoChildren:
                                    ageInfoChild = ageInfoChildRef.getChild()
                                    folder = ageInfoChild.upcastToFolderNode()
                                    if folder and folder.folderGetName() == "AgeData":
                                        ageDataFolder = folder
                                        ageDataChildren = folder.getChildNodeRefList()
                                        for ageDataChildRef in ageDataChildren:
                                            ageDataChild = ageDataChildRef.getChild()
                                            chron = ageDataChild.upcastToChronicleNode()
                                            if chron and chron.getName() == "AhnonayVolatile":
                                                if vault.inMyPersonalAge():
                                                    chron.setValue("1")
                                        break

                                PtDebugPrint("psnlBookshelf.OnNotify():  DEBUG: Sending volatile notify (hopefully)")
                                note = ptNotify(self.key)
                                note.setActivate(1.0)
                                note.addVarNumber("VolatileAhnonay", 1)
                                note.send()

                                note = ptNotify(self.key)
                                note.setActivate(1.0)
                                note.addVarNumber("VolatileAhnonayCathedral", 1)
                                note.send()

                                ageVault = ptAgeVault()
                                PAL = ageVault.getAgesIOwnFolder()
                                contents = PAL.getChildNodeRefList()
                                for content in contents:
                                    link = content.getChild()
                                    link = link.upcastToAgeLinkNode()
                                    info = link.getAgeInfo()
                                    if info and info.getAgeFilename() == "AhnonayCathedral":
                                        # found our link
                                        PtDebugPrint("psnlBookshelf.OnNotify():  found Owned link {}".format(info.getAgeFilename()))
                                        link.setVolatile(True)
                                        link.save()

                                for bookName in ["ShelfA_book17", "ShelfA_book18"]:
                                    for rkey, rvalue in respDeleteBook.byObject.items():
                                        parent = rvalue.getParentKey()
                                        if parent:
                                            if bookName == parent.getName():
                                                respDeleteBook.run(self.key, objectName=rkey)
                                                BookNumber = linkLibrary.index(bookAge)
                                                ageSDL = PtGetAgeSDL()
                                                ageSDL.setIndex("CurrentPage", BookNumber, 1)
                                                PtDebugPrint("psnlBookshelf.OnNotify():  Setting CurrentPage var of book {} to 1".format(BookNumber))
                                                break

                                objBookPicked = None
                                return
                            else:
                                # volatile it
                                link.setVolatile(True)
                                link.save()

                            PtDebugPrint("psnlBookshelf.OnNotify():  DEBUG: Sending volatile notify (hopefully)")
                            note = ptNotify(self.key)
                            note.setActivate(1.0)
                            note.addVarNumber("Volatile" + bookAge, 1)
                            note.send()
                            bookName = objBookPicked.getName()
                            for rkey, rvalue in respDeleteBook.byObject.items():
                                parent = rvalue.getParentKey()
                                if parent:
                                    if bookName == parent.getName():
                                        respDeleteBook.run(self.key, objectName=rkey)
                                        BookNumber = linkLibrary.index(bookAge)
                                        ageSDL = PtGetAgeSDL()
                                        ageSDL.setIndex("CurrentPage", BookNumber, 1)
                                        PtDebugPrint("psnlBookshelf.OnNotify():  Setting CurrentPage var of book {} to 1".format(BookNumber))
                                        break

                            objBookPicked = None
                            return

                boolShelfBusy = false
                self.IUpdateLinks()

        # in no other cases do we want to take action on state = 0 events
        if not state:
            return

        if id == actBookshelf.id:
            if PtFindAvatar(events) == PtGetLocalAvatar() and PtWasLocallyNotified(self.key) and not boolShelfInUse:
                actBookshelf.disable()  # want the Shelf clickable to be disabled for all clients
                PtDebugPrint("psnlBookshelf.OnNotify():  disabling clickable")
                PtDebugPrint("psnlBookshelf.OnNotify():  Firing clickable responder")
                respRaiseShelfClickable.run(self.key, netPropagate=0)
                self.SendNote(1)
                self.IUpdateLinks()
                for event in events:
                    if event[0] == kPickedEvent:
                        if event[1]:  # entry event
                            # Disable First Person Camera
                            cam = ptCamera()
                            cam.undoFirstPerson()
                            cam.disableFirstPersonOverride()
                            PtRecenterCamera()
                            LocalAvatar = PtFindAvatar(events)
                            SeekBehavior.run(LocalAvatar)

                            ShelfABoolOperated = 1  # me! I'm the operator
                            if AgeStartedIn == PtGetAgeName():
                                ageSDL = PtGetAgeSDL()
                                ageSDL["ShelfABoolOperated"] = (1,)
                                avID = PtGetClientIDFromAvatarKey(LocalAvatar.getKey())
                                ageSDL["ShelfAUserID"] = (avID,)
                                ShelfAUserID = avID
                                PtDebugPrint("psnlBookshelf.OnNotify():  wrote SDL - Bookshelf A user id = {}".format(avID))

                        break

        if id == actBook.id:
            if PtWasLocallyNotified(self.key):
                boolLinkerIsMe = true

            ageSDL = PtGetAgeSDL()
            CurrentUser = ageSDL["ShelfAUserID"][0]
            avatar = PtGetLocalAvatar()
            myID = PtGetClientIDFromAvatarKey(avatar.getKey())

            boolShelfBusy = true

            actTray.disable()
            actBook.disable()
            actLock.disable()

            # kPickedEvent looks like [ 2, pickflag, picker, picked ]  where picker and picked are SceneObject instances
            for event in events:
                if event[0] == kPickedEvent:
                    objBookPicked = event[3]
                    bookName = objBookPicked.getName()
                    PtDebugPrint("psnlBookshelf.OnNotify():  player picked book named {}".format(bookName))
                    try:
                        index = objLibrary.value.index(objBookPicked)
                    except:
                        PtDebugPrint("psnlBookshelf.OnNotify():  ERROR: couldn't find {} in objLibrary".format(objBookPicked))
                        return

                    if self.IGetAgeFromBook() == "city" and PtIsSinglePlayerMode():
                        ageVault = ptAgeVault()
                        citylink = self.GetOwnedAgeLink(ageVault, "city")
                        bcolink = self.GetOwnedAgeLink(ageVault, "BaronCityOffice")

                        citylinklocked = citylink and citylink.getLocked()
                        bcolinklocked = bcolink and bcolink.getLocked()

                        index = linkLibrary.index("city")
                        objLock = objLocks.value[index]
                        lockName = objLock.getName()

                        # show as locked if both are locked, or one is locked and the other doesn't exist
                        if (citylinklocked is None or citylinklocked) and (bcolinklocked is None or bcolinklocked):
                            # find lock associated with this book
                            objLockPicked = objLocks.value[index]
                            lockName = objLockPicked.getName()
                            # find the corresponding lock open responder modifier
                            for rkey, rvalue in respOpenLock.byObject.items():
                                parent = rvalue.getParentKey()
                                if parent:
                                    if lockName == parent.getName():
                                        respOpenLock.run(self.key, objectName=rkey)
                                        break
                            boolPresentAfterLockOpen = true
                            break
                        else:
                            bookName = objBookPicked.getName()
                            # find the corresponding responder modifier and present the book to the player
                            for rkey, rvalue in respPresentBook.byObject.items():
                                parent = rvalue.getParentKey()
                                if parent:
                                    if bookName == parent.getName():
                                        respPresentBook.run(self.key, objectName=rkey)
                                        break
                        self.UsingBook = 1
                        actBookshelfExit.disable()
                        return

                    elif self.IGetAgeFromBook() == "Ahnonay":
                        locked = 0
                        ageVault = ptAgeVault()
                        ageInfoNode = ageVault.getAgeInfo()

                        ageInfoChildren = ageInfoNode.getChildNodeRefList()
                        for ageInfoChildRef in ageInfoChildren:
                            ageInfoChild = ageInfoChildRef.getChild()
                            folder = ageInfoChild.upcastToFolderNode()
                            if folder and folder.folderGetName() == "AgeData":
                                ageDataChildren = folder.getChildNodeRefList()
                                for ageDataChildRef in ageDataChildren:
                                    ageDataChild = ageDataChildRef.getChild()
                                    chron = ageDataChild.upcastToChronicleNode()
                                    if chron and chron.getName() == "AhnonayLocked":
                                        locked = bool(int(chron.getValue()))

                        if not vault.inMyPersonalAge():
                            if stupidHackForLock is not None:
                                locked = stupidHackForLock

                        if locked:
                            # find lock associated with this book
                            objLockPicked = objLocks.value[index]
                            lockName = objLockPicked.getName()
                            # find the corresponding lock open responder modifier
                            for rkey, rvalue in respOpenLock.byObject.items():
                                parent = rvalue.getParentKey()
                                if parent:
                                    if lockName == parent.getName():
                                        respOpenLock.run(self.key, objectName=rkey)
                                        break
                            boolPresentAfterLockOpen = true
                            break
                        else:
                            bookName = objBookPicked.getName()
                            # find the corresponding responder modifier and present the book to the player
                            for rkey, rvalue in respPresentBook.byObject.items():
                                parent = rvalue.getParentKey()
                                if parent:
                                    if bookName == parent.getName():
                                        respPresentBook.run(self.key, objectName=rkey)
                                        break

                        self.UsingBook = 1
                        actBookshelfExit.disable()
                        return

                    link = self.IGetLinkFromBook()
                    # Do not use the age link node of a Hood child age for the city book clasp!
                    if IsChildLink:
                        link = self.GetOwnedAgeLink(ptAgeVault(), "city")
                    if link is None:
                        return
                    if type(link) != type(ptVaultAgeLinkNode()) or link.getLocked():
                        # find lock associated with this book

                        objLockPicked = objLocks.value[index]
                        lockName = objLockPicked.getName()
                        # find the corresponding lock open responder modifier
                        for rkey, rvalue in respOpenLock.byObject.items():
                            parent = rvalue.getParentKey()
                            if parent:
                                if lockName == parent.getName():
                                    respOpenLock.run(self.key, objectName=rkey)
                                    break
                        boolPresentAfterLockOpen = true
                        break
                    else:
                        bookName = objBookPicked.getName()
                        # find the corresponding responder modifier and present the book to the player
                        for rkey, rvalue in respPresentBook.byObject.items():
                            parent = rvalue.getParentKey()
                            if parent:
                                if bookName == parent.getName():
                                    respPresentBook.run(self.key, objectName=rkey)
                                    break
            self.UsingBook = 1
            actBookshelfExit.disable()
            return

        if id == respPresentBook.id and objBookPicked is not None:
            # book is finished presenting - now link
            if boolLinkerIsMe:
                # tell linking book GUI which age to present
                stringShowMeAge = self.IGetAgeFromBook()
                PtDebugPrint("psnlBookshelf.OnNotify():  send message - show client {} age {}".format(ShelfAUserID, stringShowMeAge))

                note = ptNotify(self.key)
                note.setActivate(1.0)
                note.addVarNumber(stringShowMeAge + "," + str(objLibrary.value.index(objBookPicked)), ShelfAUserID)
                note.send()

            # for now, just shelve the book again
            return

        if id == respShelveBook.id:
            if self.IGetAgeFromBook() == "city" and PtIsSinglePlayerMode():
                ageVault = ptAgeVault()
                citylink = self.GetOwnedAgeLink(ageVault, "city")
                bcolink = self.GetOwnedAgeLink(ageVault, "BaronCityOffice")

                citylinklocked = citylink and citylink.getLocked()
                bcolinklocked = bcolink and bcolink.getLocked()

                index = linkLibrary.index("city")
                objLock = objLocks.value[index]
                lockName = objLock.getName()

                # show as locked if both are locked, or one is locked and the other doesn't exist
                if (citylinklocked is None or citylinklocked) and (bcolinklocked is None or bcolinklocked):
                    lockName = objLockPicked.getName()
                    # find the corresponding responder modifier
                    for rkey, rvalue in respCloseLock.byObject.items():
                        parent = rvalue.getParentKey()
                        if parent:
                            if lockName == parent.getName():
                                respCloseLock.run(self.key, objectName=rkey)
                                objLockPicked = None
                                break

                else:
                    boolShelfBusy = false
                    self.IUpdateLinks()
                return
            link = self.IGetLinkFromBook()
            # Do not use the age link node of a Hood child age for the city book clasp!
            if IsChildLink:
                link = self.GetOwnedAgeLink(ptAgeVault(), "city")
            if link is None:
                return

            if type(link) is str and link == "Ahnonay":
                locked = 0
                ageVault = ptAgeVault()
                ageInfoNode = ageVault.getAgeInfo()

                ageInfoChildren = ageInfoNode.getChildNodeRefList()
                for ageInfoChildRef in ageInfoChildren:
                    ageInfoChild = ageInfoChildRef.getChild()
                    folder = ageInfoChild.upcastToFolderNode()
                    if folder and folder.folderGetName() == "AgeData":
                        ageDataChildren = folder.getChildNodeRefList()
                        for ageDataChildRef in ageDataChildren:
                            ageDataChild = ageDataChildRef.getChild()
                            chron = ageDataChild.upcastToChronicleNode()
                            if chron and chron.getName() == "AhnonayLocked":
                                locked = bool(int(chron.getValue()))
                        break

                if not vault.inMyPersonalAge():
                    if stupidHackForLock is not None:
                        locked = stupidHackForLock

                if locked:
                    lockName = objLockPicked.getName()
                    PtDebugPrint("psnlBookshelf.OnNotify():  setting clasp to locked: {}".format(lockName))
                    for rkey, rvalue in respCloseLock.byObject.items():
                        parent = rvalue.getParentKey()
                        if parent:
                            if lockName == parent.getName():
                                respCloseLock.run(self.key, objectName=rkey)
                                objLockPicked = None
                                return
                else:
                    boolShelfBusy = false
                    self.IUpdateLinks()
                    return

            if type(link) == type(ptAgeLinkStruct()) or link.getLocked():  # close the clasp
                lockName = objLockPicked.getName()
                # find the corresponding responder modifier
                for rkey, rvalue in respCloseLock.byObject.items():
                    parent = rvalue.getParentKey()
                    if parent:
                        if lockName == parent.getName():
                            respCloseLock.run(self.key, objectName=rkey)
                            objLockPicked = None
                            break

            else:
                boolShelfBusy = false
                self.IUpdateLinks()
            return

        if id == actLock.id:
            boolShelfBusy = true

            actTray.disable()
            actBook.disable()
            actLock.disable()

            # kPickedEvent looks like [ 2, pickflag, picker, picked ]  where picker and picked are SceneObject instances
            for event in events:
                if event[0] == kPickedEvent:
                    objLockPicked = event[3]

                    try:
                        index = objLocks.value.index(objLockPicked)
                    except:
                        PtDebugPrint("psnlBookshelf.OnNotify():  ERROR: couldn't find {} in objLocks".format(objLockPicked))
                        return
                    objBookPicked = objLibrary.value[index]
                    lockName = objLockPicked.getName()
                    agename = self.IGetAgeFromBook()

                    if agename == "city" and PtIsSinglePlayerMode():
                        agevault = ptAgeVault()
                        citylink = self.GetOwnedAgeLink(agevault, "city")
                        bcolink = self.GetOwnedAgeLink(agevault, "BaronCityOffice")

                        citylinklocked = citylink and citylink.getLocked()
                        bcolinklocked = bcolink and bcolink.getLocked()

                        if (citylinklocked is None or citylinklocked) and (bcolinklocked is None or bcolinklocked):
                            for rkey, rvalue in respOpenLock.byObject.items():
                                parent = rvalue.getParentKey()
                                if parent:
                                    if lockName == parent.getName():
                                        respOpenLock.run(self.key, objectName=rkey)
                                        break

                            citylink and citylink.setLocked(0)
                            bcolink and bcolink.setLocked(0)
                        else:
                            for rkey, rvalue in respCloseLock.byObject.items():
                                parent = rvalue.getParentKey()
                                if parent:
                                    if lockName == parent.getName():
                                        respCloseLock.run(self.key, objectName=rkey)
                                        break

                            citylink and citylink.setLocked(1)
                            bcolink and bcolink.setLocked(1)

                        if vault.inMyPersonalAge():
                            citylink and citylink.save()
                            bcolink and bcolink.save()

                        return

                    link = self.IGetLinkFromBook()
                    # Do not use the age link node of a Hood child age for the city book clasp!
                    if IsChildLink:
                        link = self.GetOwnedAgeLink(ptAgeVault(), "city")
                    if link is None:
                        return
                    lockName = objLockPicked.getName()

                    if type(link) is str and link == "Ahnonay":
                        ageVault = ptAgeVault()
                        ageInfoNode = ageVault.getAgeInfo()
                        ageInfoChildren = ageInfoNode.getChildNodeRefList()
                        for ageInfoChildRef in ageInfoChildren:
                            ageInfoChild = ageInfoChildRef.getChild()
                            folder = ageInfoChild.upcastToFolderNode()
                            if folder and folder.folderGetName() == "AgeData":
                                ageDataFolder = folder
                                ageDataChildren = folder.getChildNodeRefList()
                                for ageDataChildRef in ageDataChildren:
                                    ageDataChild = ageDataChildRef.getChild()
                                    chron = ageDataChild.upcastToChronicleNode()
                                    if chron and chron.getName() == "AhnonayLocked":
                                        locked = bool(int(chron.getValue()))
                                break

                        if not vault.inMyPersonalAge():
                            if stupidHackForLock is not None:
                                locked = stupidHackForLock

                        PtDebugPrint("psnlBookshelf.OnNotify():  locked: {}".format(locked))
                        if locked:
                            # find the corresponding open clasp responder modifier
                            for rkey, rvalue in respOpenLock.byObject.items():
                                parent = rvalue.getParentKey()
                                if parent:
                                    if lockName == parent.getName():
                                        respOpenLock.run(self.key, objectName=rkey)
                                        break
                            for ageDataChildRef in ageDataChildren:
                                ageDataChild = ageDataChildRef.getChild()
                                chron = ageDataChild.upcastToChronicleNode()
                                if chron and chron.getName() == "AhnonayLocked":
                                    if (vault.inMyPersonalAge()):
                                        PtDebugPrint("psnlBookshelf.OnNotify():  setting lock to 0")
                                        chron.setValue("0")
                        else:
                            # find the corresponding close clasp responder modifier
                            for rkey, rvalue in respCloseLock.byObject.items():
                                parent = rvalue.getParentKey()
                                if parent:
                                    if lockName == parent.getName():
                                        respCloseLock.run(self.key, objectName=rkey)
                                        break
                            for ageDataChildRef in ageDataChildren:
                                ageDataChild = ageDataChildRef.getChild()
                                chron = ageDataChild.upcastToChronicleNode()
                                if chron and chron.getName() == "AhnonayLocked":
                                    if (vault.inMyPersonalAge()):
                                        PtDebugPrint("psnlBookshelf.OnNotify():  setting lock to 1")
                                        chron.setValue("1")

                        if not vault.inMyPersonalAge():
                            stupidHackForLock = not stupidHackForLock

                        return

                    if type(link) != type(ptVaultAgeLinkNode()):
                        self.IUpdateLinks()
                        return

                    if link.getLocked():
                        # find the corresponding open clasp responder modifier
                        for rkey, rvalue in respOpenLock.byObject.items():
                            parent = rvalue.getParentKey()
                            if parent:
                                if lockName == parent.getName():
                                    respOpenLock.run(self.key, objectName=rkey)
                                    break
                        link.setLocked(False)
                        if (vault.inMyPersonalAge()):
                            link.save()
                    else:
                        # find the corresponding close clasp responder modifier
                        for rkey, rvalue in respCloseLock.byObject.items():
                            parent = rvalue.getParentKey()
                            if parent:
                                if lockName == parent.getName():
                                    respCloseLock.run(self.key, objectName=rkey)
                                    break
                        link.setLocked(True)
                        if (vault.inMyPersonalAge()):
                            link.save()
                    break
            return

        if id == respOpenLock.id:
            if boolPresentAfterLockOpen:
                bookName = objBookPicked.getName()
                # find the corresponding responder modifier and present the book to the player
                for rkey, rvalue in respPresentBook.byObject.items():
                    parent = rvalue.getParentKey()
                    if parent:
                        if bookName == parent.getName():
                            respPresentBook.run(self.key, objectName=rkey)
                            break
                boolPresentAfterLockOpen = false
            else:
                boolShelfBusy = false
                self.IUpdateLinks()
            return

        if id == respCloseLock.id:
            boolShelfBusy = false
            self.IUpdateLinks()  # after someone links, need to run this to reenable clickables
            return

        if id == actTray.id:
            boolShelfBusy = true
            actTray.disable()
            actBook.disable()
            actLock.disable()

            # kPickedEvent looks like [ 2, pickflag, picker, picked ]  where picker and picked are SceneObject instances
            for event in events:
                if event[0] == kPickedEvent:
                    objTrayPicked = event[3]
                    break

            # find the corresponding responder modifier and begin deletion
            # responders and animations are on books who are parents of the trays...
            try:
                index = objTrays.value.index(objTrayPicked)
            except:
                PtDebugPrint("psnlBookshelf.OnNotify():  ERROR: couldn't find {} in objTrays".format(objTrayPicked))
                return

            objBookPicked = objLibrary.value[index]
            objLockPicked = objLocks.value[index]

            link = self.IGetLinkFromBook()
            if not link:
                return

            bookAge = self.IGetAgeFromBook()

            if bookAge == "Ahnonay" or bookAge == "AhnonayCathedral":
                ageVault = ptAgeVault()
                ageInfoNode = ageVault.getAgeInfo()
                ageInfoChildren = ageInfoNode.getChildNodeRefList()
                for ageInfoChildRef in ageInfoChildren:
                    ageInfoChild = ageInfoChildRef.getChild()
                    folder = ageInfoChild.upcastToFolderNode()
                    if folder and folder.folderGetName() == "AgeData":
                        ageDataFolder = folder
                        ageDataChildren = folder.getChildNodeRefList()
                        for ageDataChildRef in ageDataChildren:
                            ageDataChild = ageDataChildRef.getChild()
                            chron = ageDataChild.upcastToChronicleNode()
                            if chron and chron.getName() == "AhnonayVolatile":
                                volatile = chron.getValue()
                        break

                if int(volatile):
                    for ageDataChildRef in ageDataChildren:
                        ageDataChild = ageDataChildRef.getChild()
                        chron = ageDataChild.upcastToChronicleNode()
                        if chron and chron.getName() == "AhnonayVolatile":
                            if (vault.inMyPersonalAge()):
                                chron.setValue("0")
                                break

                    PtDebugPrint("psnlBookshelf.OnNotify():  DEBUG: Sending notvolatile notify (hopefully)")
                    note = ptNotify(self.key)
                    note.setActivate(1.0)
                    note.addVarNumber("NotVolatileAhnonay", 1)
                    note.send()

                    note = ptNotify(self.key)
                    note.setActivate(1.0)
                    note.addVarNumber("NotVolatileAhnonayCathedral", 1)
                    note.send()

                    ageVault = ptAgeVault()
                    PAL = ageVault.getAgesIOwnFolder()
                    contents = PAL.getChildNodeRefList()
                    for content in contents:
                        link = content.getChild()
                        link = link.upcastToAgeLinkNode()
                        info = link.getAgeInfo()
                        if info and info.getAgeFilename() == "AhnonayCathedral":
                            # found our link
                            PtDebugPrint("psnlBookshelf.OnNotify():  found Owned link {}".format(info.getAgeFilename()))
                            link.setVolatile(False)
                            link.save()

                    for bookName in ["ShelfA_book17", "ShelfA_book18"]:
                        for rkey, rvalue in respReturnTray.byObject.items():
                            parent = rvalue.getParentKey()
                            if parent:
                                if bookName == parent.getName():
                                    respReturnTray.run(self.key, objectName=rkey)
                                    break
                    objBookPicked = None
                elif vault.inMyPersonalAge():
                    PtYesNoDialog(self.key, PtGetLocalizedString("Personal.Bookshelf.DeleteBook"))

                return

            if link.getVolatile():
                # unvolatile it
                link.setVolatile(False)
                link.save()

                PtDebugPrint("psnlBookshelf.OnNotify():  DEBUG: Sending notvolatile notify (hopefully)")
                note = ptNotify(self.key)
                note.setActivate(1.0)
                note.addVarNumber("NotVolatile" + bookAge, 1)
                note.send()

                bookName = objBookPicked.getName()
                for rkey, rvalue in respReturnTray.byObject.items():
                    parent = rvalue.getParentKey()
                    if parent:
                        if bookName == parent.getName():
                            respReturnTray.run(self.key, objectName=rkey)
                            break
                objBookPicked = None
            elif vault.inMyPersonalAge():
                if bookAge == "Neighborhood":
                    # Don't allow visitors (i.e. non-subscribers) to delete their neighborhood
                    if not PtIsSubscriptionActive():
                        PtShowDialog(xVisitorUtils.kVisitorNagDialog)
                        actTray.enable()
                        actBook.enable()
                        actLock.enable()
                        return

                    PtYesNoDialog(self.key, PtGetLocalizedString("Personal.Bookshelf.DeleteNeighborhoodBook"))
                else:
                    PtYesNoDialog(self.key, PtGetLocalizedString("Personal.Bookshelf.DeleteBook"))

        if id == respReturnTray.id or id == respDeleteBook.id:
            boolShelfBusy = false
            self.IUpdateLinks()
            return

    def IGetLinkFromBook(self, spTitle=None):
        "returns link element associated with global objBookPicked or None"
        global CityBookAges
        global IsChildLink

        # better set this to 0 by default now that we're using it to correct the city book clasp
        IsChildLink = 0

        ageName = self.IGetAgeFromBook()
        PtDebugPrint("psnlBookshelf.IGetLinkFromBook():  before city lookup, ageName = {}".format(ageName))

        isCityLink = 0
        if ageName == "city":
            isCityLink = 1
            for age, splist in CityBookAges.items():
                if spTitle in splist:
                    ageName = age
                    break
        PtDebugPrint("psnlBookshelf.IGetLinkFromBook():  after city lookup, ageName =  {}".format(ageName))

        if ageName is None:
            PtDebugPrint("psnlBookshelf.IGetLinkFromBook():  ERROR: conversion from book to link element failed")
            return None

        if ageName == "Ahnonay":
            PtDebugPrint("psnlBookshelf.IGetLinkFromBook():  Going to Ahnonay... special case.")
            return "Ahnonay"

        hoodInfo = self.IGetHoodInfoNode()
        if hoodInfo:
            childAgeFolder = hoodInfo.getChildAgesFolder()
            contents = childAgeFolder.getChildNodeRefList()
            for content in contents:
                link = content.getChild()
                link = link.upcastToAgeLinkNode()
                if not link:  # Don't break if it's not what you expect...
                    continue

                info = link.getAgeInfo()
                if info and info.getAgeFilename() == ageName:
                    if ageName == "Garrison":
                        continue
                    else:
                        # found our link
                        PtDebugPrint("psnlBookshelf.IGetLinkFromBook():  found Child link {}".format(info.getAgeFilename()))
                        IsChildLink = 1
                        return link

        if isCityLink:
            # if we got here then we're a city link but we couldn't find the child age
            # so we're going to hack it a little bit and force it
            IsChildLink = 1

            ageInfo = ptAgeInfoStruct()
            ageInfo.setAgeFilename(ageName)
            ageInfo.setAgeInstanceName("Ae'gura")

            ageLink = ptAgeLinkStruct()
            ageLink.setAgeInfo(ageInfo)

            return ageLink

        ageVault = ptAgeVault()
        PAL = ageVault.getAgesIOwnFolder()
        contents = PAL.getChildNodeRefList()
        for content in contents:
            link = content.getChild()
            link = link.upcastToAgeLinkNode()
            info = link.getAgeInfo()
            if info and info.getAgeFilename() == ageName:
                # found our link
                PtDebugPrint("psnlBookshelf.IGetLinkFromBook():  found Owned link {}".format(info.getAgeFilename()))
                IsChildLink = 0
                return link

        PtDebugPrint("psnlBookshelf.IGetLinkFromBook():  ERROR: couldn't find link to {}".format(ageName))
        PtDebugPrint("psnlBookshelf.IGetLinkFromBook():\tinfo = {}".format(info))
        PtDebugPrint("psnlBookshelf.IGetLinkFromBook():\tinfo.getAgeFilename() = {}".format(info.getAgeFilename()))
        PtDebugPrint("psnlBookshelf.IGetLinkFromBook():\tspTitle = {}".format(spTitle))
        return None

    def SendNote(self, bool):
        notify = ptNotify(self.key)
        notify.clearReceivers()
        notify.addReceiver(self.key)
        notify.netPropagate(1)
        notify.netForce(1)
        notify.setActivate(1.0)
        notify.addVarNumber('BookShelfBusy', bool)
        notify.send()

    def IUpdateLocksAndTrays(self):
        global CityBookAges

        ageVault = ptAgeVault()
        PAL = ageVault.getAgesIOwnFolder()
        contents = PAL.getChildNodeRefList()

        # check for the dang city book and do stuff
        if self.HasCityBook():
            citylink = self.GetOwnedAgeLink(ageVault, "city")
            #bcolink = self.GetOwnedAgeLink(ageVault, "BaronCityOffice")
            bcolink = self.IGetHoodChildLink("BaronCityOffice")

            citylinklocked = citylink and citylink.getLocked()
            bcolinklocked = bcolink and bcolink.getLocked()

            index = linkLibrary.index("city")
            objLock = objLocks.value[index]
            lockName = objLock.getName()

            # show as locked if both are locked, or one is locked and the other doesn't exist
            if (citylinklocked is None or citylinklocked) and (bcolinklocked is None or bcolinklocked):
                PtDebugPrint("psnlBookshelf.IUpdateLocksAndTrays():  setting city book clasp to locked: {}".format(lockName))
                for rkey, rvalue in respCloseLock.byObject.items():
                    parent = rvalue.getParentKey()
                    if parent:
                        if lockName == parent.getName():
                            respCloseLock.run(self.key, objectName=rkey, fastforward=1)
            else:
                PtDebugPrint("psnlBookshelf.IUpdateLocksAndTrays():  setting city book clasp to unlocked: {}".format(lockName))
                for rkey, rvalue in respOpenLock.byObject.items():
                    parent = rvalue.getParentKey()
                    if parent:
                        if lockName == parent.getName():
                            respOpenLock.run(self.key, objectName=rkey, fastforward=1)

        for content in contents:
            link = content.getChild()
            link = link.upcastToAgeLinkNode()
            info = link.getAgeInfo()
            if not info:
                continue
            ageName = info.getAgeFilename()
            try:
                index = linkLibrary.index(ageName)
            except:
                PtDebugPrint("psnlBookshelf.IUpdateLocksAndTrays():  no matching book for KI's link to: {}...skipping to next".format(ageName))
                continue

            if ((ageName == "city" or ageName == "BaronCityOffice") and PtIsSinglePlayerMode()) or (ageName in CityBookAges.keys()):
                continue

            if ageName == "Cleft":
                if not link.getLocked():
                    link.setLocked(True)
                    vault = ptVault()
                    if vault.inMyPersonalAge():
                        link.save()
                continue

            objLock = objLocks.value[index]
            lockName = objLock.getName()
            if link.getLocked():
                PtDebugPrint("psnlBookshelf.IUpdateLocksAndTrays():  setting clasp to locked: {}".format(lockName))
                for rkey, rvalue in respCloseLock.byObject.items():
                    parent = rvalue.getParentKey()
                    if parent:
                        if lockName == parent.getName():
                            respCloseLock.run(self.key, objectName=rkey, fastforward=1)
            else:
                PtDebugPrint("psnlBookshelf.IUpdateLocksAndTrays():  setting clasp to unlocked: {}".format(lockName))
                for rkey, rvalue in respOpenLock.byObject.items():
                    parent = rvalue.getParentKey()
                    if parent:
                        if lockName == parent.getName():
                            respOpenLock.run(self.key, objectName=rkey, fastforward=1)

            # trays are children of the books...so to manipulate the trays we manipulate the books
            objBook = objLibrary.value[index]
            bookName = objBook.getName()
            if link.getVolatile():
                PtDebugPrint("psnlBookshelf.IUpdateLocksAndTrays():  setting booktray to VOLATILE: {}".format(bookName))
                for rkey, rvalue in respDeleteBook.byObject.items():
                    parent = rvalue.getParentKey()
                    if parent:
                        if bookName == parent.getName():
                            respDeleteBook.run(self.key, objectName=rkey, fastforward=1)
            else:
                PtDebugPrint("psnlBookshelf.IUpdateLocksAndTrays():  setting booktray to NOT volatile: {}".format(bookName))
                for rkey, rvalue in respReturnTray.byObject.items():
                    parent = rvalue.getParentKey()
                    if parent:
                        if bookName == parent.getName():
                            respReturnTray.run(self.key, objectName=rkey, fastforward=1)

        ## Ahnonay Hackage!
        guid = None
        locked = 0
        volatile = 0
        ageVault = ptAgeVault()
        ageInfoNode = ageVault.getAgeInfo()

        ageInfoChildren = ageInfoNode.getChildNodeRefList()
        for ageInfoChildRef in ageInfoChildren:
            ageInfoChild = ageInfoChildRef.getChild()
            folder = ageInfoChild.upcastToFolderNode()
            if folder and folder.folderGetName() == "AgeData":
                ageDataChildren = folder.getChildNodeRefList()
                for ageDataChildRef in ageDataChildren:
                    ageDataChild = ageDataChildRef.getChild()
                    chron = ageDataChild.upcastToChronicleNode()
                    if chron and chron.getName() == "AhnonayLink":
                        guid = chron.getValue()
                    elif chron and chron.getName() == "AhnonayLocked":
                        locked = chron.getValue()
                    elif chron and chron.getName() == "AhnonayVolatile":
                        volatile = chron.getValue()

        if guid is not None:
            try:
                index = linkLibrary.index("Ahnonay")
            except:
                PtDebugPrint("psnlBookshelf.IUpdateLocksAndTrays():  no matching book for KI's link to: Ahnonay... skipping to next")
                return

            objLock = objLocks.value[index]
            lockName = objLock.getName()
            if int(locked):
                PtDebugPrint("psnlBookshelf.IUpdateLocksAndTrays():  setting clasp to locked: {}".format(lockName))
                for rkey, rvalue in respCloseLock.byObject.items():
                    parent = rvalue.getParentKey()
                    if parent:
                        if lockName == parent.getName():
                            respCloseLock.run(self.key, objectName=rkey, fastforward=1)
            else:
                PtDebugPrint("psnlBookshelf.IUpdateLocksAndTrays():  setting clasp to unlocked: {}".format(lockName))
                for rkey, rvalue in respOpenLock.byObject.items():
                    parent = rvalue.getParentKey()
                    if parent:
                        if lockName == parent.getName():
                            respOpenLock.run(self.key, objectName=rkey, fastforward=1)

            # trays are children of the books...so to manipulate the trays we manipulate the books
            objBook = objLibrary.value[index]
            bookName = objBook.getName()
            if int(volatile):
                PtDebugPrint("psnlBookshelf.IUpdateLocksAndTrays():  setting booktray to VOLATILE: {}".format(bookName))
                for rkey, rvalue in respDeleteBook.byObject.items():
                    parent = rvalue.getParentKey()
                    if parent:
                        if bookName == parent.getName():
                            respDeleteBook.run(self.key, objectName=rkey, fastforward=1)
            else:
                PtDebugPrint("psnlBookshelf.IUpdateLocksAndTrays():  setting booktray to NOT volatile: {}".format(bookName))
                for rkey, rvalue in respReturnTray.byObject.items():
                    parent = rvalue.getParentKey()
                    if parent:
                        if bookName == parent.getName():
                            respReturnTray.run(self.key, objectName=rkey, fastforward=1)

        return

    def IUpdateLinks(self):
        global stupidHackForLock
        global CityBookAges

        # ensure all books and trays are not clickable
        #  we're going to display books player has links to and enable clickables on books and associated trays
        actTray.disable()
        actBook.disable()
        actLock.disable()

        vault = ptVault()
        boolInMyAge = vault.inMyPersonalAge()

        # check for the dang city book and do stuff
        if self.HasCityBook():
            ageVault = ptAgeVault()
            citylink = self.GetOwnedAgeLink(ageVault, "city")
            bcolink = self.IGetHoodChildLink("BaronCityOffice")

            citylinklocked = citylink and citylink.getLocked()
            bcolinklocked = bcolink and bcolink.getLocked()

            index = linkLibrary.index("city")
            objBook = objLibrary.value[index]
            objBook.draw.enable()

            bookName = objBook.getName()
            for key, value in actBook.byObject.items():
                parent = value.getParentKey()
                if parent:
                    if bookName == parent.getName():
                        actBook.enable(objectName=key)
                        break

            # find and enable the corresponding clickable modifier for the book's tray and lock if owner
            objTray = objTrays.value[index]
            trayName = objTray.getName()
            objLock = objLocks.value[index]
            lockName = objLock.getName()
            if boolInMyAge:
                for key, value in actLock.byObject.items():
                    parent = value.getParentKey()
                    if parent:
                        if lockName == parent.getName():
                            actLock.enable(objectName=key)
                            break

        ageVault = ptAgeVault()
        PAL = ageVault.getAgesIOwnFolder()
        if PAL is not None:
            contents = PAL.getChildNodeRefList()

            for content in contents:
                link = content.getChild()
                link = link.upcastToAgeLinkNode()
                info = link.getAgeInfo()
                if not info:
                    continue
                ageName = info.getAgeFilename()

                if (ageName == "city" or ageName == "BaronCityOffice") or (ageName in CityBookAges.keys()):
                    continue

                try:
                    index = linkLibrary.index(ageName)
                except:
                    PtDebugPrint("psnlBookshelf.IUpdateLinks():  no matching book for KI's link to: {}...skipping to next".format(ageName))
                    continue

                if ageName == "Cleft":
                    ageSDL = PtGetAgeSDL()
                    boolCleftVisited = ageSDL["CleftVisited"][0]
                    if not boolCleftVisited:
                        continue

                # show the book
                objBook = objLibrary.value[index]
                objBook.draw.enable()

                if boolShelfBusy:
                    # not safe to enable clickables
                    return

                # find and enable the corresponding clickable modifier for the book
                PtDebugPrint("psnlBookshelf.IUpdateLinks():  ageName: {}, boolInMyAge: {}, getLocked(): {}, getVolatile(): {}".format(ageName, boolInMyAge, link.getLocked(), link.getVolatile()))
                if link.getVolatile() or ((not boolInMyAge) and (link.getLocked() or ageName == "Cleft")):
                    bookName = objBook.getName()
                    for key, value in actBook.byObject.items():
                        parent = value.getParentKey()
                        if parent:
                            if bookName == parent.getName():
                                PtDebugPrint("psnlBookshelf.IUpdateLinks():  {} book: DISABLED".format(bookName))
                                actBook.disable(objectName=key)
                                break
                    if (not boolInMyAge) and (link.getLocked() or ageName == "Cleft"):
                        # owner of book has locked this one -- go on to next link element
                        continue

                if not link.getVolatile():
                    bookName = objBook.getName()
                    for key, value in actBook.byObject.items():
                        parent = value.getParentKey()
                        if parent:
                            if bookName == parent.getName():
                                PtDebugPrint("psnlBookshelf.IUpdateLinks():  {} book: ENABLED".format(bookName))
                                actBook.enable(objectName=key)
                                break

                # find and enable the corresponding clickable modifier for the book's tray and lock if owner
                objTray = objTrays.value[index]
                trayName = objTray.getName()
                objLock = objLocks.value[index]
                lockName = objLock.getName()

                if boolInMyAge:
                    # First make sure that we disable locks (i.e sharing) and trays (i.e. deletion) on all public books
                    if ageName in kPublicBooks:
                        continue

                    for key, value in actLock.byObject.items():
                        parent = value.getParentKey()
                        if parent:
                            if lockName == parent.getName():
                                actLock.enable(objectName=key)
                                break

                    for key, value in actTray.byObject.items():
                        parent = value.getParentKey()
                        if parent:
                            if trayName == parent.getName():
                                actTray.enable(objectName=key)
                                break

        else:
            PtDebugPrint("psnlBookshelf.IUpdateLinks():  The PAL folder is missing")

        ## Ahnonay Hackage!
        guid = None
        locked = 0
        volatile = 0
        ageVault = ptAgeVault()
        ageInfoNode = ageVault.getAgeInfo()

        ageInfoChildren = ageInfoNode.getChildNodeRefList()
        for ageInfoChildRef in ageInfoChildren:
            ageInfoChild = ageInfoChildRef.getChild()
            folder = ageInfoChild.upcastToFolderNode()
            if folder and folder.folderGetName() == "AgeData":
                ageDataChildren = folder.getChildNodeRefList()
                for ageDataChildRef in ageDataChildren:
                    ageDataChild = ageDataChildRef.getChild()
                    chron = ageDataChild.upcastToChronicleNode()
                    if chron and chron.getName() == "AhnonayLink":
                        guid = chron.getValue()
                    elif chron and chron.getName() == "AhnonayLocked":
                        locked = bool(int(chron.getValue()))
                    elif chron and chron.getName() == "AhnonayVolatile":
                        volatile = chron.getValue()

        if guid is not None:
            ageName = "Ahnonay"

            try:
                index = linkLibrary.index("Ahnonay")
            except:
                PtDebugPrint("psnlBookshelf.IUpdateLocksAndTrays():  no matching book for KI's link to: Ahnonay... skipping to next")
                return

            # show the book
            objBook = objLibrary.value[index]
            objBook.draw.enable()

            if boolShelfBusy:
                # not safe to enable clickables
                return

            if not vault.inMyPersonalAge():
                if stupidHackForLock is not None:
                    locked = stupidHackForLock

            # find and enable the corresponding clickable modifier for the book
            if int(volatile) or ((not boolInMyAge) and locked):
                bookName = objBook.getName()
                for key, value in actBook.byObject.items():
                    parent = value.getParentKey()
                    if parent:
                        if bookName == parent.getName():
                            PtDebugPrint("psnlBookshelf.IUpdateLinks():  {} book: DISABLED".format(bookName))
                            actBook.disable(objectName=key)
                            break
                if (not boolInMyAge) and int(locked):
                    # owner of book has locked this one -- go on to next link element
                    return

            if not int(volatile):
                bookName = objBook.getName()
                for key, value in actBook.byObject.items():
                    parent = value.getParentKey()
                    if parent:
                        if bookName == parent.getName():
                            PtDebugPrint("psnlBookshelf.IUpdateLinks():  {} book: ENABLED".format(bookName))
                            actBook.enable(objectName=key)
                            break

            # find and enable the corresponding clickable modifier for the book's tray and lock if owner
            objTray = objTrays.value[index]
            trayName = objTray.getName()
            objLock = objLocks.value[index]
            lockName = objLock.getName()

            if boolInMyAge:
                # First make sure that we disable locks (i.e sharing) and trays (i.e. deletion) on all public books
                if ageName in kPublicBooks:
                    return

                for key, value in actLock.byObject.items():
                    parent = value.getParentKey()
                    if parent:
                        if lockName == parent.getName():
                            actLock.enable(objectName=key)
                            break

                for key, value in actTray.byObject.items():
                    parent = value.getParentKey()
                    if parent:
                        if trayName == parent.getName():
                            actTray.enable(objectName=key)
                            break

    def CheckForCityBookSpawnPoint(self, agefilename, sptitle):
        global CityBookAges

        if agefilename in CityBookAges.keys():
            splist = CityBookAges[agefilename]
            if sptitle in splist:
                return 1
        return 0

    def ILink(self):
        global SpawnPointName
        global SpawnPointTitle

        link = self.IGetLinkFromBook(SpawnPointTitle)
        if link is None:
            PtDebugPrint("psnlBookshelf.ILink():  ERROR: conversion from book to link failed -- aborting")
            return
        elif type(link) is str and link == "Ahnonay":
            info = ptAgeInfoStruct()
            info.setAgeFilename("Ahnonay")
            info.setAgeInstanceName("Ahnonay")
            guid = None
            ageVault = ptAgeVault()
            ageInfoNode = ageVault.getAgeInfo()

            ageInfoChildren = ageInfoNode.getChildNodeRefList()
            for ageInfoChildRef in ageInfoChildren:
                ageInfoChild = ageInfoChildRef.getChild()
                folder = ageInfoChild.upcastToFolderNode()
                if folder and folder.folderGetName() == "AgeData":
                    ageDataChildren = folder.getChildNodeRefList()
                    for ageDataChildRef in ageDataChildren:
                        ageDataChild = ageDataChildRef.getChild()
                        chron = ageDataChild.upcastToChronicleNode()
                        if chron and chron.getName() == "AhnonayLink":
                            guid = chron.getValue()
                            PtDebugPrint("psnlBookshelf.ILink():  guid={}".format(guid))
                            break
                    break
            info.setAgeInstanceGuid(guid)

            link = ptAgeLinkStruct()
            link.setAgeInfo(info)

        elif link.getAgeInfo().getAgeFilename() == "Neighborhood" and not PtIsSubscriptionActive():
            info = ptAgeInfoStruct()
            info.setAgeFilename("Neighborhood")
            info.setAgeInstanceGuid("366f9aa1-c4c9-4c4c-a23a-cbe6896cc3b9")
            link = ptAgeLinkStruct()
            link.setAgeInfo(info)

        info = link.getAgeInfo()
        ageName = info.getAgeFilename()

        # do the link
        PtDebugPrint("psnlBookshelf.ILink():  attempting link to {}({})".format(info.getAgeFilename(), info.getAgeInstanceName()))

        PtDebugPrint("psnlBookshelf.ILink():  SpawnPointTitle = {}; SpawnPointName = {}".format(SpawnPointTitle, SpawnPointName))
        spnpnt = None

        if type(link) == type(ptAgeLinkStruct()):
            als = link
        else:
            als = link.asAgeLinkStruct()

            spawnPoints = link.getSpawnPoints()
            for sp in spawnPoints:
                if (sp.getTitle() == SpawnPointTitle and sp.getName() == SpawnPointName) or self.CheckForCityBookSpawnPoint(ageName, SpawnPointTitle):
                    PtDebugPrint("psnlBookshelf.ILink():  found spawn point: {}, {}".format(sp.getTitle(), sp.getName()))
                    if sp.getName() == "BigRoomLinkInPoint":
                        PtDebugPrint("psnlBookshelf.ILink():  oops, found spawnpt for GZ BigRoom, we don't want to link there via city book, so we'll ignore it")
                        break
                    spnpnt = sp
                    break

        if not spnpnt:
            spnpnt = ptSpawnPointInfo(SpawnPointTitle, SpawnPointName)

        PtDebugPrint("psnlBookshelf.ILink():  spnpnt.getTitle() = {}".format(spnpnt.getTitle()))
        PtDebugPrint("psnlBookshelf.ILink():  spnpnt.getName()  = {}".format(spnpnt.getName()))

        als.setSpawnPoint(spnpnt)

        vault = ptVault()

        # If in my personal age, link with kOwnedBook rules.
        #   This will startup a new, private age instance for me.
        if (vault.inMyPersonalAge()):
            if ageName == "Ahnonay" or (ageName == "Neighborhood" and not PtIsSubscriptionActive()):
                als.setLinkingRules(PtLinkingRules.kBasicLink)
            elif IsChildLink:
                PtDebugPrint("psnlBookshelf.ILink():  using kChildAgeBook rules for link to: {}".format(ageName))
                als.setLinkingRules(PtLinkingRules.kChildAgeBook)
                als.setParentAgeFilename("Neighborhood")
            else:
                PtDebugPrint("psnlBookshelf.ILink():  using kOwnedBook rules for link to: {}".format(ageName))
                als.setLinkingRules(PtLinkingRules.kOwnedBook)

        # Otherwise, always use kOriginalBook rules.
        #   The engine will handle whether player becomes co-owner or not.
        else:
            # not using co-ownership right now so visitors use visit books unless going to neighborhood
            if ageName == "Neighborhood":
                als.setLinkingRules(PtLinkingRules.kOriginalBook)
            else:
                als.setLinkingRules(PtLinkingRules.kBasicLink)

        linkMgr = ptNetLinkingMgr()
        linkMgr.linkToAge(als)
        PtDebugPrint("psnlBookshelf.ILink():  ILink Done")

    def IShelveBook(self):
        "returns a picked book to the shelf"
        global objBookPicked
        bookName = objBookPicked.getName()
        for rkey, rvalue in respShelveBook.byObject.items():
            parent = rvalue.getParentKey()
            if parent:
                if bookName == parent.getName():
                    respShelveBook.run(self.key, objectName=rkey)
                    break

        self.UsingBook = 0
        actBookshelfExit.enable()

    def IGetAgeFromBook(self):
        "returns age name associated with global objBookPicked or None"
        global objBookPicked

        # find where book object is in object library
        try:
            index = objLibrary.value.index(objBookPicked)
        except:
            PtDebugPrint("psnlBookshelf.IGetAgeFromBook():  ERROR: couldn't find {} in objLibrary".format(objBookPicked))
            return None

        PtDebugPrint("psnlBookshelf.IGetAgeFromBook():  picked book goes to {}".format(linkLibrary[index]))
        return linkLibrary[index]

    def IResetShelf(self):
        global ShelfABoolOperated
        global ShelfAUserID

        PtDebugPrint("psnlBookshelf.IResetShelf:  Resetting shelf")
        ShelfABoolOperated = 0
        ShelfAUserID = -1
        respLowerShelfClickable.run(self.key)
        actBookshelf.enable()
        if AgeStartedIn == PtGetAgeName():
            ageSDL = PtGetAgeSDL()
            ageSDL["ShelfABoolOperated"] = (0,)
            ageSDL["ShelfAUserID"] = (-1,)

    def IDisengageShelf(self):
        global miniKIrestore

        self.SendNote(0)
        if AgeStartedIn == PtGetAgeName() and not self.UsingBook:
            ageSDL = PtGetAgeSDL()
            CurrentBookshelfUser = ageSDL["ShelfAUserID"][0]

            PtDebugPrint("psnlBookshelf.IDisengageShelf:  Player {} is done with the bookshelf.".format(CurrentBookshelfUser))
            self.IResetShelf()

            avatar = PtGetLocalAvatar()
            myID = PtGetClientIDFromAvatarKey(avatar.getKey())

            if myID == CurrentBookshelfUser:
                PtDebugPrint("psnlBookshelf.IDisengageShelf:  I was the Shelf User, and I'm done with the Shelf now.")

                avatar.draw.enable()
                #reeneable first person
                cam = ptCamera()
                cam.enableFirstPersonOverride()
                # go back to the Hut Circle Cam
                virtCam = ptCamera()
                virtCam.save(HutCamera.sceneobject.getKey())
                PtEnableMovementKeys()
                actBookshelfExit.disable()
                PtGetControlEvents(false, self.key)

                if miniKIrestore:
                    miniKIrestore = 0
                    PtShowDialog("KIMini")

    def OnControlKeyEvent(self, controlKey, activeFlag):
        if controlKey == PlasmaControlKeys.kKeyExitMode or controlKey == PlasmaControlKeys.kKeyMoveBackward:
            self.IDisengageShelf()

    def OnTimer(self, id):
        if id == 1:
            PtGetControlEvents(true, self.key)
            actBookshelfExit.enable()

    def IGetHoodLinkNode(self):
        vault = ptVault()
        folder = vault.getAgesIOwnFolder()
        contents = folder.getChildNodeRefList()
        for content in contents:
            link = content.getChild()
            link = link.upcastToAgeLinkNode()
            if link is not None:
                info = link.getAgeInfo()
            if not info:
                continue
            ageName = info.getAgeFilename()
            if ageName == "Neighborhood":
                return link
        return None

    def IGetHoodInfoNode(self):
        link = self.IGetHoodLinkNode()
        if link is None:
            return None

        info = link.getAgeInfo()
        return info

    def IGetHoodChildLink(self, age):
        hoodInfo = self.IGetHoodInfoNode()
        if hoodInfo:
            childAgeFolder = hoodInfo.getChildAgesFolder()
            if childAgeFolder is not None:
                contents = childAgeFolder.getChildNodeRefList()
                for content in contents:
                    link = content.getChild().upcastToAgeLinkNode()
                    if not link:  # Don't break if corrupt/not agelink
                        continue

                    info = link.getAgeInfo()
                    if not info:
                        continue
                    ageName = info.getAgeFilename()
                    if ageName == age:
                        return link
        return None

    def HasCityBook(self):
        #####
        #  COMMENT OUT THIS LINE TO RESTORE THE CITY BOOK:
        #return 0
        #####
        global CityBookAges

        vault = ptVault()
        if not vault.amOwnerOfCurrentAge():
            ageSDL = PtGetAgeSDL()
            GotBook = ageSDL["psnlGotCityBook"][0]
            if GotBook:
                PtDebugPrint("psnlBookshelf.HasCityBook():  owner has the city book")
                return 1
            else:
                PtDebugPrint("psnlBookshelf.HasCityBook():  owner does NOT have city book")
                return 0

        CityLinks = []
        vault = ptVault()
        entryCityLinks = vault.findChronicleEntry("CityBookLinks")
        if entryCityLinks is not None:
            valCityLinks = entryCityLinks.chronicleGetValue()
            PtDebugPrint("psnlBookshelf.HasCityBook():  valCityLinks = {}".format(valCityLinks))
            CityLinks = valCityLinks.split(",")
            PtDebugPrint("psnlBookshelf.HasCityBook():  CityLinks = {}".format(CityLinks))
            for tmpLink in CityLinks:
                if tmpLink in xLinkingBookDefs.CityBookLinks:
                    return 1
        else:
            PtDebugPrint("psnlBookshelf.HasCityBook():  can't find CityBookLinks chron entry")
        return 0

        vault = ptAgeVault()
        # look for city book age links
        for age, splist in CityBookAges.items():
            agelink = self.IGetHoodChildLink(age)
            PtDebugPrint("psnlBookshelf.HasCityBook():  age =     {}".format(age))
            PtDebugPrint("psnlBookshelf.HasCityBook():  agelink = {}".format(agelink))

            if agelink is not None:
                spawnPoints = agelink.getSpawnPoints()

                for sp in spawnPoints:
                    PtDebugPrint("psnlBookshelf.HasCityBook():\tsp          = {}".format(sp))
                    PtDebugPrint("psnlBookshelf.HasCityBook():\tsp.getTitle = {}".format(sp.getTitle()))
                    PtDebugPrint("psnlBookshelf.HasCityBook():\tsp.getName  = {}".format(sp.getName()))
                    if sp.getTitle() in splist:
                        PtDebugPrint("psnlBookshelf.HasCityBook():  found a city book link: {}, {}".format(age, sp.getTitle()))
                        return 1

        # look for a city treasure link, but it's a Hood childage now
        agelink = self.IGetHoodChildLink(age)
        PtDebugPrint("psnlBookshelf.HasCityBook():  age     = the city")
        PtDebugPrint("psnlBookshelf.HasCityBook():  agelink = {}".format(agelink))

        if agelink is not None:
            spawnPoints = agelink.getSpawnPoints()

            for sp in spawnPoints:
                PtDebugPrint("psnlBookshelf.HasCityBook():\tsp          = {}".format(sp))
                PtDebugPrint("psnlBookshelf.HasCityBook():\tsp.getTitle = {}".format(sp.getTitle()))
                PtDebugPrint("psnlBookshelf.HasCityBook():\tsp.getName  = {}".format(sp.getName()))
                if sp.getTitle() in xLinkingBookDefs.CityBookLinks:
                    PtDebugPrint("psnlBookshelf.HasCityBook():  found a city book link: city {}".format(sp.getTitle()))
                    return 1

        # no BCO or city treasure link
        PtDebugPrint("psnlBookshelf.HasCityBook():  found no city book links")
        return 0

    def GetOwnedAgeLink(self, vault, age):
        PAL = vault.getAgesIOwnFolder()
        if PAL is not None:
            contents = PAL.getChildNodeRefList()
            for content in contents:
                link = content.getChild().upcastToAgeLinkNode()
                info = link.getAgeInfo()
                if not info:
                    continue
                ageName = info.getAgeFilename()
                PtDebugPrint("psnlBookshelf.GetOwnedAgeLink():  found {}, looking for {}".format(ageName, age))
                if ageName == age:
                    return link

        return None
