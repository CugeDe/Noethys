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

import GestionDB
import CTRL_Saisie_euros
import CTRL_Image_mode


LISTE_METHODES_ARRONDI = [
    (u"Arrondi au centime sup�rieur", "centimesup"),
    (u"Arrondi au centime inf�rieur", "centimeinf"),
    ]


class Dialog(wx.Dialog):
    def __init__(self, parent, IDmode=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Saisie_mode_reglement", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDmode = IDmode
        
        # G�n�ralit�s
        self.staticbox_generalites_staticbox = wx.StaticBox(self, -1, u"G�n�ralites")
        self.label_label = wx.StaticText(self, -1, u"Nom :")
        self.ctrl_label = wx.TextCtrl(self, -1, u"")
        self.label_image = wx.StaticText(self, -1, u"Image :")
        self.ctrl_image = CTRL_Image_mode.CTRL(self, table="modes_reglements", key="IDmode", IDkey=self.IDmode, imageDefaut="Images/Special/Image_non_disponible.png", style=wx.BORDER_SUNKEN)
        self.bouton_ajouter_image = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_image = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.label_type_comptable = wx.StaticText(self, -1, u"Type :")
        self.ctrl_type_comptable= wx.Choice(self, -1, choices=[u"Banque", u"Caisse"])
        self.ctrl_type_comptable.SetSelection(0) 
        
        # Options
        self.staticbox_options_staticbox = wx.StaticBox(self, -1, u"Options")
        
        # Numero de pi�ce
        self.label_numero = wx.StaticText(self, -1, u"N� Pi�ce :")
        self.radio_numero_aucun = wx.RadioButton(self, -1, u"Aucun", style=wx.RB_GROUP)
        self.radio_numero_alpha = wx.RadioButton(self, -1, u"Alphanumerique")
        self.radio_numero_numerique = wx.RadioButton(self, -1, u"Num�rique")
        self.ctrl_check_caract = wx.CheckBox(self, -1, u"Nbre caract�res max :")
        self.ctrl_nbre_caract = wx.SpinCtrl(self, -1, u"", min=0, max=100)
        
        # Frais de gestion
        self.label_frais = wx.StaticText(self, -1, u"Frais de\ngestion :")
        self.radio_frais_aucun = wx.RadioButton(self, -1, u"Aucun", style=wx.RB_GROUP)
        self.radio_frais_libre = wx.RadioButton(self, -1, u"Montant libre")
        self.radio_frais_fixe = wx.RadioButton(self, -1, u"Montant fixe :")
        self.ctrl_frais_fixe = CTRL_Saisie_euros.CTRL(self)
        self.radio_frais_prorata = wx.RadioButton(self, -1, u"Montant au prorata :")
        self.ctrl_frais_prorata = wx.TextCtrl(self, -1, u"0.0", style=wx.TE_RIGHT)
        self.label_pourcentage = wx.StaticText(self, -1, u"%")
        listeLabelsArrondis = []
        for labelArrondi, code in LISTE_METHODES_ARRONDI :
            listeLabelsArrondis.append(labelArrondi)
        self.ctrl_frais_arrondi = wx.Choice(self, -1, choices=listeLabelsArrondis)
        self.ctrl_frais_arrondi.SetSelection(0)
        self.label_frais_label = wx.StaticText(self, -1, u"Label de la prestation :")
        self.ctrl_frais_label = wx.TextCtrl(self, -1, u"Frais de gestion")
        
##        # Emetteurs
##        self.staticbox_emetteurs_staticbox = wx.StaticBox(self, -1, u"Emetteurs")
##        self.ctrl_emetteurs = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
##        self.bouton_ajouter_emetteur = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
##        self.bouton_modifier_emetteur = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
##        self.bouton_supprimer_emetteur = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        
        # Commandes
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap(u"Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnAjouterImage, self.bouton_ajouter_image)
        self.Bind(wx.EVT_BUTTON, self.OnSupprimerImage, self.bouton_supprimer_image)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioNumero, self.radio_numero_aucun)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioNumero, self.radio_numero_alpha)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioNumero, self.radio_numero_numerique)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckCaract, self.ctrl_check_caract)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioFrais, self.radio_frais_aucun)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioFrais, self.radio_frais_libre)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioFrais, self.radio_frais_fixe)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioFrais, self.radio_frais_prorata)
