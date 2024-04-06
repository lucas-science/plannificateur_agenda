import sys
import os

# Ajouter le chemin du répertoire parent au chemin de recherche des modules
chemin_actuel = os.path.dirname(os.path.abspath(__file__))
chemin_parent = os.path.abspath(os.path.join(chemin_actuel, '..'))
sys.path.append(chemin_parent)

# Maintenant, vous pouvez importer la classe LocalStorage
from model.local_storage import LocalStorage


class Controller:
    def __init__(self) -> None:
        self.local_storage = LocalStorage("test.json")
    
    def increase_streak(self):
        state = "streak"
        val = self.local_storage.get_state(state)
        self.local_storage.change_state(state, val + 1)

c = Controller()
