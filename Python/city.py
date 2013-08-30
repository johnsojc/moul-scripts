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
Module: City.py
Age: City
Date: October 2002
event manager hooks for the City
"""

from Plasma import *
from PlasmaTypes import *

IsPublic = 0
IsKadishGallery = 0

sdlS1FinaleBahro = ["islmS1FinaleBahro", "islmS1FinaleBahroCity1", "islmS1FinaleBahroCity2",
                    "islmS1FinaleBahroCity3", "islmS1FinaleBahroCity4", "islmS1FinaleBahroCity5",
                    "islmS1FinaleBahroCity6"]
pagesS1FinaleBahro = ["bahroFlyers_arch", "bahroFlyers_city1", "bahroFlyers_city2",
                      "bahroFlyers_city3", "bahroFlyers_city4", "bahroFlyers_city5",
                      "bahroFlyers_city6"]


class city(ptResponder):

    def __init__(self):
        ptResponder.__init__(self)
        self.id = 5026
        version = 1
        minor = 0
        self.version = "{}.{}".format(version, minor)
        PtDebugPrint("__init__: city v{}".format(self.version))

        global IsPublic
        global IsKadishGallery

        parentname = None

        try:
            agevault = ptAgeVault()
            ageinfo = agevault.getAgeInfo()
            parent = ageinfo.getParentAgeLink()
            parentinfo = parent.getAgeInfo()
            parentname = parentinfo.getAgeFilename()
        except:
            pass

        if parentname == "Neighborhood":
            IsPublic = 1
            PtDebugPrint("city.__init__():  city version = public")
        else:
            PtDebugPrint("city.__init__():  city version = Yeesha")

        if not IsPublic:
            pass

        try:
            linkmgr = ptNetLinkingMgr()
            link = linkmgr.getCurrAgeLink()
            spawnPoint = link.getSpawnPoint()
            spTitle = spawnPoint.getTitle()
            spName = spawnPoint.getName()
        except:
            spTitle = "title unknown"
            spName = "spawn point unknown"

        PtDebugPrint("city.__init__():  spTitle      = {}".format(spTitle))
        PtDebugPrint("city.__init__():  spName       = {}".format(spName))

        pages = []

        # For the non-public age, add all the remaining pages
        if not IsKadishGallery:
            pages += ["canyon", "cavetjunction", "courtyard", "ferry", "greatstair"]
            pages += ["guildhall", "harbor", "HarborReflect", "islmGreatZeroState"]
            pages += ["islmJCNote", "islmNegilahnCreatureChartGUI", "islmNickNote"]
            pages += ["islmPodMapGUI", "islmWatsonLetterGUI", "KahloPub", "kahlopubtunnel"]
            pages += ["library", "LibraryInterior", "MuseumInteriorPage", "palace"]
            pages += ["trailerCamPage", "islmBahroShoutFerry", "islmBahroShoutLibrary"]
            pages += ["islmBahroShoutPalace"]

            PtPageInNode(pages)

    def OnFirstUpdate(self):
        pass

    def OnServerInitComplete(self):
        try:
            ageSDL = PtGetAgeSDL()
            n = 0
            for sdl in sdlS1FinaleBahro:
                ageSDL.setFlags(sdl, 1, 1)
                ageSDL.sendToClients(sdl)
                ageSDL.setNotify(self.key, sdl, 0.0)
                val = ageSDL[sdl][0]
                if val:
                    self.ILoadS1FinaleBahro(n, 1)
                n += 1
        except:
            PtDebugPrint("city.OnServerInitComplete():  ERROR: Couldn't find all Bahro sdl, leaving default = 0")

    def Load(self):
        pass

    def OnNotify(self, state, id, events):
        pass

    def OnSDLNotify(self, VARname, SDLname, playerID, tag):
        ageSDL = PtGetAgeSDL()
        PtDebugPrint("city.OnSDLNotify():  VARname: {}, SDLname: {}, tag: {}, value: {}".format(VARname, SDLname, tag, ageSDL[VARname][0]))

        if VARname in sdlS1FinaleBahro:
            id = sdlS1FinaleBahro.index(VARname)
            val = ageSDL[sdlS1FinaleBahro[id]][0]
            self.ILoadS1FinaleBahro(id, val)

    def ILoadS1FinaleBahro(self, bahro, state):
        PtDebugPrint("city.ILoadS1FinaleBahro():  bahro = {}, load = {}".format(bahro, state))
        if state:
            PtPageInNode(pagesS1FinaleBahro[bahro])
        else:
            PtPageOutNode(pagesS1FinaleBahro[bahro])

    def OnBackdoorMsg(self, target, param):
        if target == "kadishgallerydoors":
            ageSDL = PtGetAgeSDL()
            ageSDL.setFlags("islmKadishGalleryDoorVis", 1, 1)
            ageSDL.sendToClients("islmKadishGalleryDoorVis")
            ageSDL.setNotify(self.key, "islmKadishGalleryDoorVis", 0.0)
            tmpdoors = ageSDL["islmKadishGalleryDoorVis"][0]
            if param == "on" or param == "1":
                if not tmpdoors:
                    ageSDL["islmKadishGalleryDoorVis"] = (1,)
            elif param == "off" or param == "0":
                if tmpdoors:
                    ageSDL["islmKadishGalleryDoorVis"] = (0,)
        elif target == "s1finale":
            if param == "on" or param == "1":
                n = 0
                for p in pagesS1FinaleBahro:
                    self.ILoadS1FinaleBahro(n, 1)
                    n += 1
            elif param == "off" or param == "0":
                n = 0
                for p in pagesS1FinaleBahro:
                    self.ILoadS1FinaleBahro(n, 0)
                    n += 1