##        self.Bind(wx.EVT_BUTTON, self.OnAjouterEmetteur, self.bouton_ajouter_emetteur)
##        self.Bind(wx.EVT_BUTTON, self.OnModifierEmetteur, self.bouton_modifier_emetteur)
##        self.Bind(wx.EVT_BUTTON, self.OnSupprimerEmetteur, self.bouton_supprimer_emetteur)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        # Importation
        if self.IDmode != None :
            self.Importation()
            self.SetTitle(u"Modification d'un mode de r�glement")
        else:
            self.SetTitle(u"Cr�ation d'un mode de r�glement")
            
        # Initialisation des contr�les
        self.OnRadioNumero(None)
        self.OnRadioFrais(None)
        
        
        

    def __set_properties(self):
        self.ctrl_label.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, u""))
        self.ctrl_frais_fixe.SetMinSize((50, -1))
        self.ctrl_nbre_caract.SetMinSize((50, -1))
        self.ctrl_frais_prorata.SetMinSize((50, -1))
        self.ctrl_label.SetToolTipString(u"Saisissez ici le nom du mode de r�glement")
        self.bouton_ajouter_image.SetToolTipString(u"Cliquez ici pour importer une image pour ce mode de r�glement")
        self.bouton_supprimer_image.SetToolTipString(u"Cliquez ici pour supprimer l'image active")
        self.radio_numero_aucun.SetToolTipString(u"Cochez ici si le r�glement de n�cessite aucun num�ro de pi�ce")
        self.radio_numero_alpha.SetToolTipString(u"Cochez ici si le num�ro peut contenir des lettres et des chiffres")
        self.radio_numero_numerique.SetToolTipString(u"Cochez ici si le num�ro ne peut contenir que des chiffres")
        self.ctrl_check_caract.SetToolTipString(u"Cochez cette case si le num�ro a un nombre maximal de chiffres")
        self.ctrl_nbre_caract.SetToolTipString(u"Saisissez ici le nombre de chiffres du num�ro")
        self.radio_frais_aucun.SetToolTipString(u"Cochez ici si aucun frais de gestion n'est applicable pour ce mode de r�glement")
        self.radio_frais_libre.SetToolTipString(u"Cochez ici si des frais de gestion d'un montant variable est applicable")
        self.radio_frais_fixe.SetToolTipString(u"Cochez ici si des frais d'un montant fixe sont applicables")
        self.ctrl_frais_fixe.SetToolTipString(u"Saisissez le montant fixe des frais de gestion")
        self.radio_frais_prorata.SetToolTipString(u"Cochez ici si des frais de gestion d'un montant au prorata est applicable")
        self.ctrl_frais_prorata.SetToolTipString(u"Saisissez ici le pourcentage du montant du r�glement")
        self.ctrl_frais_arrondi.SetToolTipString(u"Selectionnez une m�thode de calcul de l'arrondi")
        self.ctrl_frais_label.SetToolTipString(u"Vous avez ici la possibilit� de modifier le label de la prestation qui sera cr��e pour les frais de gestion")
        self.ctrl_type_comptable.SetToolTipString(u"S�lectionnez le type comptable ('Caisse' pour les esp�ces et 'Banque' pour les autres)")
