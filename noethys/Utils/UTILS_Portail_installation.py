#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
import os
import os.path
import ftplib
import time
import urllib
import urllib2
import zipfile
import shutil
import UTILS_Fichiers
import UTILS_Portail_synchro
import traceback
import sys
import importlib
import json


LISTE_EXCEPTIONS = ["*.pyc", "*.db", "*.db3", "*.exe"]

def IsException(name):
    if name in LISTE_EXCEPTIONS :
        return True
    for item in LISTE_EXCEPTIONS :
        if "*" in item :
            if name.endswith(item.replace("*", "")) :
                return True
    return False

def GetNbreFichiers(rep="") :
    """ R�cup�ration du nombre des fichiers � transf�rer """
    def listdirectory(path):
        fichier=[]
        for root, dirs, files in os.walk(path):
            for i in files:
                if IsException(i) == False :
                    fichier.append(os.path.join(root, i))
        return fichier
    return len(listdirectory(rep))

def AffichetailleFichier(url):
    try :
        fichier = urllib2.urlopen(url)
        infoFichier = (fichier.info().getheaders('Content-Length'))
        if len(infoFichier) > 0 :
            tailleFichier = infoFichier[0]
        else :
            tailleFichier = 0
    except IOError :
        tailleFichier = 0
    return int(tailleFichier)

def GetPourcentage(index, taille):
    return int(index*100/taille)

def FormateTailleFichier(taille):
    if 0 <= taille <1000 :
        texte = str(taille) + " octets"
    elif 1000 <= taille < 1000000 :
        texte = str(taille/1000) + " Ko"
    else :
        texte = str(taille/1000000) + " Mo"
    return texte

def GetExclusions(liste_versions=[], version_ancienne=""):
    """ R�cup�ration de la liste des exclusions entre 2 num�ros de versions """
    """ Cette astuce permet d'all�ger le t�l�chargement des mises � jour de Connecthys """
    nbre_versions = None
    dict_exclusions = {}
    for dictVersion in liste_versions :

        # Recherche de la version actuelle
        if dictVersion["version"] == version_ancienne :
            nbre_versions = 0

        else :

            # Recherche les exclusions � partir de la version trouv�e
            if nbre_versions != None :

                if dictVersion.has_key("exclusions") :
                    for exclusion in dictVersion["exclusions"] :
                        if not dict_exclusions.has_key(exclusion) :
                            dict_exclusions[exclusion] = 0
                        dict_exclusions[exclusion] += 1

                nbre_versions += 1

    liste_exclusions = []
    for exclusion, nbre in dict_exclusions.iteritems() :
        if nbre == nbre_versions :
            liste_exclusions.append(exclusion)

    return liste_exclusions






class Abort(Exception):
    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        return repr(self.value)



