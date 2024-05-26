import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

from controllers.controllers import Controller



class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestionnaire emplois du temps")
        self.completed_events = []
        self.geometry("900x600")
        
        self.menu_frame = tk.Frame(self, bg="lightgrey", width=200)
        self.menu_frame.pack(side="left", fill="y")

        self.main_frame = tk.Frame(self, bg="white")
        self.main_frame.pack(expand=True, fill="both")
        self.week_frame = tk.Frame(self.main_frame)

        self.c = Controller()
        self.agenda_data = None
        self.status_generation_automatique = 0

        self.create_menu()
        self.show_agenda_or_formulaire()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        # Save data before closing
        self.c.local_storage.save_data()
        self.destroy()

    def change_title(self,status):
        if status == -1:
            self.title('Gestionnaire emplois du temps - Combinaison impossible')
        elif status == 0:
            self.title('Gestionnaire emplois du temps')
        else:
            self.title('Gestionnaire emplois du temps - Combinaison possible')
    
    def show_week_events(self, current_date, week_frame):
        # Clear previous week widgets

        taches_fini = self.c.local_storage.get_state('taches_fini')
        for widget in week_frame.winfo_children():
            widget.destroy()

        # Create labels for days of the week
        days_of_week = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

        for col in range(7):
            date = (current_date + timedelta(days=col)).strftime('%Y-%m-%d')
            tk.Label(week_frame, text=date).grid(row=0, column=col+1)

        # Create labels for hours
        for row in range(24):
            tk.Label(week_frame, text=f"{row:02}:00").grid(row=row+1, column=0)

        # Fill events in the schedule
        for date, events in self.agenda_data.items():
            for event in events:
                event_date = datetime.strptime(date, '%Y-%m-%d').date()
                if event_date <= current_date + timedelta(days=6) and event_date >= current_date:
                    col = (event_date - current_date).days
                    
                    # Extract start and end times
                    start_time_str = event['start_time']
                    end_time_str = event['end_time']
                    
                    try:
                        # Convert start and end times to integers
                        start_hour, start_minute = map(int, start_time_str.split(':'))
                        end_hour, end_minute = map(int, end_time_str.split(':'))
                        
                        # Check if start and end hours and minutes are within valid ranges
                        if not 0 <= start_hour <= 23 or not 0 <= start_minute <= 59:
                            raise ValueError("Heure de début invalide")
                        if not 0 <= end_hour <= 23 or not 0 <= end_minute <= 59:
                            raise ValueError("Heure de fin invalide")
                        
                        # Calculate start and end rows
                        start_row = start_hour + 1
                        end_row = end_hour + 1
                        event_text = f"{event['summary']} ({event['start_time']} - {event['end_time']})"
                        
                        # Check if the event is completed and in the completed events list
                        event_completed = False
                        event["completed"] = True
                        for tache_fini in taches_fini:
                            if event == tache_fini[0]:
                                event_completed = True
                        if event_completed == False:
                            event["completed"] = False

                        # Create a clickable button for each event
                        button = tk.Button(week_frame, text=event_text, wraplength=100, command=lambda e=event: self.toggle_completion(e, datetime.strptime(date, '%Y-%m-%d')))
                        button.grid(row=start_row, column=col+1, rowspan=end_row-start_row, sticky="nsew")
                        
                        # Change background color based on completion status
                        if event_completed:
                            button.config(bg='green', activebackground='green')  # Mise à jour de la couleur d'arrière-plan en vert
                        else:
                            button.config(bg='yellow', activebackground='yellow')

                    except ValueError as e:
                        messagebox.showerror("Erreur", str(e))
                        continue

        # Configure row and column weights
        week_frame.grid_rowconfigure(0, weight=1)
        week_frame.grid_columnconfigure(0, weight=1)
        for i in range(24):
            week_frame.grid_rowconfigure(i+1, weight=1)
        for i in range(7):
            week_frame.grid_columnconfigure(i+1, weight=1)

    def update_completed_events(self):
        # Récupération de l'historique des tâches réalisées depuis le local storage
        history = self.c.local_storage.get_state("taches_fini")
        
        # Parcours des événements de l'agenda
        for widget in self.week_frame.winfo_children():
            if isinstance(widget, tk.Button):
                event_text = widget.cget('text')
                # Vérification si l'événement est dans l'historique des tâches réalisées
                if any('summary' in event and event['summary'] in event_text for event in history):
                    widget.config(bg='green', activebackground='green')  # Mise à jour de la couleur d'arrière-plan en vert

    def toggle_completion(self, event, event_date):
        event['completed'] = not event.get('completed', False)
        print(event['completed'])
        if event['completed']:
            self.c.post_tache_fini(event, event_date)
            self.c.increase_streak()
        else:
            self.c.delete_finished_task(event, event_date)
            self.c.decrease_streak()
        self.show_week_events(current_date, self.week_frame)

    def send_link(self):
        url = self.entry.get()
        if url:
            self.c.local_storage.change_state('url', url)
            self.c.init_agenda_data(url)
            status_generation_automatique , self.agenda_data = self.c.get_plannification_automatique()
            self.change_title(status_generation_automatique)
            self.show_page_agenda()
        else:
            messagebox.showwarning("Avertissement", "Veuillez entrer un lien valide.")
    
    def collect_and_send_data(self):
            # Collect data from the entry widgets
            task = self.entry1.get()
            duration = self.entry2.get()
            deadline = self.entry3.get()
            
            # Validate data
            if not task or not duration or not deadline:
                tk.messagebox.showerror("Erreur", "Tous les champs doivent être remplis.")
                return
            
            try:
                duration = int(duration)
            except ValueError:
                tk.messagebox.showerror("Erreur", "La durée doit être un nombre entier.")
                return
            
            try:
                deadline = datetime.strptime(deadline, "%d/%m/%Y").strftime("%d/%m/%Y")
            except ValueError:
                tk.messagebox.showerror("Erreur", "La date limite doit être au format jj/mm/aaaa.")
                return
            
            # Format the data
            new_objectif = {"name": task, "deadline": deadline, "temps": duration}
            
            # Send the data using the controller method
            self.c.post_list_objectifs([new_objectif])
            tk.messagebox.showinfo("Succès", "L'objectif a été ajouté avec succès.")
            status_generation_automatique , self.agenda_data = self.c.get_plannification_automatique()
            self.change_title(status_generation_automatique)
            self.show_page2()

    def show_agenda_or_formulaire(self):
        AGENDA_URL = self.c.local_storage.get_state('url')
        if AGENDA_URL:
            self.c.init_agenda_data(AGENDA_URL)
            status_generation_automatique , self.agenda_data = self.c.get_plannification_automatique()
            self.change_title(status_generation_automatique)
            self.show_page_agenda() 
        else:
            self.show_page1()


    def delete_objective_and_update(self, objective):
        self.delete_objective(objective)
        status_generation_automatique , self.agenda_data = self.c.get_plannification_automatique()
        self.change_title(status_generation_automatique)
        self.show_page2()
        

    def delete_objective(self, objective):
        # Get current objectives from the controller
        objectives = self.c.local_storage.get_state("objectifs_utilisateur")

        # Remove the objective from the list
        objectives.remove(objective)

        # Update the local storage with the modified list of objectives
        self.c.local_storage.change_state("objectifs_utilisateur", objectives)

        # Re-display the objectives
        self.show_page2()
    
    def create_menu(self):
        menu_label = tk.Label(self.menu_frame, text="Menu", bg="lightgrey")
        menu_label.pack(pady=10)

        # Button to show page 1
        button1 = tk.Button(self.menu_frame, text="Visualisation Agenda", command=self.show_agenda_or_formulaire)
        button1.pack(fill="x")

        # Button to show page 2
        button2 = tk.Button(self.menu_frame, text="Définition Objectifs", command=self.show_page2)
        button2.pack(fill="x")

        # Button to show page 3
        button3 = tk.Button(self.menu_frame, text="Historique et score", command=self.show_page3)
        button3.pack(fill="x")

    def show_page1(self):
        self.clear_main_frame()
        
        # Create entry widget for URL EDT
        entry_label = tk.Label(self.main_frame, text="Lien de votre emploi du temps:", pady=10)
        entry_label.pack()
        self.entry = tk.Entry(self.main_frame)
        self.entry.pack(pady=10)

        # Create a button to send the link
        send_button = tk.Button(self.main_frame, text="Envoyer", command=self.send_link)
        send_button.pack(pady=10)

    def show_page_agenda(self):
        self.clear_main_frame()
        self.main_frame.configure(bg="#add8e6")

        global current_date
        current_date = datetime.now().date()
        self.week_frame = tk.Frame(self.main_frame)
        self.week_frame.pack(pady=10)

        self.completed_events = []

        self.show_week_events(current_date, self.week_frame)
        self.update_completed_events()  # Appel de la fonction pour mettre à jour les événements déjà réalisés

    def show_page2(self):
        self.clear_main_frame()
        label = tk.Label(self.main_frame, text="Définissez vos objectifs", pady=10)
        label.grid(row=0, column=0, columnspan=6, padx=10, pady=10)
        
        # Labels for entry widgets
        entry_label1 = tk.Label(self.main_frame, text="Tâche à réaliser:")
        entry_label1.grid(row=1, column=0, padx=5, pady=5)
        
        entry_label2 = tk.Label(self.main_frame, text="Durée de la tâche:")
        entry_label2.grid(row=1, column=2, padx=5, pady=5)
        
        entry_label3 = tk.Label(self.main_frame, text="Date limite:")
        entry_label3.grid(row=1, column=4, padx=5, pady=5)

        # Create entry widgets
        self.entry1 = tk.Entry(self.main_frame)
        self.entry1.grid(row=1, column=1, padx=5, pady=5)

        self.entry2 = tk.Entry(self.main_frame)
        self.entry2.grid(row=1, column=3, padx=5, pady=5)

        self.entry3 = tk.Entry(self.main_frame)
        self.entry3.grid(row=1, column=5, padx=5, pady=5)
        
        # Button to add a task
        button4 = tk.Button(self.main_frame, text="Ajouter une tâche", command=self.collect_and_send_data)
        button4.grid(row=2, column=0, columnspan=6, padx=10, pady=20)

        # Get current objectives from the controller
        objectives = self.c.local_storage.get_state("objectifs_utilisateur")

        # Display objectives
        for i, objective in enumerate(objectives):
            objective_text = f"Tâche : {objective['name']} - Durée : {objective['temps']} - Date limite : {objective['deadline']}"

            # Create label for the objective
            label = tk.Label(self.main_frame, text=objective_text)
            label.grid(row=i+3, column=0, columnspan=4, padx=10, pady=5, sticky="w")
            # Create button to delete the objective
            delete_button = tk.Button(self.main_frame, text="Supprimer", command=lambda obj=objective: self.delete_objective_and_update(obj))
            delete_button.grid(row=i+3, column=4, padx=10, pady=5, sticky="e")
        
    def show_page3(self):
        self.clear_main_frame()
        label = tk.Label(self.main_frame, text="Votre historique des tâches accomplies et votre score", pady=10)
        label.pack()

        # Radio buttons
        radio_var = tk.IntVar()
        radio_var.set(1)  # Default selection
        history_radio = tk.Radiobutton(self.main_frame, text="Historique", variable=radio_var, value=1)
        history_radio.pack()
        score_radio = tk.Radiobutton(self.main_frame, text="Score", variable=radio_var, value=2)
        score_radio.pack()
    
        # Text area
        text_area = tk.Text(self.main_frame, height=10, width=80)
        text_area.pack()

        historique = self.c.local_storage.get_state('taches_fini')
        historique_txt = ''
        for tache in historique:
            event, day = tache
            texte = f"{event['summary']} de {event['start_time']} à {event['end_time']}, a été réalisé le {day}"
            historique_txt += texte + '\n'
        
        score = self.c.getScore()

        def display_selected():
            selection = radio_var.get()
            if selection == 1:
                text_area.delete(1.0, tk.END)
                text_area.insert(tk.END, historique_txt)
            elif selection == 2:
                text_area.delete(1.0, tk.END)
                text_area.insert(tk.END, str(score))
    
        # Button to display selection
        display_button = tk.Button(self.main_frame, text="Afficher", command=display_selected)
        display_button.pack()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