##        self.bouton_ajouter_emetteur.SetToolTipString(u"Cliquez ici pour ajouter un �metteur")
##        self.bouton_modifier_emetteur.SetToolTipString(u"Cliquez ici pour modifier l'�metteur selectionn� dans la liste")
##        self.bouton_supprimer_emetteur.SetToolTipString(u"Cliquez ici pour supprimer l'�metteur selectionn� dans la liste")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider la saisie")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler la saisie")
        self.SetMinSize((800, -1))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        staticbox_options = wx.StaticBoxSizer(self.staticbox_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_frais = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_frais_label = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_frais_prorata = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_frais_fixe = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_numero = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        grid_sizer_numero_numerique = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        staticbox_generalites = wx.StaticBoxSizer(self.staticbox_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        grid_sizer_image = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons_image = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_generalites.Add(self.label_label, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_generalites.Add(self.ctrl_label, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_image, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_image.Add(self.ctrl_image, 0, 0, 0)
        grid_sizer_boutons_image.Add(self.bouton_ajouter_image, 0, 0, 0)
        grid_sizer_boutons_image.Add(self.bouton_supprimer_image, 0, 0, 0)
        grid_sizer_image.Add(grid_sizer_boutons_image, 1, wx.EXPAND, 0)
        grid_sizer_generalites.Add(grid_sizer_image, 1, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_type_comptable, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 0)
        grid_sizer_generalites.Add(self.ctrl_type_comptable, 0, wx.EXPAND, 0)

        grid_sizer_generalites.AddGrowableCol(1)
        staticbox_generalites.Add(grid_sizer_generalites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_haut.Add(staticbox_generalites, 1, wx.LEFT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_options.Add(self.label_numero, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_numero.Add(self.radio_numero_aucun, 0, 0, 0)
        grid_sizer_numero.Add(self.radio_numero_alpha, 0, 0, 0)
        grid_sizer_numero.Add(self.radio_numero_numerique, 0, 0, 0)
        grid_sizer_numero_numerique.Add((15, 10), 0, wx.EXPAND, 0)
        grid_sizer_numero_numerique.Add(self.ctrl_check_caract, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_numero_numerique.Add(self.ctrl_nbre_caract, 0, 0, 0)
        grid_sizer_numero.Add(grid_sizer_numero_numerique, 1, wx.EXPAND, 0)
        grid_sizer_options.Add(grid_sizer_numero, 1, wx.EXPAND, 0)
        grid_sizer_options.Add(self.label_frais, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_frais.Add(self.radio_frais_aucun, 0, 0, 0)
        grid_sizer_frais.Add(self.radio_frais_libre, 0, 0, 0)
        grid_sizer_frais_fixe.Add(self.radio_frais_fixe, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_frais_fixe.Add(self.ctrl_frais_fixe, 0, 0, 0)
        grid_sizer_frais.Add(grid_sizer_frais_fixe, 1, wx.EXPAND, 0)
        grid_sizer_frais_prorata.Add(self.radio_frais_prorata, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_frais_prorata.Add(self.ctrl_frais_prorata, 0, 0, 0)
        grid_sizer_frais_prorata.Add(self.label_pourcentage, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_frais_prorata.Add(self.ctrl_frais_arrondi, 0, 0, 0)
        grid_sizer_frais.Add(grid_sizer_frais_prorata, 1, wx.EXPAND, 0)
        grid_sizer_frais_label.Add(self.label_frais_label, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_frais_label.Add(self.ctrl_frais_label, 0, wx.EXPAND, 0)
        grid_sizer_frais_label.AddGrowableCol(1)
        grid_sizer_frais.Add(grid_sizer_frais_label, 1, wx.EXPAND, 0)
        grid_sizer_frais.AddGrowableCol(0)
        grid_sizer_options.Add(grid_sizer_frais, 1, wx.EXPAND, 0)
        grid_sizer_options.AddGrowableCol(1)
        staticbox_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_haut.Add(staticbox_options, 1, wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_haut.AddGrowableCol(0)
##        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.EXPAND, 0)
        
        # Emetteurs
##        staticbox_emetteurs = wx.StaticBoxSizer(self.staticbox_emetteurs_staticbox, wx.VERTICAL)
##        grid_sizer_emetteurs = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
##        grid_sizer_boutons_emetteurs = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
##        grid_sizer_emetteurs.Add(self.ctrl_emetteurs, 1, wx.EXPAND, 0)
##        grid_sizer_boutons_emetteurs.Add(self.bouton_ajouter_emetteur, 0, 0, 0)
##        grid_sizer_boutons_emetteurs.Add(self.bouton_modifier_emetteur, 0, 0, 0)
##        grid_sizer_boutons_emetteurs.Add(self.bouton_supprimer_emetteur, 0, 0, 0)
##        grid_sizer_emetteurs.Add(grid_sizer_boutons_emetteurs, 1, wx.EXPAND, 0)
##        grid_sizer_emetteurs.AddGrowableRow(0)
##        grid_sizer_emetteurs.AddGrowableCol(0)
##        staticbox_emetteurs.Add(grid_sizer_emetteurs, 1, wx.ALL|wx.EXPAND, 10)
##        grid_sizer_base.Add(staticbox_emetteurs, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnAjouterImage(self, event): 
        self.ctrl_image.Ajouter(sauvegarder=False)

    def OnSupprimerImage(self, event): 
        self.ctrl_image.Supprimer(sauvegarder=False)

    def OnRadioNumero(self, event): 
        if self.radio_numero_numerique.GetValue() == True :
            etat = True
        else:
            etat = False
        self.OnCheckCaract(None)
        self.ctrl_check_caract.Enable(etat)

    def OnCheckCaract(self, event): 
        if self.ctrl_check_caract.GetValue() == True and self.radio_numero_numerique.GetValue() == True :
            self.ctrl_nbre_caract.Enable(True)
        else:
            self.ctrl_nbre_caract.Enable(False)

    def OnRadioFrais(self, event): 
        if self.radio_frais_aucun.GetValue() == True :
            self.ctrl_frais_fixe.Enable(False)
            self.ctrl_frais_prorata.Enable(False)
            self.label_pourcentage.Enable(False)
            self.ctrl_frais_arrondi.Enable(False)
            self.label_frais_label.Enable(False)
            self.ctrl_frais_label.Enable(False)
        else:
            self.label_frais_label.Enable(True)
            self.ctrl_frais_label.Enable(True)
        
        if self.radio_frais_libre.GetValue() == True :
            self.ctrl_frais_fixe.Enable(False)
            self.ctrl_frais_prorata.Enable(False)
            self.label_pourcentage.Enable(False)
            self.ctrl_frais_arrondi.Enable(False)
        
        if self.radio_frais_fixe.GetValue() == True :
            self.ctrl_frais_fixe.Enable(True)
            self.ctrl_frais_prorata.Enable(False)
            self.label_pourcentage.Enable(False)
            self.ctrl_frais_arrondi.Enable(False)
        
        if self.radio_frais_prorata.GetValue() == True :
            self.ctrl_frais_fixe.Enable(False)
            self.ctrl_frais_prorata.Enable(True)
            self.label_pourcentage.Enable(True)
            self.ctrl_frais_arrondi.Enable(True)
        

    def OnAjouterEmetteur(self, event): 
        print u"Event handler `OnAjouterEmetteur' not implemented!"
        event.Skip()

    def OnModifierEmetteur(self, event): 
        print u"Event handler `OnModifierEmetteur' not implemented!"
        event.Skip()

    def OnSupprimerEmetteur(self, event): 
        print u"Event handler `OnSupprimerEmetteur' not implemented!"
        event.Skip()

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Modesderglements")

    def OnBoutonOk(self, event): 
        # R�cup�ration et v�rification des donn�es saisies
        label = self.ctrl_label.GetValue()
        if label == None :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir un label !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_label.SetFocus()
            return
        
        # Num�ro de pi�ce
        numero_piece = None
        nbre_chiffres = None
        if self.radio_numero_alpha.GetValue() == True :
            numero_piece = "ALPHA"
        if self.radio_numero_numerique.GetValue() == True :
            numero_piece = "NUM"
            if self.ctrl_check_caract.GetValue() == True :
                nbre_chiffres = self.ctrl_nbre_caract.GetValue()
                if nbre_chiffres == 0 :
                    dlg = wx.MessageDialog(self, u"Vous avez s�lectionn� l'option 'Nbre limit� de caract�res' sans saisir de chiffre !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    self.ctrl_nbre_caract.SetFocus()
                    return
        
        # Frais de gestion
        frais_gestion = None
        frais_montant = None 
        frais_pourcentage = None 
        frais_arrondi = None 
        frais_label = None
        if self.radio_frais_libre.GetValue() == True :
            frais_gestion = "LIBRE"
        if self.radio_frais_fixe.GetValue() == True :
            frais_gestion = "FIXE"
            frais_montant = self.ctrl_frais_fixe.GetMontant()
            validation, erreur = self.ctrl_frais_fixe.Validation()
            if frais_montant == 0.0 or validation == False :
                dlg = wx.MessageDialog(self, u"Le montant que vous avez saisi pour les frais de gestion n'est pas valide !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_frais_fixe.SetFocus()
                return
        if self.radio_frais_prorata.GetValue() == True :
            frais_gestion = "PRORATA"
            frais_pourcentage = self.ctrl_frais_prorata.GetValue()
            try :
                frais_pourcentage = float(frais_pourcentage) 
            except :
                dlg = wx.MessageDialog(self, u"Le pourcentage que vous avez saisi pour les frais de gestion n'est pas valide !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_frais_prorata.SetFocus()
                return
            if frais_pourcentage == 0.0 :
                dlg = wx.MessageDialog(self, u"Le pourcentage que vous avez saisi pour les frais de gestion n'est pas valide !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_frais_prorata.SetFocus()
                return
            frais_arrondi = LISTE_METHODES_ARRONDI[self.ctrl_frais_arrondi.GetSelection()][1]
        if frais_gestion != None :
            frais_label = self.ctrl_frais_label.GetValue() 
            if frais_label == "" :
                dlg = wx.MessageDialog(self, u"Le label de prestation que vous avez saisi n'est pas valide !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_frais_label.SetFocus()
                return
        
        if self.ctrl_type_comptable.GetSelection() == 0 :
            type_comptable = "banque"
        else :
            type_comptable = "caisse"
            
        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [    
                ("label", label),
                ("image", None),
                ("numero_piece", numero_piece),
                ("nbre_chiffres", nbre_chiffres),
                ("frais_gestion", frais_gestion),
                ("frais_montant", frais_montant),
                ("frais_pourcentage", frais_pourcentage),
                ("frais_arrondi", frais_arrondi),
                ("frais_label", frais_label),
                ("type_comptable", type_comptable),
            ]
        if self.IDmode == None :
            self.IDmode = DB.ReqInsert("modes_reglements", listeDonnees)
        else:
            DB.ReqMAJ("modes_reglements", listeDonnees, "IDmode", self.IDmode)
        DB.Close()
        
        # Sauvegarde de l'image
        self.ctrl_image.IDkey = self.IDmode
        self.ctrl_image.Sauvegarder() 
        
        # Fermeture de la fen�tre
        self.EndModal(wx.ID_OK)
        
    def Importation(self):
        """ Importation des donn�es """
        DB = GestionDB.DB()
        req = """SELECT label, image, 
        numero_piece, nbre_chiffres, 
        frais_gestion, frais_montant, frais_pourcentage, frais_arrondi, frais_label, type_comptable
        FROM modes_reglements 
        WHERE IDmode=%d;""" % self.IDmode
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        mode = listeDonnees[0]
        label, image, numero_piece, nbre_chiffres, frais_gestion, frais_montant, frais_pourcentage, frais_arrondi, frais_label, type_comptable = mode
        
        # label
        self.ctrl_label.SetLabel(label)
        
        # Image
        
        # Num�ro de pi�ce
        if numero_piece == "ALPHA" :
            self.radio_numero_alpha.SetValue(True)
        if numero_piece == "NUM" :
            self.radio_numero_numerique.SetValue(True)
            if nbre_chiffres != None :
                self.ctrl_check_caract.SetValue(True)
                self.ctrl_nbre_caract.SetValue(nbre_chiffres)
        
        # Frais de gestion
        if frais_gestion == "LIBRE" :
            self.radio_frais_libre.SetValue(True)
        if frais_gestion == "FIXE" :
            self.radio_frais_fixe.SetValue(True)
            if frais_montant != None :
                self.ctrl_frais_fixe.SetMontant(frais_montant)
        if frais_gestion == "PRORATA" :
            self.radio_frais_prorata.SetValue(True)
            if frais_pourcentage != None :
                self.ctrl_frais_prorata.SetValue(str(frais_pourcentage))
            if frais_arrondi != None :
                index = 0
                for labelArrondi, code in LISTE_METHODES_ARRONDI :
                    if frais_arrondi == code :
                        self.ctrl_frais_arrondi.SetSelection(index)
                    index += 1
        if frais_gestion != None and frais_label != None :
            self.ctrl_frais_label.SetValue(frais_label)
        
        # Type comptable
        if type_comptable == "banque" : 
            self.ctrl_type_comptable.SetSelection(0) 
        else : 
            self.ctrl_type_comptable.SetSelection(1) 
        
    def GetIDmode(self):
        return self.IDmode




if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDmode=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
