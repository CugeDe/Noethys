#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import os
import sys
import shutil


def GetRepTemp(fichier=""):
    chemin = GetRepUtilisateur("Temp")
    return os.path.join(chemin, fichier)

def GetRepUpdates(fichier=""):
    chemin = GetRepUtilisateur("Updates")
    return os.path.join(chemin, fichier)


def GetRepUtilisateur(fichier=""):
    """ Recherche le r�pertoire Utilisateur pour stockage des fichiers de config et provisoires """
    chemin = None

    # Variable d'environnement
    for evar in ('XDG_CONFIG_HOME', 'LOCALAPPDATA', 'APPDATA'):
        path = os.environ.get(evar, None)
        if path and os.path.isdir(path):
            chemin = path
            break
    if not chemin:
        # ... ou r�pertoire de l'utilisateur
        path = os.path.expanduser("~")
        if path != "~" and os.path.isdir(path):
            if sys.platform.startswith('linux'):
                chemin = os.path.join(path, '.config')
            else:
                chemin = path
        # ... ou dossier courrant.
        else:
            chemin = os.path.dirname(os.path.abspath(__file__))

    # Ajoute 'noethys' dans le chemin et cr�ation du r�pertoire
    chemin = os.path.join(chemin, "noethys")
    if not os.path.isdir(chemin):
        os.mkdir(chemin)

    # Ajoute le dirname si besoin
    return os.path.join(chemin, fichier)

def DeplaceFichiers():
    """ V�rifie si des fichiers du r�pertoire Data ou du r�pertoire Utilisateur sont � d�placer vers le r�pertoire Utilisateur>AppData>Roaming """
    for nom in ("journal.log", "Config.dat", "Customize.ini") :
        for rep in ("", "Data", os.path.join(os.path.expanduser("~"), "noethys")) :
            fichier = os.path.join(rep, nom)
            if os.path.isfile(fichier) :
                nouveauNom = GetRepUtilisateur(nom)
                shutil.move(fichier, nouveauNom)




if __name__ == "__main__":
    # Test les chemins
    print "Chemin Fichier config =", GetRepUtilisateur("Config.dat")

    # Test les d�placements de fichiers
    DeplaceFichiers()
