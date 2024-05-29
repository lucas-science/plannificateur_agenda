import sys
import os
import datetime

chemin_actuel = os.path.dirname(os.path.abspath(__file__))
chemin_parent = os.path.abspath(os.path.join(chemin_actuel, '..'))
sys.path.append(chemin_parent)

from model.local_storage import LocalStorage
from model.agenda import Agenda_data


class Controller:
    def __init__(self) -> None:
        """
        Initialise une instance de la classe Controller.
        """
        self.local_storage = LocalStorage("test.json")
        self.agenda_data = None

    def init_agenda_data(self, agenda_URL):
        """
        Initialise les données de l'agenda avec l'URL fournie.
        
        Args:
            agenda_URL (str): L'URL du fichier ICS à charger.
        """
        self.agenda_data = Agenda_data(agenda_URL)
        
    def _delate_tache_from_liste_evenemnts(self, tache, nom_liste_evenements):
        """
        Supprime une tâche d'une liste d'événements spécifique.
        
        Args:
            tache (str): La tâche à supprimer.
            nom_liste_evenements (str): Le nom de la liste d'événements.

        Returns:
            list: La liste mise à jour des événements.
        """
        liste_evenements = self.local_storage.get_state(nom_liste_evenements)
        if tache not in liste_evenements:
            return False
        liste_evenements.remove(tache)
        return liste_evenements

    def increase_streak(self):
        """
        Augmente le score (streak) de l'utilisateur.
        """
        state = "score"
        val = self.local_storage.get_state(state)
        self.local_storage.change_state(state, val + 1)
    
    def decrease_streak(self):
        """
        Diminue le score (streak) de l'utilisateur.
        """
        state = "score"
        val = self.local_storage.get_state(state)
        self.local_storage.change_state(state, val - 1)

    def getScore(self):
        """
        Récupère le score actuel de l'utilisateur.

        Returns:
            int: Le score actuel.
        """
        score = self.local_storage.get_state("score")
        return score
    
    def get_agenda(self):
        """
        Récupère les événements pour les 7 prochains jours depuis l'agenda.

        Returns:
            dict: Les événements des 7 prochains jours.
        """
        # on récupère les evenements INSA pour les 7 prochains jours
        evenements_INSA = self.agenda_data.get_events_for_next_x_day(6)
        # on regarde si il y a des evenements plannifier par l'algo
        return evenements_INSA

    def post_list_objectifs(self, new_objectifs: list):
        """
        Ajoute une liste d'objectifs à la liste existante des objectifs utilisateur.
        
        Args:
            new_objectifs (list): La nouvelle liste d'objectifs.

        Returns:
            bool: True si la mise à jour a réussi, sinon False.
        """
        # On récupère les anciens objectifs
        anciens_objectifs = self.local_storage.get_state("objectifs_utilisateur")

        # On vérifie s'il y a des nouveaux objectifs qui ne sont pas déjà présents dans les anciens objectifs
        for objectif in new_objectifs:
            if objectif not in anciens_objectifs:
                anciens_objectifs.append(objectif)

        # On met à jour la base de données avec les objectifs sans doublons
        res = self.local_storage.change_state("objectifs_utilisateur", anciens_objectifs)
        return res

    def post_tache_fini(self, tache, date: datetime):
        """
        Ajoute une tâche terminée à la liste des tâches terminées.

        Args:
            tache (str): La tâche terminée.
            date (datetime): La date à laquelle la tâche a été terminée.
        """
        # On récupère la liste des tâches terminées depuis le stockage local
        taches_fini = self.local_storage.get_state("taches_fini")

        # On vérifie si la tâche n'est pas déjà dans la liste des tâches terminées
        tache_existante = [t for t in taches_fini if t[0] == tache and t[1] == date.strftime("%d/%m/%Y")]
        if not tache_existante:
            # Si la tâche n'existe pas, on l'ajoute à la liste des tâches terminées
            taches_fini.append([tache, date.strftime("%d/%m/%Y")])

            # On met à jour la base de données avec la nouvelle liste des tâches terminées
            self.local_storage.change_state("taches_fini", taches_fini)
        else:
            print("La tâche existe déjà dans la liste des tâches terminées.")

    def delete_finished_task(self, task, date: datetime):
        """
        Supprime une tâche terminée de la liste des tâches terminées.

        Args:
            task (dict): La tâche à supprimer.
            date (datetime): La date à laquelle la tâche a été terminée.
        """
        # On récupère la liste des tâches terminées depuis le stockage local
        finished_tasks = self.local_storage.get_state("taches_fini")
        task['completed'] = True

        for finished_task in finished_tasks:
            if [task, date.strftime("%d/%m/%Y")] == finished_task:
                self.local_storage.data["taches_fini"].remove(finished_task)
                print('removed')
    
    def get_plannification_automatique(self):
        """
        Planifie automatiquement les objectifs utilisateur en fonction des créneaux libres dans l'agenda.

        Returns:
            tuple: Un tuple contenant un indicateur de succès (1 pour succès, -1 pour échec) et les cours (dict).
        """
        objectifs = self.local_storage.get_state("objectifs_utilisateur")
        cours = self.agenda_data.get_events_for_next_x_day(6)
        if not objectifs:
            return (0, cours)
        else:
            res = self.agenda_data.get_creneaux_supllémentaire(objectifs, cours)
            if res == -1:
                return (-1, cours)
            else:
                return (1, cours)

