import requests
import calendar
from icalendar import Calendar
from datetime import datetime, timedelta



class Agenda_data:
    def __init__(self, url) -> None:
        self.ics_content = self._get_ics_content(url)
        self.cal = Calendar.from_ical(self.ics_content)
    
    def _get_ics_content(self,url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print("Erreur lors de la récupération du fichier ICS.")
            return None

    def _get_events_for_date_searched(self,date_searched):
        events_for_date = []
        events_final_for_date = []
        calendar = self.cal
        for event in calendar.walk('VEVENT'):
            event_date = event.get('DTSTART').dt.date()
            if event_date == date_searched:
                events_for_date.append(event)
        
        for ev in events_for_date:
            summary = str(ev.get('SUMMARY'))
            start_time = ev.get('DTSTART').dt.strftime('%H:%M')
            end_time = ev.get('DTEND').dt.strftime('%H:%M')

            event = {"summary":summary, "start_time":start_time, "end_time":end_time}
            events_final_for_date.append(event)

        return events_final_for_date
    
    def _difference(self, heure1, heure2):
        heure1_heures, heure1_minutes = map(int, heure1.split(':'))
        heure2_heures, heure2_minutes = map(int, heure2.split(':'))
        
        if heure1_heures > heure2_heures:
            return -1
        
        total_minutes_heure1 = heure1_heures * 60 + heure1_minutes
        total_minutes_heure2 = heure2_heures * 60 + heure2_minutes
        
        difference_minutes = total_minutes_heure2 - total_minutes_heure1
        
        return difference_minutes


    def _calculer_heure_fin(self, heure_debut, duree_minutes):
        heures_debut, minutes_debut = map(int, heure_debut.split(':'))
        
        total_minutes_debut = heures_debut * 60 + minutes_debut
        total_minutes_fin = total_minutes_debut + duree_minutes

        heures_fin = total_minutes_fin // 60
        minutes_fin = total_minutes_fin % 60

        heure_fin = '{:02d}:{:02d}'.format(heures_fin, minutes_fin)
        
        return heure_fin

    def _comparer_temps_debut(self, event):
        return event['start_time']


    def _init_slot(self,start,stop):
        slot_time = self._difference(start, stop)
        res = {'start':start, 'end':stop, 'time':slot_time}
        return res



    def _get_creneaux_libre_by_day(self, events, delta_minute):
        events.append({'summary': 'pause repas', 'start_time': '12:00', 'end_time': '14:00'})
        events_triees = sorted(events, key=self._comparer_temps_debut, reverse=False)
        begin = '8:00'
        end = '21:00'
        free_slots = []
        
        if events != []:
            premier_event = events_triees[0]
            dernier_event = events_triees[-1]

            if self._difference(begin, premier_event['start_time']) >= delta_minute:
                free_slots.append(self._init_slot(begin, premier_event['start_time']))

            for index in range(len(events) - 1):
                fin1 = events_triees[index]['end_time']
                debut2 = events_triees[index + 1]['start_time'] 
                if self._difference(fin1, debut2) >= delta_minute:
                    free_slots.append(self._init_slot(fin1, debut2))
            
            
            if self._difference(dernier_event['end_time'], end) >= delta_minute:
                free_slots.append(self._init_slot(dernier_event['end_time'], end))
        else:
            free_slots = [{'start':begin, 'end':end}]

        return free_slots

    def _is_enough_time(self, objectifs, temp_libre):
        objectifs_triee = sorted(objectifs, key=lambda x: datetime.strptime(x['deadline'], '%d/%m/%Y'))
        somme_time_objectifs = 0
        for objectif in objectifs_triee:
            time_objectif = objectif['temps']*60
            date = objectif['deadline']
            temps_libre = self._get_total_time_creneaux_libre_until_deadline(temp_libre, date)
            temps_libre -= (time_objectif + somme_time_objectifs)
            if temps_libre < 0:
                return False
            somme_time_objectifs += time_objectif
        return True


    def _get_total_time_creneaux_libre_until_deadline(self,days, date_str):
        total_time = 0
        date_actuelle = datetime.now()
        date_obj = datetime.strptime(date_str, "%d/%m/%Y") 
        date_obj -= timedelta(days=1)
        date_string_formatted = date_obj.strftime("%Y-%m-%d")
        i = 0
        while i < len(days) and datetime.strptime(days[i][0], "%Y-%m-%d") <= date_obj:
            day_creneaux_libres = days[i][1]
            for creneau in day_creneaux_libres:
                total_time += creneau['time']
            i += 1
        
        return total_time

    def _extraire_date_deadline(self,event):
        return datetime.strptime(event['deadline'], "%d/%m/%Y")

    def _get_temp_libre_until_last_goal(self,liste_events, list_cours):
        liste_events_triee = sorted(liste_events, key=self._extraire_date_deadline)

        # Date actuelle
        date_actuelle = datetime.now().date()
        date_last_deadline = liste_events_triee[-1]['deadline']
        # Date jusqu'à laquelle vous voulez générer la liste
        date_fin = datetime.strptime(date_last_deadline, '%d/%m/%Y').date()

        # Liste pour stocker les dates générées
        liste_dates = []

        # Boucle pour générer les dates jusqu'à la date de fin
        while date_actuelle < date_fin:
            date_actuelle_string = date_actuelle.strftime("%Y-%m-%d")
            temps_libre_by_date = self._get_creneaux_libre_by_day(list_cours[date_actuelle_string], 120)
            liste_dates.append([date_actuelle_string, temps_libre_by_date])
            date_actuelle += timedelta(days=1)  # Incrémentation d'un jour
        return liste_dates
        # Affichage de la liste des dates générées

    def _create_new_creneaux(self,temp_libre, list_cours, liste_objectifs):
        day_index = 0
        for event in liste_objectifs:
            temps_event = event['temps'] * 60
            event_name = event['name']
            creneau_index = 0  # Initialise creneau_index à zéro avant la boucle externe
            while temps_event > 0 and day_index < len(temp_libre):
                date = temp_libre[day_index][0]
                creneaux = temp_libre[day_index][1]
                while creneau_index < len(creneaux) and temps_event > 0:
                    heure_debut_creneau = creneaux[creneau_index]['start']
                    heure_fin_creneau = creneaux[creneau_index]['end']
                    temps_creneau = creneaux[creneau_index]['time']
                    if temps_creneau > 0:  # Ajoutez cette condition pour éviter les créneaux avec une durée nulle
                        if temps_creneau >= temps_event:
                            heure_fin = self._calculer_heure_fin(heure_debut_creneau, temps_event)
                            list_cours[date].append({'summary': event_name, 'start_time': heure_debut_creneau, 'end_time': heure_fin})
                            creneaux[creneau_index]['start'] = heure_fin
                            creneaux[creneau_index]['time'] -= temps_event
                            temps_event = 0
                        else:
                            list_cours[date].append({'summary': event_name, 'start_time': heure_debut_creneau, 'end_time': heure_fin_creneau})
                            temps_event -= temps_creneau
                            creneaux[creneau_index]['start'] = heure_fin_creneau
                            creneaux[creneau_index]['time'] = 0
                            creneau_index += 1  # Mettre à jour creneau_index pour passer au créneau suivant
                    else:
                        creneau_index += 1  # Passer au créneau suivant si la durée est nulle
                if temps_event > 0:
                    day_index += 1  # Passer au jour suivant si tous les créneaux pour le jour actuel ont été explorés
                    creneau_index = 0  # Réinitialiser creneau_index pour le nouveau jour
                

    def get_creneaux_supllémentaire(self, liste_objectifs, list_cours):
        temp_libre = self._get_temp_libre_until_last_goal(liste_objectifs, list_cours)
        if self._is_enough_time(liste_objectifs, temp_libre):
            self._create_new_creneaux(temp_libre, list_cours, liste_objectifs)
            return list_cours
        else:
            return -1


    def get_events_for_next_x_day(self,x):
        events = {}

        for i in range(x+1):
            futur_time = datetime.now() + timedelta(days=i)
            futur_time_date = futur_time.date()
            event = self._get_events_for_date_searched(futur_time_date)
            if str(futur_time) not in events.keys():
                events[str(futur_time_date)] = event
            else:
                events[str(futur_time_date)].append(event)
        return events
    
    def add_event(self, date, event):
        pass

# Lien vers le fichier ICS
ics_url = "https://ade-outils.insa-lyon.fr/ADE-Cal:~llhomme!2023-2024:a5c217dab6bd6040d9f1cf0f3285b7242f936f18"

agenda = Agenda_data(ics_url)
cours = agenda.get_events_for_next_x_day(20)


liste_objectifs = [
    {"name":"IE meca", "deadline":"23/04/2024", "temps":6},
    {"name":"IE math", "deadline":"21/04/2024", "temps":6}
]
new_agenda = agenda.get_creneaux_supllémentaire(liste_objectifs, cours)

