import datetime

from kivymd.app import MDApp
from kivy.properties import ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout

from kivy.clock import Clock
from kivy.uix.widget import WidgetException
from kivymd.uix.list import ThreeLineIconListItem
from kivymd.uix.list import OneLineIconListItem

from kivymd.uix.list import OneLineListItem
from kivymd.uix.pickers import MDDatePicker

from components.listComponent.List import List
from components.saveComponent.Save import Save

from files.backend import *

class Body(MDBoxLayout):

    screenManager = ObjectProperty(None)
    details = ObjectProperty(None)
    montantPaiement = ObjectProperty(None)
    paiementYear = ObjectProperty(None)
    detailToolbar = ObjectProperty(None)
    year = ObjectProperty(None)
    addYearButton = ObjectProperty(None)
    paie_tab = ObjectProperty(None)
    detteMontant = ObjectProperty(None)
    listDette = ObjectProperty(None)
    totalPaiement = ObjectProperty(None)

    MONTH = [
        "janvier", "fevrier", "mars", "avril",
        "mai", "juin", "juillet", "aout",
        "septembre", "octobre", "novembre", "decembre"
    ]

    def __init__(self, **kwargs):
        super(Body, self).__init__(**kwargs)
        self.backend = DataBase()
        self.employee = None

    def showEmployeesDetails(self, instence, *args) -> None:
        self.id = instence.text.split('|')[0]
        self.screenManager.transition.direction = 'left'
        self.screenManager.current = 'details'
        self.employee = self.backend.getEmployeeById(self.id)
        self.detailToolbar.title = f'{self.employee[0][1]} {self.employee[0][2]} {self.employee[0][3]}'

        #clear the widget with it contains last employee informations...

#==================================Details start here==================================

        self.hide_button()
        self.get_employee_details()
        self.getEmployeesDetteList()

    def updateSomme(self, year: int) -> int:
        self.backend.updateTotal(self.id, year)
        self.backend.updateTotalPaiement(self.id)
        self.backend.updateEpargne(self.id)
        total_paiement = self.getUpdateTotal(self.id, year)
        total_paiement = 0 if total_paiement is None else total_paiement
        self.totalPaiement.text = f"[b]Total des paiements : [color=#ffff00]{total_paiement} F[/color][/b]"

    def updatePaiement(self, year: int, mois: str, salaire: int) -> None:
        # Avoid querying the database if year is not defined
        if year:
            self.backend.updatePaiement(self.id, year, mois, salaire)
        else:
            self.ids[mois].text = ""
            self.totalPaiement.text = ""


    def addNewYear(self) -> None:
        check_year_existence = self.backend.checkAnneeExistence(self.id, self.year.text)
        if (check_year_existence):
            pass
        else:
            self.backend.insertPaiement(self.id, self.year.text)
            self.hide_button()
            paie = self.backend.getYearPaiement(self.id, self.year.text)
            for i in range(len(paie[0]) - 4):
                self.ids[self.MONTH[i]].text = str(paie[0][i + 3])

    def clear_paiement(self) -> None:
        """Clear all paiements input contents"""
        for textInput in self.MONTH:
            self.ids[textInput].text = ""
        self.totalPaiement.text = ""

    def hide_button(self) -> None:
        try:
            self.paie_tab.remove_widget(self.addYearButton)
        except WidgetException:
            pass

    def showButton(self):
        try:
            self.paie_tab.add_widget(self.addYearButton)
        except WidgetException:
            self.paie_tab.remove_widget(self.addYearButton)
            self.paie_tab.add_widget(self.addYearButton)

    def getUpdateTotal(self, id: int, annee: int):
        result = self.backend.getUpdateTotal(id, annee)
        return result

    def show_date_picker(self):
        date_dialog = MDDatePicker(
            min_year=2019,
            max_year=2038
        )
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()
    
    def on_save(self, instance, value, date_range):
        self.year.text = str(value.year)
        paie = self.backend.getYearPaiement(self.id, value.year)
        if (paie==[]):
            self.clear_paiement()
            self.showButton()
        else:
            self.paie_tab.remove_widget(self.addYearButton)
            for i in range(len(paie[0]) - 4):
                self.ids[self.MONTH[i]].text = str(paie[0][i + 3])

    def on_cancel(self, instance, value):
        '''Events called when the "CANCEL" dialog box button is clicked.'''
        pass

#==================================Dette=============================================

    def setDette(self, montant: int):

        if (int(montant) < 1000 or int(montant) >= 1000000):
            self.ids["detteInfos"].text = "[color=#ffff00]Montant n'est pas dans la fourchette...[/color]"
            Clock.schedule_once(self.hideDetteInfos, 3)
        elif (montant.isnumeric()==False):
            self.ids["detteInfos"].text = "[color=#ffff00]Montant invalide...[/color]"
            Clock.schedule_once(self.hideDetteInfos, 3)
        else:
            date = datetime.datetime.now()
            date = date.strftime("%d-%m-%Y")
            self.backend.insertDette(self.id, date, montant)
            self.clearDette()
            self.backend.updateTotalDette(self.id)
            self.backend.updateEpargne(self.id)
            self.getEmployeesDetteList()
            self.ids["detteInfos"].text = "[color=#00ff00]Dette accorder avec succès...[/color]"
            Clock.schedule_once(self.hideDetteInfos, 3)

    def getEmployeesDetteList(self) -> None:
        """MDList for credits on allowed to an employee"""
        # self.listDette.clear_widgets()
        dettes = self.backend.getEmployeesDetteList(self.id)
        for i in range(len(dettes)):
            print(dettes[i])
            # self.listDette.add_widget(
            #     OneLineListItem(text=f"Single-line item {i}")
                # OneLineIconListItem(
                #     text=f'[b]{dettes[i][2]} [color=#ff0]{dettes[i][3]} F CFA[/color][/b]',
                #     bg_color=(0, 0, 0) if i%2==0 else (0, 0, 1)
                # )
            # )

    def getSommeDette(self) -> int:
        """Get somme of credits allowed to employee"""
        result = self.backend.getTotalDette(self.id)
        return result

    def hideDetteInfos(self, instence):
        self.ids["detteInfos"].text = ''

    def clearDette(self):
        self.detteMontant.text = ''

