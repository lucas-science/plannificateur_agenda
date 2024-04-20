import json
import os

class LocalStorage:
    def __init__(self, nom_fichier) -> None:
        self.nom_fichier = nom_fichier
        self.data = self._init_data(nom_fichier)

    def _init_data(self, nom_fichier):
        if not os.path.exists(nom_fichier):
            init_data = {
                "score":0,
                "objectifs_utilisateur":[],
                "objectifs_plannifiés":[],
                "taches_fini" : []
            }
            return init_data
        else:
            with open(nom_fichier, 'r') as json_file:
                data = json.load(json_file)
            return data
    
    def _is_state_init(self, state):
        if state in self.data.keys():
            return True
        return False
    
    def save_data(self):
        with open(self.nom_fichier, 'w') as fichier_json:
            print("Data saved")
            json.dump(self.data, fichier_json)

    def get_state(self,state):
        if self._is_state_init(state):
            return self.data[state]
        else:
            return False

    def change_state(self,state, value):
        if self._is_state_init(state):
            self.data[state] = value
            return True
        else:
            return False
    
    def state_append(self, state, value):
        if self._is_state_init(state):
            self.data[state].append(value)
            return True
        else:
            return False



    



