from kivy.properties import ObjectProperty
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.tab import MDTabsBase

from files.backend import *

class List(MDFloatLayout, MDTabsBase):
    '''Class implementing content for a tab.'''
    listContainer = ObjectProperty(None)

    def __init__(self, *args):
        super(List, self).__init__(*args)
        self.title = 'Employers'
        self.backend = DataBase()

    def showEmployeesList(self, filtre: str):
        nom = filtre.capitalize()
        employees_list = self.backend.getEmployeesByNom(nom)