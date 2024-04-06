import requests
import calendar
from icalendar import Calendar
from datetime import datetime, timedelta

tomorrow = datetime.now() + timedelta(days=1)
tomorrow_date = tomorrow.date()


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
events = agenda.get_events_for_next_x_day(3)