class Installer():
    def __init__(self, dict_parametres={}):
        self.dict_parametres = dict_parametres

        self.url_telechargement = "https://github.com/Noethys/Connecthys/archive/master.zip"
        self.nom_fichier_dest = UTILS_Fichiers.GetRepTemp(fichier="connecthys.zip")
        self.index = 0

    def Telecharger(self):
        """ T�l�chargement de la source depuis Github """
        def _hook(nb_blocs, taille_bloc, taille_fichier):
            if nb_blocs % 5 == 0 :
                pourcentage = GetPourcentage(nb_blocs*taille_bloc, taille_fichier)
                keepGoing, skip = self.dlgprogress.Update(pourcentage, _(u"T�l�chargement de Connecthys en cours... %s %%") % pourcentage)
                if keepGoing == False :
                    raise Abort(u"T�l�chargement interrompu")

        urllib.urlretrieve(self.url_telechargement, self.nom_fichier_dest, _hook)
        return True

    def Dezipper(self, fichier_zip, chemin_dest=""):
        """ D�zippe un fichier ZIP dans un r�pertoire donn� """
        zfile = zipfile.ZipFile(fichier_zip, 'r')
        liste_fichiers = zfile.namelist()
        nbre_fichiers = len(liste_fichiers)

        index = 0
        for i in liste_fichiers:
            pourcentage = GetPourcentage(index, nbre_fichiers)
            keepGoing, skip = self.dlgprogress.Update(pourcentage, _(u"D�compression de Connecthys en cours... %s %%") % pourcentage)
            if os.path.isdir(os.path.join(chemin_dest, i)) or "2.5" in i or "." not in i :
                try: os.makedirs(os.path.join(chemin_dest, i))
                except: pass
            else:
                try: os.makedirs(os.path.join(chemin_dest, os.path.dirname(i)))
                except: pass
                data = zfile.read(i)
                fp = open(os.path.join(chemin_dest, i), "wb")
                fp.write(data)
                fp.close()
            index += 1
        zfile.close()

    def EnvoieRepertoire(self, path="", ftp=None, nbre_total=0, liste_exclusions=[]):
        for name in os.listdir(path):

            # Envoi des fichiers
            if IsException(name) == False :
                localpath = os.path.join(path, name)
                if os.path.isfile(localpath):

                    self.index += 1

                    # Barre de progression
                    pourcentage = GetPourcentage(self.index, nbre_total)
                    try :
                        keepGoing, skip = self.dlgprogress.Update(pourcentage, _(u"Installation : Transfert du fichier %s...") % name)
                    except :
                        keepGoing = True

                    # Stoppe la proc�dure
                    if keepGoing == False :
                        raise Abort(u"Transfert interrompue")

                    ftp.storbinary('STOR ' + name, open(localpath, 'rb'))

                    # Permission sp�ciale
		    # ATTENTION: beaucoup d'hebergements n autorisent pas le chmod/ftp et ftplib ne permet pas de lister les commandes acceptees par le serveur ftp
		    # TODO: boite de dialogue pour indiquer de modifier les droits autrement
                    if name == "portail.cgi" :
                        ftp.sendcmd("chmod 0755 portail.cgi")

                # Envoi des r�pertoires
                elif os.path.isdir(localpath):

                    if name not in liste_exclusions :

                        try:
                            ftp.mkd(name)
                        except Exception, e:
                            # ignore "directory already exists"
                            if not e.args[0].startswith('550'):
                                raise

                        ftp.cwd(name)
                        self.EnvoiRepertoire(localpath, ftp, nbre_total, liste_exclusions)

                        ftp.cwd("..")

    def Upload(self, source_repertoire=""):
        # R�cup�ration du nombre de fichiers � transf�rer
        nbreFichiers = GetNbreFichiers(source_repertoire)

        # Ouverture du FTP
        keepGoing, skip = self.dlgprogress.Update(1, _(u"Connexion FTP en cours..."))
        ftp = ftplib.FTP(self.dict_parametres["ftp_serveur"], self.dict_parametres["ftp_utilisateur"], self.dict_parametres["ftp_mdp"])

        # Cr�ation du r�pertoire s'il n'existe pas
        try:
            ftp.mkd(self.dict_parametres["ftp_repertoire"])
        except Exception, e:
            # ignore "directory already exists"
            if not e.args[0].startswith('550'):
                raise

        ftp.cwd(self.dict_parametres["ftp_repertoire"])

        keepGoing, skip = self.dlgprogress.Update(2, _(u"Connexion FTP effectu�e..."))

        # Recherche le num�ro de version de l'application d�j� install�e
        try :
            url = self.dict_parametres["url_repertoire"] + "/portail.cgi/get_version"
            # R�cup�ration des donn�es au format json
            req = urllib2.Request(url)
            reponse = urllib2.urlopen(req)
            page = reponse.read()
            data = json.loads(page)
            version_ancienne = data["version_str"]
        except Exception, err :
            version_ancienne = None

        # Recherche des exclusions
        if version_ancienne == None :
            liste_exclusions = []
        else :
            # Importation de la liste des exclusions dans le r�pertoire source
            nomFichier = "versions.py"
            chemin = os.path.join(source_repertoire, "application")
            sys.path.append(chemin)
            versions = importlib.import_module(nomFichier.replace(".py", ""))
            liste_exclusions = GetExclusions(liste_versions=versions.VERSIONS, version_ancienne=version_ancienne)

        # Envoi des donn�es
        self.index = 0
        self.EnvoiRepertoire(source_repertoire, ftp, nbre_total=nbreFichiers+5, liste_exclusions=liste_exclusions)

        synchro = UTILS_Portail_synchro.Synchro(self.dict_parametres)

        # Envoi du fichier de config
        keepGoing, skip = self.dlgprogress.Update(98, _(u"Installation du fichier de configuration en cours..."))
        synchro.Upload_config(ftp=ftp)

        # Demande un upgrade de l'application
        keepGoing, skip = self.dlgprogress.Update(99, _(u"Demande la mise � jour de l'application..."))
        synchro.Upgrade_application()

        # Fermeture du FTP
        ftp.quit()

    def CopieRepertoire(self, path="", destpath="", nbre_total=0, liste_exclusions=[]):
        for name in os.listdir(path):

            # Copie des fichiers
            if IsException(name) == False :
                localpath = os.path.join(path, name)
		fulldestpath = os.path.join(destpath, name)
                if os.path.isfile(localpath):

                    self.index += 1

                    # Barre de progression
                    pourcentage = GetPourcentage(self.index, nbre_total)
                    try :
                        keepGoing, skip = self.dlgprogress.Update(pourcentage, _(u"Installation : Copie du fichier %s...") % name)
                    except :
                        keepGoing = True

                    # Stoppe la proc�dure
                    if keepGoing == False :
                        raise Abort(u"Copie interrompue")

		    os.renames(localpath, fulldestpath)

                    # Permission sp�ciale
