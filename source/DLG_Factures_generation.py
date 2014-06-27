#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import datetime
import GestionDB
import CTRL_Bandeau

from DLG_Factures_generation_parametres import Panel as Page1
from DLG_Factures_generation_selection import Panel as Page2
from DLG_Factures_generation_actions import Panel as Page3


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Facturation", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        intro = u"Vous pouvez ici g�n�rer des factures. Page 1 : S�lectionnez des param�tres puis cliquez sur Suite pour afficher les factures disponibles. Page 2 : Cochez les factures � g�n�rer puis cliquez sur Suite. Page 3 : Vous pouvez effectuer d'autres actions sur les factures g�n�r�es."
        titre = u"G�n�ration de factures"
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Generation.png")
        
        self.listePages = ("Page1", "Page2", "Page3")
        
        self.static_line = wx.StaticLine(self, -1)
        
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_retour = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Retour_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_suite = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Suite_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap("Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))
        
        self.__set_properties()
        self.__do_layout()
                
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_retour, self.bouton_retour)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_suite, self.bouton_suite)
        
        self.bouton_retour.Enable(False)
        self.nbrePages = len(self.listePages)    
        self.pageVisible = 1
                        
        # Cr�ation des pages
        self.Creation_Pages()        
        
            
    def Creation_Pages(self):
        """ Creation des pages """
        for numPage in range(1, self.nbrePages+1) :
            exec( "self.page" + str(numPage) + " = " + self.listePages[numPage-1] + "(self)" )
            exec( "self.sizer_pages.Add(self.page" + str(numPage) + ", 1, wx.EXPAND, 0)" )
            self.sizer_pages.Layout()
            exec( "self.page" + str(numPage) + ".Show(False)" )
        self.page1.Show(True)
        self.sizer_pages.Layout()

    def __set_properties(self):
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_retour.SetToolTipString(u"Cliquez ici pour revenir � la page pr�c�dente")
        self.bouton_suite.SetToolTipString(u"Cliquez ici pour passer � l'�tape suivante")
        self.bouton_annuler.SetToolTipString(u"Cliquez pour annuler")
        self.SetMinSize((730, 670))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=0, hgap=0)
        # Bandeau
        grid_sizer_base.Add(self.ctrl_bandeau, 1, wx.EXPAND, 0)
        
        # Contenu
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_pages = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base.Add(sizer_pages, 1, wx.EXPAND|wx.ALL, 10)
        grid_sizer_base.Add(self.static_line, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_retour, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_suite, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, wx.LEFT, 10)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen()
        
        self.sizer_pages = sizer_pages
    
    def Onbouton_aide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("Gnration")

    def Onbouton_retour(self, event):
        # rend invisible la page affich�e
        pageCible = eval("self.page"+str(self.pageVisible))
        pageCible.Show(False)
        # Fait appara�tre nouvelle page
        self.pageVisible -= 1
        pageCible = eval("self.page"+str(self.pageVisible))
        pageCible.Show(True)
        self.sizer_pages.Layout()
        # Si on quitte l'avant-derni�re page, on active le bouton Suivant
        if self.pageVisible == self.nbrePages :
            self.bouton_suite.Enable(True)
            self.bouton_suite.SetBitmapLabel(wx.Bitmap("Images/BoutonsImages/Fermer_L72.png", wx.BITMAP_TYPE_ANY))
        else:
            self.bouton_suite.Enable(True)
            self.bouton_suite.SetBitmapLabel(wx.Bitmap("Images/BoutonsImages/Suite_L72.png", wx.BITMAP_TYPE_ANY))
        # Si on revient � la premi�re page, on d�sactive le bouton Retour
        if self.pageVisible == 1 :
            self.bouton_retour.Enable(False)
        # On active le bouton annuler
        self.bouton_annuler.Enable(True)

    def Onbouton_suite(self, event):
        # V�rifie que les donn�es de la page en cours sont valides
        validation = self.ValidationPages()
        if validation == False : return
        # Si on est d�j� sur la derni�re page : on termine
        if self.pageVisible == self.nbrePages :
            self.Terminer()
            return
        # Rend invisible la page affich�e
        pageCible = eval("self.page"+str(self.pageVisible))
        pageCible.Show(False)
        # Fait appara�tre nouvelle page
        self.pageVisible += 1
        pageCible = eval("self.page"+str(self.pageVisible))
        pageCible.MAJ() 
        pageCible.Show(True)
        self.sizer_pages.Layout()
        # Si on arrive � la derni�re page, on d�sactive le bouton Suivant
        if self.pageVisible == self.nbrePages :
            self.bouton_suite.SetBitmapLabel(wx.Bitmap("Images/BoutonsImages/Fermer_L72.png", wx.BITMAP_TYPE_ANY))
            self.bouton_annuler.Enable(False)
        # Si on quitte la premi�re page, on active le bouton Retour
        if self.pageVisible > 1 :
            self.bouton_retour.Enable(True)
        
        # D�sactivation du bouton Retour si derni�re page > SPECIAL FACTURATION !!!
        if self.pageVisible == self.nbrePages :            
            self.bouton_retour.Enable(False)

    def ValidationPages(self) :
        """ Validation des donn�es avant changement de pages """
        exec( "validation = self.page" + str(self.pageVisible) + ".Validation()" )
        return validation
    
    def Terminer(self):
        # Fermeture
        self.EndModal(wx.ID_OK)
        
    def SetFamille(self, IDfamille=None):
        self.page1.SetFamille(IDfamille)
        
        
        
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    IDactivite = 1
    frame_1 = Dialog(None) 
    # TESTS
    frame_1.page1.ctrl_date_debut.SetDate(datetime.date(2011, 1, 1))
    frame_1.page1.ctrl_date_fin.SetDate(datetime.date(2011, 12, 31))
    
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
