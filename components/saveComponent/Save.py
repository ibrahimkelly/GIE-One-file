from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.tab import MDTabsBase

from files.backend import *

class Save(MDFloatLayout, MDTabsBase):

    prenom = ObjectProperty(None)
    surnom = ObjectProperty(None)
    nom = ObjectProperty(None)

    def __init__(self, *args):
        super(Save, self).__init__(*args)
        self.title = 'Enregistrement'
        self.backend = DataBase()

    def check_enreg_error(self):

        if self.prenom.text == '' or self.prenom.text.isalpha() == False or len(self.prenom.text) > 13:
            self.prenom.helper_text = 'Veuillez renseigner un prénom correct...'
            self.prenom.error = True
        else:
            self.prenom.helper_text, self.prenom.error = '', False

        if (len(self.surnom.text) > 13):
            self.surnom.helper_text = 'Veuillez renseigner un surnom correct...'
            self.surnom.error = True
        else:
            self.surnom.helper_text, self.surnom.error = '', False

        if (self.nom.text == '' or self.nom.text.isalpha() == False):
            self.nom.helper_text = 'Veuillez renseigner un nom correct...'
            self.nom.error = True
        else:
            self.nom.helper_text, self.nom.error = '', False

    def saveRecords(self):

        prenomValue = self.prenom.text.capitalize()
        surnomValue = self.surnom.text.capitalize()
        nomValue = self.nom.text.capitalize()

        # By default textFields error mode is set to False, so this methode is called to check their contents
        self.check_enreg_error()

        if (self.prenom.error == False and self.surnom.error == False and self.nom.error == False):
            if (self.backend.checEmployeeExistence(prenomValue, surnomValue, nomValue) == True):
                self.ids["enreg_infos"].text = "[color=#ffff00]Ce nom existe déjà dans la base de donnée...[/color]"
                Clock.schedule_once(self.hideInfo, 3)
            else:
                self.backend.saveEmployee(prenomValue, surnomValue, nomValue)
                self.clearEnregInput()
                self.ids["enreg_infos"].text = "[color=#00ff00]Enregistrement réussi...[/color]"
                Clock.schedule_once(self.hideInfo, 3)
        else:
            self.ids[
                "enreg_infos"].text = "[color=#ffff00]Veuillez renseigner correctement les informations...[/color]"
            Clock.schedule_once(self.hideInfo, 3)

    def cancelEnregistrement(self):
        self.clearEnregInput()
        self.ids['enreg_infos'].text = "[color=#ffff00]Enregistrement annulé[/color]"
        Clock.schedule_once(self.hideInfo, 3)

    def clearEnregInput(self):
        self.prenom.text, self.prenom.error = '', False
        self.surnom.text, self.surnom.error = '', False
        self.nom.text, self.nom.error = '', False

    def hideInfo(self, event):
        self.ids["enreg_infos"].text = ""
