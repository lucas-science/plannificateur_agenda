import requests
import calendar
from icalendar import Calendar

def get_ics_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print("Erreur lors de la récupération du fichier ICS.")
        return None


# Lien vers le fichier ICS
ics_url = "https://ade-outils.insa-lyon.fr/ADE-Cal:~llhomme!2023-2024:a5c217dab6bd6040d9f1cf0f3285b7242f936f18"

# Récupération du contenu du fichier ICS
ics_content = get_ics_content(ics_url)
cal = Calendar.from_ical(ics_content)
