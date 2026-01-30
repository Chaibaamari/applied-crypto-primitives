import customtkinter as ctk
from tkinter import messagebox
from Model import miller_robin, fermat, solovay_strassen , aks
import time

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def solovay_strassen_test(n, k=10):
    return solovay_strassen(n, k)

def miller_rabin_test(n, k=10):
    return miller_robin(n, k)

def fermat_test(n, k=10):
    return fermat(n, k)

def aks_test(n, k=None):
    """AKS est déterministe, k n'est pas utilisé"""
    return aks(n)

def compare_tests(n, k):
    results = {}
    tests = {
        "Solovay-Strassen": solovay_strassen_test,
        "Miller-Rabin": miller_rabin_test,
        "Fermat": fermat_test,
        "AKS": aks_test
    }
   
    for test_name, test_func in tests.items():
        start = time.perf_counter()
        is_probable_prime = test_func(n, k)
        time_taken = (time.perf_counter() - start) * 1000  # ms
       
        if is_probable_prime:
            status = "Probablement Premier"
            if test_name == "Solovay-Strassen":
                err_prob = "≤ (1/2)^k"
            elif test_name == "Miller-Rabin":
                err_prob = "≤ (1/4)^k"
            elif test_name == "AKS":
                err_prob = "0 (déterministe - toujours correct)"
            else:
                err_prob = "< (1/2)^k (vulnérable aux nombres de Carmichael)"
        else:
            status = "Composé"
            err_prob = "0 (certain)"
       
        results[test_name] = {
            "status": status,
            "time_ms": time_taken,
            "err_prob": err_prob,
            "is_prime": is_probable_prime
        }
   
    return results