#                    if name == "portail.cgi" :
#                        ftp.sendcmd("chmod 0755 portail.cgi")

                # Envoi des r�pertoires
                elif os.path.isdir(localpath):

                    if name not in liste_exclusions :

                        try:
			    os.makedirs(fulldestpath)
                        except Exception, e:
                            # ignore "directory already exists"
                            #if not e.args[0].startswith('550'):
                            #    raise
			    print

                        self.CopieRepertoire(localpath, fulldestpath, nbre_total, liste_exclusions)


    def CopieLocale(self, source_repertoire="", dest_repertoire=""):
        # R�cup�ration du nombre de fichiers � transf�rer
        nbreFichiers = GetNbreFichiers(source_repertoire)

        # Demarage de la copie
        keepGoing, skip = self.dlgprogress.Update(1, _(u"Copie en cours..."))

        # Cr�ation du r�pertoire s'il n'existe pas
	localrep = self.dict_parametres["hebergement_local_repertoire"]
        try:
            os.makedirs(localrep)
        except Exception, e:
	    print e
            # ignore "directory already exists"
        #    if not e.args[0].startswith('550'):
        #        raise

        # Recherche le num�ro de version de l'application d�j� install�e
        try :
            url = self.dict_parametres["url_repertoire"] + "/portail.cgi/get_version"
            # R�cup�ration des donn�es au format json
            req = urllib2.Request(url)
            reponse = urllib2.urlopen(req)
            page = reponse.read()
            data = json.loads(page)
            version_ancienne = data["version_str"]
        except Exception, err :
            version_ancienne = None

        # Recherche des exclusions
        if version_ancienne == None :
            liste_exclusions = []
        else :
            # Importation de la liste des exclusions dans le r�pertoire source
            nomFichier = "versions.py"
            chemin = os.path.join(source_repertoire, "application")
            sys.path.append(chemin)
            versions = importlib.import_module(nomFichier.replace(".py", ""))
            liste_exclusions = GetExclusions(liste_versions=versions.VERSIONS, version_ancienne=version_ancienne)

        # Envoi des donn�es
        self.index = 0
        self.CopieRepertoire(source_repertoire, dest_repertoire, nbre_total=nbreFichiers+5, liste_exclusions=liste_exclusions)

        synchro = UTILS_Portail_synchro.Synchro(self.dict_parametres)

        # Envoi du fichier de config
        keepGoing, skip = self.dlgprogress.Update(98, _(u"Copie du fichier de configuration en cours..."))
        #syncro.Copie_config(dest_repertoire)

        # Demande un upgrade de l'application
        keepGoing, skip = self.dlgprogress.Update(99, _(u"Demande la mise � jour de l'application..."))
        synchro.Upgrade_application()


    def Installer(self):
        """ Installation de Connecthys """
        dlg = wx.MessageDialog(None, _(u"Confirmez-vous l'installation du portail internet Connecthys ?\n\nRemarque : Ce processus peut n�cessiter plusieurs dizaines de minutes (selon votre connexion internet)"), _(u"Installation"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return False

        # Init de la dlgprogress
        self.dlgprogress = wx.ProgressDialog(_(u"Veuillez patienter"), _(u"Lancement de l'installation..."), maximum=100, parent=None, style= wx.PD_SMOOTH | wx.PD_ESTIMATED_TIME | wx.PD_REMAINING_TIME | wx.PD_CAN_ABORT | wx.PD_AUTO_HIDE | wx.PD_APP_MODAL)

        try :

            # Recherche la taille du fichier � t�l�charger sur Github
            num_essai = 1
            taille_fichier = 0
            while num_essai < 3 :
                taille_fichier = AffichetailleFichier(self.url_telechargement)
                if taille_fichier > 0 :
                    break
                else :
                    time.sleep(1)

            if taille_fichier == 0 :
                raise Abort(u"Impossible de trouver le source de Connecthys sur internet ! ")

            # T�l�chargement de la source sur Github
            self.Telecharger()

            # D�zippage du fichier
            self.Dezipper(self.nom_fichier_dest, UTILS_Fichiers.GetRepTemp())

	    if self.dict_parametres["hebergement_ftp_activation"] == True :

        	# Envoi des fichiers par FTP
        	source_repertoire = UTILS_Fichiers.GetRepTemp("Connecthys-master/connecthys")
        	self.Upload(source_repertoire)

        	# Fermeture dlgprogress
        	self.dlgprogress.Destroy()

        	return True

	    elif self.dict_parametres["hebergement_local_activation"] == True :

		# deplacement des fichiers dans le repertoire local
		source_repertoire = UTILS_Fichiers.GetRepTemp("Connecthys-master/connecthys")
		dest_repertoire = self.dict_parametres["hebergement_local_repertoire"]
		self.CopieLocale(source_repertoire, dest_repertoire)

		# Fermeture dlgprogress
    		self.dlgprogress.Destroy()

    		return True

	    else :

		# Fermeture dlgprogress
        	self.dlgprogress.Destroy()
		return False

        except Abort as err:
            if self.dlgprogress != None :
                self.dlgprogress.Destroy()
            self.dlgprogress = None

            time.sleep(3)
            dlg = wx.MessageDialog(None, _(u"L'erreur suivante a �t� rencontr�e : %s") % unicode(err), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        except Exception, err :
            if self.dlgprogress != None :
                self.dlgprogress.Destroy()

            traceback.print_exc()
            print "Erreur dans l'installation de l'application : ", err

            time.sleep(3)
            dlg = wx.MessageDialog(None, _(u"L'erreur suivante a �t� rencontr�e : " + str(err)), "Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False




if __name__ == '__main__':
    app = wx.App(0)
    install = Installer()
    install.Installer()
    app.MainLoop()