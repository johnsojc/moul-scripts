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
"""Module: krelPodium.py
Age: Kirel Neighborhood
Author: Doug McBride
Date: January 2004
"""

from Plasma import *
from PlasmaTypes import *

# define the attributes that will be entered in 3dsMAX
actSwitch01 = ptAttribActivator(1, "act: Podium Button")
respButtonOneshot = ptAttribResponder(2, "resp: Push Podium oneshot")
respSpeech01 = ptAttribResponder(3, "resp: Speech #1")
respSilence = ptAttribResponder(4, "resp: Shut all speeches off")

#globals
ElapsedTime = 0
SecondsToCharge = 60
baton = 0
ElevatorDelay = 5
Resetting = 0


class krelPodium(ptResponder):

    def __init__(self):
        # run parent class init
        ptResponder.__init__(self)
        self.id = 5245

        version = 2
        minor = 0
        self.version = "{}.{}".format(version, minor)
        PtDebugPrint("__init__: krelPodium v{}".format(self.version))

    def OnServerInitComplete(self):
        try:
            ageSDL = PtGetAgeSDL()
        except:
            PtDebugPrint("krelPodium.OnServerInitComplete():  ERROR: Cannot find the Kirel Age SDL")
            ageSDL["nb01CmnRmSpeech"] = (0, )

        ageSDL.setNotify(self.key, "nb01CmnRmSpeech", 0.0)
        ageSDL.sendToClients("nb01CmnRmSpeech")
        ageSDL.setFlags("nb01CmnRmSpeech", 1, 1)
        nb01CmnRmSpeech = ageSDL["nb01CmnRmSpeech"][0]
        ageSDL["nb01CmnRmSpeech"] = (0, )

    def OnNotify(self, state, id, events):
        ageSDL = PtGetAgeSDL()

        PtDebugPrint("krelPodium.OnNotify():  state={:f} id={} events={}".format(state, id, events))

        if not state:
            return

        if id == actSwitch01.id:
            respButtonOneshot.run(self.key, events=events)
            return

        elif id == respButtonOneshot.id and self.sceneobject.isLocallyOwned():
            PtDebugPrint("##")
            nb01CmnRmSpeech = ageSDL["nb01CmnRmSpeech"][0]

            if nb01CmnRmSpeech == 0:  # No speech was playing
                PtDebugPrint("krelPodium.OnNotify():  No speech was previously playing. Playing speech #1.")
                respSpeech01.run(self.key)
                ageSDL["nb01CmnRmSpeech"] = (1,)

            else:
                PtDebugPrint("krelPodium.OnNotify():  Speech #1 was stopped manually by the avatar.")
                respSilence.run(self.key)
                ageSDL["nb01CmnRmSpeech"] = (0,)

        elif id == respSpeech01.id:
            PtDebugPrint("krelPodium.OnNotify():  Speech #1 was stopped automatically after it finished playing.")
            respSilence.run(self.key)
            ageSDL["nb01CmnRmSpeech"] = (0,)
