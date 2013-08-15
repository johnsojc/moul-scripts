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
Module: xPsnlVaultSDL
Age: Global
Date: June 2003
Author: Adam Van Ornum
Allows ptSDL-like access to Psnl Age SDL from anywhere
"""

from Plasma import *
from PlasmaConstants import *
import types


class xPsnlVaultSDL:
    def __init__(self, useAgeVault=0):
        if useAgeVault:
            self.useAgeVault = 1
            self.vault = ptAgeVault()
        else:
            self.useAgeVault = 0
            self.vault = ptVault()

    def __getitem__(self, sub):
        if self.useAgeVault:
            sdl = self.vault.getAgeSDL()
        else:
            sdl = self.vault.getPsnlAgeSDL()

        var = sdl.findVar(sub)
        retval = self.IGetVar(var)

        return (retval,)

    def __setitem__(self, sub, val):

        if type(val) is tuple:
            val = val[0]
        else:
            raise ValueError("Value must be tuple type")

        if self.useAgeVault:
            sdl = self.vault.getAgeSDL()
        else:
            sdl = self.vault.getPsnlAgeSDL()

        var = sdl.findVar(sub)
        self.ISetVar(var, val)

        if self.useAgeVault:
            self.vault.updateAgeSDL(sdl)
        else:
            self.vault.updatePsnlAgeSDL(sdl)

    def IGetVar(self, var):
        vartype = var.getType()

        if vartype == PtSDLVarType.kInt:
            retval = var.getInt()

        elif vartype == PtSDLVarType.kFloat:
            retval = var.getFloat()

        elif vartype == PtSDLVarType.kDouble:
            retval = var.getDouble()

        elif vartype == PtSDLVarType.kBool:
            retval = var.getBool()

        elif vartype == PtSDLVarType.kString32:
            retval = var.getString()

        else:
            retval = var.getInt()

        return retval

    def ISetVar(self, var, val):
        vartype = var.getType()

        if vartype == PtSDLVarType.kInt:
            if type(val) in (types.IntType, types.LongType):
                var.setInt(val)

        elif vartype == PtSDLVarType.kFloat:
            if type(val) in (types.IntType, types.LongType, types.FloatType):
                var.setFloat(val)

        elif vartype == PtSDLVarType.kDouble:
            if type(val) in (types.IntType, types.LongType, types.FloatType):
                var.setDouble(val)

        elif vartype == PtSDLVarType.kBool:
            if val:
                var.setBool(1)
            else:
                var.setBool(0)

        elif vartype == PtSDLVarType.kString32:
            if type(val) is str:
                var.setString(val)
            else:
                var.setString(str(val))

        else:
            if type(val) in (types.IntType, types.LongType):
                var.setInt(val)

    def BatchGet(self, vars):
        retval = {}
        if self.useAgeVault:
            sdl = self.vault.getAgeSDL()
        else:
            sdl = self.vault.getPsnlAgeSDL()

        for sub in vars:
            var = sdl.findVar(sub)
            retval[sub] = self.IGetVar(var)

        return retval

    def BatchSet(self, vars):
        if self.useAgeVault:
            sdl = self.vault.getAgeSDL()
        else:
            sdl = self.vault.getPsnlAgeSDL()

        for sub in vars:
            var = sdl.findVar(sub[0])
            vallist = sub[1]
            self.ISetVar(var, vallist[0])

        if self.useAgeVault:
            self.vault.updateAgeSDL(sdl)
        else:
            self.vault.updatePsnlAgeSDL(sdl)
