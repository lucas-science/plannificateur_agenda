import sys
import os
import datetime 

chemin_actuel = os.path.dirname(os.path.abspath(__file__))
chemin_parent = os.path.abspath(os.path.join(chemin_actuel, '..'))
sys.path.append(chemin_parent)

from model.local_storage import LocalStorage
from model.agenda import Agenda_data


class Controller:
    def __init__(self, agenda_URL) -> None:
        self.local_storage = LocalStorage("test.json")
        self.agenda_data = Agenda_data(agenda_URL)
    
    def _delate_tache_from_liste_evenemnts(self, tache, nom_liste_evenements):
        liste_evenements = self.local_storage.get_state(nom_liste_evenements)
        if tache not in liste_evenements:
            return False
        liste_evenements.remove(tache)
        return  liste_evenements

    def increase_streak(self):
        state = "streak"
        val = self.local_storage.get_state(state)
        self.local_storage.change_state(state, val + 1)
    
    def getScore(self):
        score = self.local_storage.get_state("score")
        return score
    
    def get_agenda(self):
        # on récupère les evenements INSA pour les 7 prochains jours
        evenements_INSA = self.agenda_data.get_events_for_next_x_day(6)
        # on regarde si il y a des evenements plannifier par l'algo
        return evenements_INSA
    
    def post_list_objectifs(self, new_objectifs:list):
        # on ajoute à la base de donnée la liste d'objectifs
        anciens_objectifs = self.local_storage.get_state("objectifs_utilisateur")
        # on ne met pas des doublons d'objectifs
        for objectif in anciens_objectifs:
            if objectif not in new_objectifs:
                new_objectifs.append(objectif)

        # on ajoute dans la base de donnée l'ensemble des objectifs
        res = self.local_storage.change_state("objectifs_utilisateur", new_objectifs)
        return res

    def post_tache_fini(self, tache, date:datetime):
        new_objectifs_utilisateur = self._delate_tache_from_liste_evenemnts(tache, "objectifs_utilisateur")
        new_objectifs_planifies = self._delate_tache_from_liste_evenemnts(tache, "objectifs_plannifiés")
        # on update la base de données
        if new_objectifs_planifies:
            self.local_storage.change_state("objectifs_plannifiés", new_objectifs_planifies)
        if new_objectifs_utilisateur:
            self.local_storage.change_state("objectifs_utilisateur", new_objectifs_utilisateur)

        # on ajoute dans les taches finis
        self.local_storage.state_append("taches_fini", [tache, date.strftime("%d/%m/%Y")])

    def get_plannification_automatique(self):
        objectifs = self.local_storage.get_state("objectifs_utilisateur")
        cours = self.agenda_data.get_events_for_next_x_day(6)
        if objectifs == []:
            return False
        else:
            return self.agenda_data.get_creneaux_supllémentaire(objectifs,cours)
    
c = Controller("https://ade-outils.insa-lyon.fr/ADE-Cal:~llhomme!2023-2024:a5c217dab6bd6040d9f1cf0f3285b7242f936f18")

"""
print(c.local_storage.data)


c.post_list_objectifs([
    {"name":"IE meca", "deadline":"23/04/2024", "temps":6},
    {"name":"IE math", "deadline":"21/04/2024", "temps":6}
])

print(c.get_plannification_automatique())

c.local_storage.save_data()

"""