class ModernPrimalityCalculator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Calculateur de Test de Primalité")
        self.geometry("550x550")
        self.minsize(550, 550)

        # Main frame
        main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Titre en vert et gras
        title_label = ctk.CTkLabel(
            main_frame,
            text="🔢 Calculateur de Test de Primalité 🔢",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#10b981"
        )
        title_label.pack(pady=(20, 10))

        # Entrée: Nombre n
        self.n_entry = self.create_input_group(
            main_frame,
            "Nombre à Tester (n)",
            "ex: 2541, 561, xxxx"
        )

        # Entrée: Itérations k
        self.k_entry = self.create_input_group(
            main_frame,
            "Nombre d'Itérations (k)",
            "ex: 10"
        )
        self.k_entry.insert(0, "10")

        # Boutons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)

        self.calc_button = ctk.CTkButton(
            button_frame,
            text="LANCER LES TESTS",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            corner_radius=10,
            command=self.run_tests
        )
        self.calc_button.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.clear_button = ctk.CTkButton(
            button_frame,
            text="EFFACER",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            corner_radius=10,
            fg_color="#374151",
            hover_color="#4b5563",
            command=self.clear_all
        )
        self.clear_button.grid(row=0, column=1, padx=(10, 0), sticky="ew")

        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        # Cadre des résultats
        self.results_frame = ctk.CTkFrame(main_frame, corner_radius=10)

        results_title = ctk.CTkLabel(
            self.results_frame,
            text="📊 Résultats des Tests de Primalité",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#10b981",
            anchor="w"
        )
        results_title.pack(fill="x", padx=15, pady=(10, 8))

        self.results_textbox = ctk.CTkTextbox(
            self.results_frame,
            font=ctk.CTkFont(family="Courier New", size=12),
            wrap="word",
            corner_radius=8,
            height=400
        )
        self.results_textbox.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Cadre du résumé
        self.summary_frame = ctk.CTkFrame(main_frame, corner_radius=10)

        summary_title = ctk.CTkLabel(
            self.summary_frame,
            text="✨ Résumé Comparatif",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#10b981",
            anchor="w"
        )
        summary_title.pack(fill="x", padx=15, pady=(10, 8))

        self.summary_textbox = ctk.CTkTextbox(
            self.summary_frame,
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            wrap="word",
            corner_radius=8,
            height=120,
            fg_color="#1e293b"
        )
        self.summary_textbox.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def create_input_group(self, parent, label_text, placeholder):
        group_frame = ctk.CTkFrame(parent, fg_color="transparent")
        group_frame.pack(fill="x", pady=(10, 20))

        label = ctk.CTkLabel(
            group_frame,
            text=label_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        label.pack(fill="x", pady=(0, 8))

        entry = ctk.CTkEntry(
            group_frame,
            placeholder_text=placeholder,
            font=ctk.CTkFont(size=13),
            height=45,
            corner_radius=10,
            border_width=2
        )
        entry.pack(fill="x")

        info = ctk.CTkLabel(
            group_frame,
            text=f"Entrez {label_text.lower()}",
            font=ctk.CTkFont(size=10),
            text_color="gray60",
            anchor="w"
        )
        info.pack(fill="x", pady=(4, 0))

        return entry

    def run_tests(self):
        try:
            n_str = self.n_entry.get().strip()
            if not n_str:
                messagebox.showerror("Erreur de Saisie", "Veuillez entrer un nombre n")
                return
            n = int(n_str)
            if n < 2:
                messagebox.showerror("Erreur de Saisie", "Le nombre doit être ≥ 2")
                return

            k_str = self.k_entry.get().strip()
            k = int(k_str) if k_str else 10
            if k < 1:
                messagebox.showerror("Erreur de Saisie", "Les itérations k doivent être ≥ 1")
                return
        except ValueError:
            messagebox.showerror("Erreur de Saisie", "Veuillez entrer des entiers valides pour n et k")
            return

        # Afficher les cadres de résultats et de résumé
        if not self.results_frame.winfo_ismapped():
            self.results_frame.pack(fill="both", expand=True, pady=(10, 10))
            self.summary_frame.pack(fill="both", expand=True, pady=(0, 20))

        self.geometry("550x850")
        self.minsize(550, 850)

        # Effacer les résultats précédents
        self.results_textbox.configure(state="normal")
        self.summary_textbox.configure(state="normal")
        self.results_textbox.delete("1.0", "end")
        self.summary_textbox.delete("1.0", "end")

        self.results_textbox.insert("1.0", f"Test de n = {n} avec k = {k} itérations\n\n")

        results = compare_tests(n, k)

        # Schéma de couleurs pour chaque test
        test_colors = {
            "Solovay-Strassen": "#ff6b6b",  # Rouge
            "Miller-Rabin": "#4ecdc4",      # Turquoise/Cyan
            "Fermat": "#ffe66d",
            "AKS": "#a78bfa"        
        }

        # Afficher les résultats individuels des tests avec couleurs
        for test_name, data in results.items():
            test_color = test_colors.get(test_name, "#3b82f6")
            status_color = "#10b981" if data["is_prime"] else "#ef4444"
            
            # Nom du test dans sa couleur distinctive
            self.results_textbox.insert("end", f"━━━ {test_name} ━━━\n", ("title", test_color))
            
            # Statut
            self.results_textbox.insert("end", f" Statut : ", "label")
            self.results_textbox.insert("end", f"{data['status']}\n", ("status", status_color))
            
            # Temps
            self.results_textbox.insert("end", f" Temps : ", "label")
            self.results_textbox.insert("end", f"{data['time_ms']:.4f} ms\n", "time")
            
            # Probabilité d'erreur en couleur
            self.results_textbox.insert("end", f" Probabilité d'Erreur : ", "label")
            prob_color = "#10b981" if data['err_prob'] == "0 (certain)" else "#fbbf24"
            self.results_textbox.insert("end", f"{data['err_prob']}\n\n", ("error_prob", prob_color))

        # Résumé
        all_prime = all(data["is_prime"] for data in results.values())
        statuses = [data["status"] for data in results.values()]
        agreement = "Tous les tests sont d'accord ! ✓" if len(set(statuses)) == 1 else "Les tests ne sont pas d'accord ! ⚠"
        fastest = min(results, key=lambda x: results[x]["time_ms"])

        summary_text = f"Concordance : {agreement}\n"
        summary_text += f"Verdict Global : {'Probablement Premier ✓' if all_prime else 'Composé ✗'}\n"
        summary_text += f"Test le Plus Rapide : {fastest} ({results[fastest]['time_ms']:.4f} ms)"

        self.summary_textbox.insert("1.0", summary_text)

        # Configurer toutes les balises de couleur (accès au widget Tkinter interne)
        textbox = self.results_textbox._textbox
        textbox.tag_configure("label", foreground="#94a3b8")
        textbox.tag_configure("time", foreground="#60a5fa")
        textbox.tag_configure("error_prob")
        textbox.tag_configure("status")
        
        # Couleurs spécifiques aux tests
        for test_name, color in test_colors.items():
            textbox.tag_configure(color, foreground=color)

        # Désactiver l'édition
        self.results_textbox.configure(state="disabled")
        self.summary_textbox.configure(state="disabled")

    def clear_all(self):
        self.n_entry.delete(0, "end")
        self.k_entry.delete(0, "end")
        self.k_entry.insert(0, "10")
        
        self.results_textbox.configure(state="normal")
        self.summary_textbox.configure(state="normal")
        self.results_textbox.delete("1.0", "end")
        self.summary_textbox.delete("1.0", "end")
        
        self.results_frame.pack_forget()
        self.summary_frame.pack_forget()
        
        self.geometry("550x550")
        self.minsize(550, 550)
        self.update_idletasks()

if __name__ == "__main__":
    app = ModernPrimalityCalculator()
    app.mainloop()