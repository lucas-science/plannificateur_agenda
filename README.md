# plannificateur_agenda


### Récupération les évenements des x:int prochains jours 
x=0 représente aujourd'hui, x=1 représente demain, ..., x=i représente le xème jour inclus.

```python
ics_url = "https://ade-outils.insa-lyon.fr/ADE-Cal:~llhomme!2023-2024:a5c217dab6bd6040d9f1cf0f3285b7242f936f18"

agenda = Agenda_data(ics_url)
events = agenda.get_events_for_next_x_day(3)
```

on obtient alors : 
```json
{'2024-04-04': [
    {'summary': 'FIMI:2:S2::MA-TF:TD::055 #016', 'start_time': '08:00', 'end_time': '09:00'}, 
    {'summary': 'FIMI:2:S2::CSS-FC:TD::055 #006', 'start_time': '06:00', 'end_time': '08:00'}
    ],
'2024-04-05': [
    {'summary': 'PH O1 Câble gr055', 'start_time': '06:00', 'end_time': '09:00'}, 
    ......
    {'summary': 'FIMI:2:S0::*:EDT::N #041', 'start_time': '12:00', 'end_time': '16:00'}
    ], 
    '2024-04-06': [], 
    '2024-04-07': []
    }
```
les liste vides représentent les jours sans cours (weekend, jour ferié..)
