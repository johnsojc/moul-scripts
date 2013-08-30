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
Module: xSaveCloth
Age: Most post-prime ages
Date: January 2004
Author: Adam Van Ornum
Sets a save point
"""

from Plasma import *
from PlasmaTypes import *


# define the attributes that will be entered in max
Activator = ptAttribActivator(1, "Activator: Cloth Clickable")
OneShotResp = ptAttribResponder(2, "Resp: One Shot")
AnimResp = ptAttribResponder(3, "Anim responder", netForce=1)
soSpawnpoint = ptAttribSceneobject(4, "Spawn point scene object")
numSC = ptAttribInt(5, "SaveCloth #:")


# globals
CAM_DIVIDER = "~"
sdlBase = "GotSaveCloth"
sdlSC = ""
gotSC = 0

# constants
kMaxSC = 7


class xSaveCloth(ptModifier):
    def __init__(self):
        ptModifier.__init__(self)
        self.id = 5324
        version = 2
        minor = 0
        self.version = "{}.{}".format(version, minor)
        PtDebugPrint("__init__: xSaveCloth v{}".format(self.version))

    def OnFirstUpdate(self):
        pass

    def OnServerInitComplete(self):
        global sdlSC
        global gotSC

        linkmgr = ptNetLinkingMgr()
        link = linkmgr.getCurrAgeLink()
        spawnPoint = link.getSpawnPoint()

        spTitle = spawnPoint.getTitle()
        spName = spawnPoint.getName()

        PtDebugPrint("xSaveCloth.OnserverInitComplete():  spawned into {}, this save cloth handles {}".format(spName, soSpawnpoint.value.getName()))
        if spTitle.endswith("SavePoint") and spName == soSpawnpoint.value.getName():
            PtDebugPrint("xSaveCloth.OnserverInitComplete():  restoring camera stack for save point {}, {}".format(spTitle, spName))

            # Restore camera stack
            camstack = spawnPoint.getCameraStack()
            PtDebugPrint("xSaveCloth.OnserverInitComplete():  camera stack:{}".format(camstack))
            if camstack != "":
                PtClearCameraStack()
                camlist = camstack.split(CAM_DIVIDER)

                age = PtGetAgeName()
                for x in camlist:
                    PtDebugPrint("adding camera: |{}|".format(x))
                    try:
                        PtRebuildCameraStack(x, age)
                    except:
                        PtDebugPrint("xSaveCloth.OnserverInitComplete():  ERROR: xSaveCloth.OnServerInitComplete: problem rebuilding camera stack...continuing")
            # Done restoring camera stack

        # SaveCloth SDL stuff, for use with POTS symbols
        if not (numSC.value > 0 and numSC.value <= kMaxSC):
            PtDebugPrint("xSaveCloth.OnServerInitComplete():  ERROR: invalid save cloth # of {}, specified in MAX component.  Please revise...".format(numSC.value))
            return
        ageName = PtGetAgeName()
        if ageName == "Ercana":
            sdlPre = "erca"
        else:
            PtDebugPrint("xSaveCloth.OnServerInitComplete():  xSaveCloth.py not updated for this age's SDL.  Ignoring SaveCloth SDL stuff...")
            return

        sdlSC = sdlPre + sdlBase + str(numSC.value)
        try:
            ageSDL = PtGetAgeSDL()
            ageSDL.setFlags(sdlSC, 1, 1)
            ageSDL.sendToClients(sdlSC)
            ageSDL.setNotify(self.key, sdlSC, 0.0)
            gotSC = ageSDL[sdlSC][0]
        except:
            PtDebugPrint("xSaveCloth.OnServerInitComplete():  ERROR: Couldn't find sdl: {}, defaulting to 0".format(sdlSC))

    def OnSDLNotify(self, VARname, SDLname, playerID, tag):
        global gotSC

        if VARname != sdlSC:
            return
        ageSDL = PtGetAgeSDL()
        PtDebugPrint("xSaveCloth.OnSDLNotify():  VARname:{}, SDLname:{}, tag:{}, value:{}".format(VARname, SDLname, tag, ageSDL[sdlSC][0]))
        gotSC = ageSDL[sdlSC][0]

    def OnNotify(self, state, id, events):
        global ClothInUse
        global CAM_DIVIDER

        if not state:
            return

        if id == Activator.id:
            Activator.disable()
            OneShotResp.run(self.key, events=events)  # run the oneshot
            return

        elif id == OneShotResp.id:
            vault = ptVault()
            if vault.amOwnerOfCurrentAge() and PtWasLocallyNotified(self.key):
                PtDebugPrint("DEBUG: xSaveCloth.OnNotify():  am owner of current age, getting save point")
                try:
                # Save the camera stack
                    camstack = ""
                    numcams = PtGetNumCameras()
                    for x in range(numcams):
                        camstack += (PtGetCameraNumber(x+1) + CAM_DIVIDER)
                    camstack = camstack[:-1]

                    PtDebugPrint("xSaveCloth.OnNotify():  camera stack:{}".format(camstack))

                    # camera stack is now being saved as a spawn point on the owned age link
                    vault = ptVault()
                    ainfo = ptAgeInfoStruct()
                    savepoint = None
                    ainfo.setAgeFilename(PtGetAgeName())
                    agelink = vault.getOwnedAgeLink(ainfo)

                    if agelink is not None:
                        spawnpoints = agelink.getSpawnPoints()

                        for sp in spawnpoints:
                            if sp.getTitle() == "SCSavePoint":
                                savepoint = sp
                                break

                        if savepoint is not None:
                            agelink.removeSpawnPoint(savepoint.getName())

                        savepoint = ptSpawnPointInfo("SCSavePoint", soSpawnpoint.value.getName())
                        savepoint.setCameraStack(camstack)

                        agelink.addSpawnPoint(savepoint)
                        agelink.save()
                    # Done saving the camera stack
                except:
                    PtDebugPrint("xSaveCloth.OnNotify():  ERROR: Error occurred doing the whole save point thing")

            AnimResp.run(self.key, events=events)

            if soSpawnpoint.sceneobject.isLocallyOwned():
                if not gotSC:
                    ageSDL = PtGetAgeSDL()
                    ageSDL[sdlSC] = (1,)

        elif id == AnimResp.id:
            Activator.enable()

        else:
            PtDebugPrint("xSaveCloth.OnNotify():  ERROR: Error trying to access the Vault.")
