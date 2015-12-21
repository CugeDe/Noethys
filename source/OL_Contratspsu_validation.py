#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import GestionDB
import UTILS_Dates
import datetime
import calendar
from UTILS_Decimal import FloatToDecimal as FloatToDecimal
import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"�")

from ObjectListView import ObjectListView, FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter
from ObjectListView import EVT_CELL_EDIT_STARTING, EVT_CELL_EDIT_FINISHING, CellEditorRegistry

from DLG_Saisie_contratpsu import Base

LISTE_MOIS = [_(u"Janvier"), _(u"F�vrier"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Ao�t"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"D�cembre")]



class CTRL_Duree(wx.SpinCtrl):
    def __init__(self, parent):
        wx.SpinCtrl.__init__(self, parent, -1, "", min=-99999, max=99999, style=wx.TE_PROCESS_ENTER)

    def SetValue(self, valeur=datetime.timedelta(seconds=0)):
        heures = (valeur.days*24) + (valeur.seconds/3600)
        super(CTRL_Duree, self).SetValue(heures)

    def GetValue(self):
        heures = super(CTRL_Duree, self).GetValue()
        if heures == -99999 : heures = 0
        return datetime.timedelta(hours=heures)


class Track(object):
    def __init__(self, mois=1, annee=2015, clsbase=None, track_mensualite=None):
        self.mois = mois
        self.annee = annee
        self.clsbase = clsbase
        self.track_mensualite = track_mensualite

        # G�n�ralit�s
        self.individu_nom_complet = self.clsbase.GetValeur("individu_nom_complet", "")

        # Mensualit�
        self.label_prestation = self.track_mensualite.label_prestation
        self.heures_prevues = self.track_mensualite.heures_prevues
        self.montant_prevu = self.track_mensualite.montant_prevu
        self.IDprestation = self.track_mensualite.IDprestation
        self.date_facturation = self.track_mensualite.date_facturation
        self.forfait_date_debut = self.track_mensualite.forfait_date_debut
        self.forfait_date_fin = self.track_mensualite.forfait_date_fin
        self.taux = self.track_mensualite.taux
        self.tarif_base = self.track_mensualite.tarif_base
        self.tarif_depassement = self.track_mensualite.tarif_depassement

        # Prestation existante
        self.IDfacture = self.track_mensualite.IDfacture
        self.num_facture = self.track_mensualite.num_facture
        self.heures_facturees = self.track_mensualite.heures_facturees
        self.montant_facture = self.track_mensualite.montant_facture

        # Consommations
        self.heures_prevues_mois = datetime.timedelta(seconds=0)
        self.heures_presences = datetime.timedelta(seconds=0)
        self.heures_absences_deductibles = datetime.timedelta(seconds=0)
        self.heures_absences_non_deductibles = datetime.timedelta(seconds=0)
        self.heures_depassements = datetime.timedelta(seconds=0)
        self.heures_regularisation = datetime.timedelta(seconds=0)

        for dictConso in self.clsbase.GetValeur("liste_conso", []) :

            if dictConso["date"].month == self.mois and dictConso["date"].year == self.annee :

                heure_debut_time = UTILS_Dates.HeureStrEnTime(dictConso["heure_debut"])
                heure_fin_time = UTILS_Dates.HeureStrEnTime(dictConso["heure_fin"])
                duree = UTILS_Dates.SoustractionHeures(heure_fin_time, heure_debut_time)

                # Recherche des pr�visions
                if dictConso["IDunite"] == self.clsbase.GetValeur("IDunite_prevision") :
                    self.heures_prevues_mois += duree

                # Recherche des pr�sences et des absences
                if dictConso["IDunite"] == self.clsbase.GetValeur("IDunite_presence") :

                    if dictConso["etat"] in ("reservation", "present") :
                        self.heures_presences += duree

                    if dictConso["etat"] in ("absenti",) :
                        self.heures_absences_non_deductibles += duree

                    if dictConso["etat"] in ("absentj",) :
                        self.heures_absences_deductibles += duree

                # Recherche des d�passements
                if dictConso["IDunite"] == self.clsbase.GetValeur("IDunite_depassement") :
                    self.heures_depassements += duree

        self.MAJ()

    def MAJ(self):
        # Calcul des heures � facturer
        self.heures_a_facturer = self.heures_prevues - self.heures_absences_deductibles + self.heures_regularisation
        self.heures_a_facturer_entier = (self.heures_a_facturer.days*24) + (self.heures_a_facturer.seconds/3600)
        self.montant_a_facturer = FloatToDecimal(self.tarif_base * self.heures_a_facturer_entier)

        # Calcul des d�passements
        self.heures_depassements_entier = (self.heures_depassements.days*24) + (self.heures_depassements.seconds/3600)
        self.montant_depassements = FloatToDecimal(self.tarif_depassement * self.heures_depassements_entier)
        self.montant_a_facturer += self.montant_depassements

        self.heures_a_facturer += self.heures_depassements

# ----------------------------------------------------------------------------------------------------------------------------------------

class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # R�cup�ration des param�tres perso
        self.mois = None
        self.annee = None
        self.IDactivite = None
        self.nomActivite = ""

        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(EVT_CELL_EDIT_FINISHING, self.handleCellEditFinishing)
        self.donnees = []
        self.InitObjectListView()

        def TimedeltaEditor(olv, rowIndex, subItemIndex):
            ctrl = CTRL_Duree(self)
            return ctrl

        # Register the "editor factory" for wx.Colour objects
        CellEditorRegistry().RegisterCreatorFunction(datetime.timedelta, TimedeltaEditor)

    def handleCellEditFinishing(self, event):
        index = event.rowIndex
        wx.CallAfter(self.MAJtracks)

    def MAJtracks(self):
        for track in self.donnees :
            track.MAJ()
        self.RefreshObjects()

    def InitObjectListView(self):
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        # Pr�paration de la listeImages
        imageValide = self.AddNamedImages("valide", wx.Bitmap("Images/16x16/Ok4.png", wx.BITMAP_TYPE_PNG))

        def GetImage(track):
            if track.IDprestation != None :
                return "valide"
            else:
                return None

        def FormateDate(dateDD):
            if dateDD == None :
                return ""
            else:
                return UTILS_Dates.DateDDEnFr(dateDD)

        def FormateMontant(montant):
            if montant in ("", None, FloatToDecimal(0.0)) :
                return ""
            return u"%.2f %s" % (montant, SYMBOLE)

        def FormateMontant2(montant):
            if montant == None or montant == "" : return ""
            return u"%.5f %s" % (montant, SYMBOLE)

        def FormateDuree(duree):
            if duree in (None, "", datetime.timedelta(seconds=0)):
                return ""
            else :
                return UTILS_Dates.DeltaEnStr(duree, separateur="h")

        liste_Colonnes = [
            # ColumnDefn(_(u""), "left", 0, "IDprestation", typeDonnee="entier", isEditable=False),
            ColumnDefn(_(u""), "left", 18, "", typeDonnee="texte", imageGetter=GetImage, isEditable=False),
            ColumnDefn(_(u"Individu"), 'left', 130, "individu_nom_complet", typeDonnee="texte", isEditable=False),
            # ColumnDefn(_(u"Mois"), 'left', 100, "label_prestation", typeDonnee="texte", isEditable=False),
            ColumnDefn(_(u"H. forfait."), 'center', 80, "heures_prevues", typeDonnee="duree", stringConverter=FormateDuree, isEditable=False),
            ColumnDefn(_(u"Mt. forfait"), 'center', 80, "montant_prevu", typeDonnee="montant", stringConverter=FormateMontant, isEditable=False),

            ColumnDefn(_(u"H. pr�vues"), 'center', 80, "heures_prevues_mois", typeDonnee="duree", stringConverter=FormateDuree, isEditable=False),
            ColumnDefn(_(u"Pr�sences"), 'center', 80, "heures_presences", typeDonnee="duree", stringConverter=FormateDuree, isEditable=False),
            ColumnDefn(_(u"Abs d�duc."), 'center', 80, "heures_absences_deductibles", typeDonnee="duree", stringConverter=FormateDuree, isEditable=False),
            ColumnDefn(_(u"Abs non d�duc."), 'center', 95, "heures_absences_non_deductibles", typeDonnee="duree", stringConverter=FormateDuree, isEditable=False),
            ColumnDefn(_(u"H. compl."), 'center', 80, "heures_depassements", typeDonnee="duree", stringConverter=FormateDuree, isEditable=False),
            ColumnDefn(_(u"H. r�gular."), 'center', 80, "heures_regularisation", typeDonnee="duree", stringConverter=FormateDuree, isEditable=True),

            ColumnDefn(_(u"H. factur�es"), 'center', 80, "heures_a_facturer", typeDonnee="duree", stringConverter=FormateDuree, isEditable=False),
            ColumnDefn(_(u"MONTANT"), 'center', 80, "montant_a_facturer", typeDonnee="montant", stringConverter=FormateMontant, isEditable=False),
            ColumnDefn(_(u"Date"), 'center', 80, "date_facturation", typeDonnee="date", stringConverter=FormateDate, isEditable=False),

            ColumnDefn(_(u"H. fact."), 'center', 80, "heures_facturees", typeDonnee="duree", stringConverter=FormateDuree, isEditable=False),
            ColumnDefn(_(u"Montant fact."), 'center', 90, "montant_facture", typeDonnee="montant", stringConverter=FormateMontant, isEditable=False),
            ColumnDefn(_(u"N� Facture"), 'center', 70, "num_facture", typeDonnee="entier", isEditable=False),

            # ColumnDefn(_(u"Taux"), 'center', 80, "taux", typeDonnee="montant", stringConverter=FormateMontant2, isEditable=False),
            # ColumnDefn(_(u"Tarif de base"), 'center', 80, "tarif_base", typeDonnee="montant", stringConverter=FormateMontant2, isEditable=False),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)
        self.SetEmptyListMsg(_(u"Aucune mensualit�"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(2)

        self.cellEditMode = ObjectListView.CELLEDIT_SINGLECLICK # ObjectListView.CELLEDIT_DOUBLECLICK

    def SetParametres(self, mois=1, annee=2015, IDactivite=None, nomActivite=""):
        self.mois = mois
        self.annee = annee
        self.IDactivite = IDactivite
        self.nomActivite = nomActivite

        # Recherche des dates extr�mes du mois
        dernierJourMois = calendar.monthrange(annee, mois)[1]
        date_debut = datetime.date(annee, mois, 1)
        date_fin = datetime.date(annee, mois, dernierJourMois)

        if IDactivite == None :
            IDactivite = 0

        # Recherche des contrats
        DB = GestionDB.DB()
        req = """SELECT IDcontrat, IDindividu
        FROM contrats
        WHERE type='psu' AND date_debut<='%s' AND date_fin>='%s' AND IDactivite=%d
        ;""" % (date_fin, date_debut, IDactivite)
        DB.ExecuterReq(req)
        listeContrats = DB.ResultatReq()

        listeIDcontrats = []
        for IDcontrat, IDindividu in listeContrats :
            listeIDcontrats.append(IDcontrat)

        # Recherche des donn�es de chaque contrat
        self.donnees = []
        for IDcontrat in listeIDcontrats :
            clsbase = Base(IDcontrat=IDcontrat, DB=DB)
            clsbase.Calculer()

            # Recherche d'une mensualit� valide
            track_mensualite = None
            liste_mensualites = clsbase.GetValeur("tracks_mensualites", [])
            for track in liste_mensualites :
                if track.mois == mois and track.annee == annee :
                    track_mensualite = track
                    break

            # Cr�ation du track
            track = Track(mois, annee, clsbase, track_mensualite)
            track.MAJ()
            self.donnees.append(track)

        DB.Close()

        # MAJ du listview
        self.MAJ()
        self.CocheListeTout()

    def MAJ(self):
        self.SetObjects(self.donnees)
        self._ResizeSpaceFillingColumns() 

    def GetTracks(self):
        return self.GetObjects()

    def SetTracks(self, tracks=[]):
        self.donnees = tracks
        self.MAJ()

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """        
        # Cr�ation du menu contextuel
        menuPop = wx.Menu()

        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
                
        # Cr�ation du menu contextuel
        menuPop = wx.Menu()

        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aper�u avant impression"))
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        menuPop.AppendSeparator()
    
        # Item Export Texte
        item = wx.MenuItem(menuPop, 600, _(u"Exporter au format Texte"))
        bmp = wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 700, _(u"Exporter au format Excel"))
        bmp = wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()
            
    def Apercu(self, event):
        if self.IDactivite == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez commencer par s�lectionner une activit� !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des mensualit�s"), intro=self.GetIntro(), format="A", orientation=wx.LANDSCAPE)
        prt.Preview()

    def Imprimer(self, event):
        if self.IDactivite == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez commencer par s�lectionner une activit� !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des mensualit�s"), intro=self.GetIntro(), format="A", orientation=wx.LANDSCAPE)
        prt.Print()

    def ExportTexte(self, event):
        if self.IDactivite == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez commencer par s�lectionner une activit� !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des mensualit�s"), autoriseSelections=False)
        
    def ExportExcel(self, event):
        if self.IDactivite == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez commencer par s�lectionner une activit� !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des mensualit�s"), autoriseSelections=False)

    def GetIntro(self):
        return u"Mensualit�s de %s %d de l'activit� %s" % (LISTE_MOIS[self.mois-1], self.annee, self.nomActivite)

    def Valider(self):
        """ Valider les mensualit�s """
        listeTracks = self.GetCheckedObjects()

        # V�rifications
        if len(listeTracks) == 0 :
           dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucune mensualit� � g�n�rer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
           dlg.ShowModal()
           dlg.Destroy()
           return False

        for track in listeTracks :
            if track.IDprestation != None :
                dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas s�lectionner des lignes dont les mensualit�s ont d�j� �t� g�n�r�es !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        # Demande de confirmation
        dlg = wx.MessageDialog(self, _(u"Confirmez-vous la validation des %d mensualit�s s�lectionn�es sur le mois de %s %d ?" % (len(listeTracks), LISTE_MOIS[self.mois-1], self.annee)), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return False

        # Enregistrement des mensualit�s
        DB = GestionDB.DB()

        for track in listeTracks :
            listeDonnees = (
                ("IDcompte_payeur", track.clsbase.GetValeur("IDcompte_payeur", None)),
                ("date", track.date_facturation),
                ("categorie", "consommation"),
                ("label", track.label_prestation),
                ("montant_initial", track.montant_a_facturer),
                ("montant", track.montant_a_facturer),
                ("IDactivite", track.clsbase.GetValeur("IDactivite", None)),
                ("IDtarif", track.clsbase.GetValeur("IDtarif", None)),
                ("IDfacture", track.IDfacture),
                ("IDfamille", track.clsbase.GetValeur("IDfamille", None)),
                ("IDindividu", track.clsbase.GetValeur("IDindividu", None)),
                ("forfait", None),
                ("temps_facture", UTILS_Dates.DeltaEnStr(track.heures_a_facturer, ":")),
                ("IDcategorie_tarif", track.clsbase.GetValeur("IDcategorie_tarif", None)),
                ("forfait_date_debut", track.forfait_date_debut),
                ("forfait_date_fin", track.forfait_date_fin),
                ("IDcontrat", track.clsbase.IDcontrat),
            )
            if track.IDprestation == None :
                IDprestation = DB.ReqInsert("prestations", listeDonnees)
            else :
                IDprestation = track.IDprestation
                DB.ReqMAJ("prestations", listeDonnees, "IDprestation", IDprestation)

            # MAJ du track
            track.IDprestation = IDprestation
            track.heures_facturees = track.heures_a_facturer
            track.montant_facture = track.montant_a_facturer
            self.RefreshObject(track)

        DB.Commit()
        DB.Close()

        # Confirmation succ�s
        dlg = wx.MessageDialog(self, _(u"Les mensualit�s ont �t� g�n�r�es avec succ�s !"), _(u"G�n�ration termin�e"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return True




# -------------------------------------------------------------------------------------------------------------------------------------------

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "individu_nom_complet" : {"mode" : "nombre", "singulier" : _(u"individu"), "pluriel" : _(u"individus"), "alignement" : wx.ALIGN_CENTER},
            "heures_prevues" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER, "format" : "temps"},
            "montant_prevu" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER},

            "heures_prevues_mois" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER, "format" : "temps"},
            "heures_presences" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER, "format" : "temps"},
            "heures_absences_deductibles" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER, "format" : "temps"},
            "heures_absences_non_deductibles" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER, "format" : "temps"},
            "heures_depassements" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER, "format" : "temps"},
            "heures_regularisation" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER, "format" : "temps"},

            "heures_a_facturer" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER, "format" : "temps"},
            "montant_a_facturer" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER},

            "heures_facturees" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER, "format" : "temps"},
            "montant_facture" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER},
            }
        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        ctrl = ListviewAvecFooter(panel, kwargs={})
        listview = ctrl.GetListview()
        listview.MAJ()

        listview.SetParametres(mois=12, annee=2015, IDactivite=43)
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(ctrl, 1, wx.ALL|wx.EXPAND, 10)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.SetSize((1200, 400))

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
