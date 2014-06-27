#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import os
import sys


def AdaptePolice(ctrl):
    """ Adapte la taille de la police du ctrl donn� """
    taille = 8
    if "linux" in sys.platform :
        ft = ctrl.GetFont()
        ft.SetPointSize(taille)
        ctrl.SetFont(ft)


def AdaptationsDemarrage():
    """ Adaptations au d�marrage de Noethys """
    # V�rifie que le chemin est ok
    os.chdir(sys.path[0])
    # V�rifie que les r�pertoires vides sont bien l�
    for rep in ("Temp", "Updates", "Aide") :
        if os.path.isdir(rep) == False :
            os.remove(rep)
            try :
                os.mkdir(rep)
            except Exception, err:
                pass


if __name__ == "__main__":
    AdaptationsDemarrage()