# ================================Update================================

    def get_employee_details(self):

        self.ids["updatePrenom"].text = str(self.employee[0][1])
        self.ids["updateSurnom"].text = str(self.employee[0][2])
        self.ids["updateNom"].text = str(self.employee[0][3])

        self.ids["updateDateEntrer"].text = str(self.employee[0][4])
        self.ids["updateSalaire"].text = str(self.employee[0][6])
        self.ids["updateDateDebut"].text = str(self.employee[0][5])

        self.ids["updatePrenomTuteur"].text = str(self.employee[0][10])
        self.ids["updateNomTutuer"].text = str(self.employee[0][11])
        self.ids["updateTuteurContact"].text = str(self.employee[0][12])
        self.ids["updateAdressTuteur"].text = str(self.employee[0][13])

        self.ids["updateInfos"].text = ""

    def hideUpdateInfos(self, instence):
        self.ids["updateInfos"].text = ""

    def setEnterDate(self, instance, value, date_range):
        self.ids.updateDateEntrer.text = str(value)

    def setStartDate(self, instance, value, date_range):
        self.ids.updateDateDebut.text = str(value)

    def on_cancel(self, instance, value):
        '''Events called when the "CANCEL" dialog box button is clicked.'''

    def shooseEnterDate(self):
        date_dialog = MDDatePicker()  # max_date=datetime.datetime.now(); primary_color=app.theme_cls.primary_color
        date_dialog.bind(on_save=self.setEnterDate, on_cancel=self.on_cancel)
        date_dialog.open()

    def shooseStartDate(self):
        date_dialog = MDDatePicker()  # max_date=datetime.datetime.now(); primary_color=app.theme_cls.primary_color
        date_dialog.bind(on_save=self.setStartDate, on_cancel=self.on_cancel)
        date_dialog.open()

    def set_update(self):

        prenom, surnom, nom = (
            self.ids["updatePrenom"].text,
            self.ids["updateSurnom"].text,
            self.ids["updateNom"].text
        )
        date_in, date_start, salaire = (
            self.ids["updateDateEntrer"].text,
            self.ids["updateDateDebut"].text,
            self.ids["updateSalaire"].text
        )
        t_prenom, t_nom, t_contact, t_adress = (
            self.ids["updatePrenomTuteur"].text,
            self.ids["updateNomTutuer"].text,
            self.ids["updateTuteurContact"].text,
            self.ids["updateAdressTuteur"].text
        )
        self.backend.updateEmployee(
            self.id, prenom, surnom, nom,
            date_in, date_start, salaire,
            t_prenom, t_nom, t_contact, t_adress
        )
        Clock.schedule_once(self.updateSuccess, 0.8)

    def updateSuccess(self, event):
        self.ids["updateInfos"].text = "[color=#ffff00]Mise en jour effectuée...[/color]"
        Clock.schedule_once(self.hideUpdateInfos, 1.9)

class Main(MDApp):
    def build(self):
        self.backend = DataBase()
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Blue'
        self.body = Body()
        return self.body

    def backToHome(self):
        self.body.screenManager.transition.direction = 'right'
        self.body.screenManager.current = 'home'
        self.body.year.text = ""
        for m in self.body.MONTH:
            self.body.ids[m].text = ""
        self.body.totalPaiement.text = ""

    def on_start(self):
        self.save = Save()
        self.employees = List()
        self.root.ids.tabs.add_widget(self.save)
        self.root.ids.tabs.add_widget(self.employees)

    def on_tab_switch(
        self, instance_tabs, instance_tab, instance_tab_label, tab_text
    ):
        if tab_text == 'Employers':
            employees_list = self.backend.getEmployeesByNom('tous')
            instance_tab.ids.listContainer.clear_widgets()
            for i in range(len(employees_list)):
                instance_tab.ids.listContainer.add_widget(
                    ThreeLineIconListItem(
                        text=f'{employees_list[i][0]} | {employees_list[i][1]} {employees_list[i][2]} {employees_list[i][3]}',
                        secondary_text=f'PAIEMENTS : [b][color=#ff0]{employees_list[i][4]} F CFA[/color][/b]',
                        tertiary_text=f'EPARGNE : [b][color=#ff0]{employees_list[i][6]} F CFA[/color][/b]',
                        theme_text_color='Primary',
                        #font_style='H6',
                        secondary_theme_text_color='Primary',
                        tertiary_theme_text_color='Primary',
                        bg_color=(0, 0, 0) if i%2==0 else self.theme_cls.primary_color,
                        on_release=self.body.showEmployeesDetails
                    )
                )

if __name__=='__main__':
    Main().run()