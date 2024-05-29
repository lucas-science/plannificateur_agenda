import json
import os

class LocalStorage:
    def __init__(self, nom_fichier) -> None:
        """
        Initialise une instance de la classe LocalStorage.
        Args:
            nom_fichier (str): Le nom du fichier JSON utilisé pour le stockage des données.
        """
        self.nom_fichier = nom_fichier
        self.data = self._init_data(nom_fichier)

    def _init_data(self, nom_fichier):
        """
        Initialise les données en chargeant à partir d'un fichier JSON ou en créant un modèle de données par défaut.
        Args:
            nom_fichier (str): Le nom du fichier JSON utilisé pour le stockage des données.

        Returns:
            dict: Les données initialisées.
        """
        if not os.path.exists(nom_fichier):
            init_data = {
                'url': "",
                "score": 0,
                "objectifs_utilisateur": [],
                "objectifs_plannifiés": [],
                "taches_fini": []
            }
            return init_data
        else:
            with open(nom_fichier, 'r') as json_file:
                data = json.load(json_file)
            return data

    def _is_state_init(self, state):
        """
        Vérifie si un état est initialisé dans les données.
        Args:
            state (str): Le nom de l'état à vérifier.

        Returns:
            bool: True si l'état est initialisé, sinon False.
        """
        return state in self.data

    def save_data(self):
        """
        Sauvegarde les données actuelles dans le fichier JSON.
        """
        with open(self.nom_fichier, 'w') as fichier_json:
            json.dump(self.data, fichier_json)
        print("Data saved")

    def get_state(self, state):
        """
        Récupère la valeur d'une clef spécifique dans le fichier json.
        Args:
            state (str): Le nom de l'état à récupérer.

        Returns:
            any: La valeur de l'état si initialisé, sinon False.
        """
        return self.data.get(state, False)

    def change_state(self, state, value):
        """
        Modifie la valeur d'une clef spécifique.
        Args:
            state (str): Le nom de l'état à modifier.
            value (any): La nouvelle valeur de l'état.

        Returns:
            bool: True si l'état a été modifié avec succès, sinon False.
        """
        if self._is_state_init(state):
            self.data[state] = value
            return True
        else:
            return False

    def state_append(self, state, value):
        """
        Ajoute une valeur à une liste d'une clef spécifique spécifique.
        Args:
            state (str): Le nom de l'état à modifier.
            value (any): La valeur à ajouter à la liste.

        Returns:
            bool: True si la valeur a été ajoutée avec succès, sinon False.
        """
        if self._is_state_init(state) and isinstance(self.data[state], list):
            self.data[state].append(value)
            return True
        else:
            return False

    def remove_state(self, state):
        """
        Supprime une clef spécifique des données.
        Args:
            state (str): Le nom de l'état à supprimer.

        Returns:
            bool: True si l'état a été supprimé avec succès, sinon False.
        """
        if self._is_state_init(state):
            del self.data[state]
            return True
        else:
            return False
