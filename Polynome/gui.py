import customtkinter as ctk
from tkinter import messagebox
import re
from utils import valider_polynome
from model import PGCD, inverse, Polynome


class ModernPolynomialCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Polynomial Calculator")
        self.root.geometry("500x600")
        self.root.minsize(550, 550)
        
        # Set theme and color
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main frame
        main_frame = ctk.CTkFrame(root, corner_radius=0, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)  # reduced from 20
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Calculateur de polynômes",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#3b82f6"
        )
        title_label.pack(pady=(0, 5))  # reduced from 10
        
        # First Polynomial Input
        self.poly1_entry = self.create_input_group(
            main_frame,
            "Premier polynôme",
            "e.g., x^2 + 3x + 2"
        )
        
        # Second Polynomial Input
        self.poly2_entry = self.create_input_group(
            main_frame,
            "Deuxième polynôme",
            "e.g., 2x^2 - x + 5"
        )
        
        # Prime Number Input
        self.prime_entry = self.create_input_group(
            main_frame,
            "Nombre premier",
            "e.g., 7"
        )
        
        # Operation Selection Frame
        operation_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        operation_frame.pack(fill="x", pady=(0, 5))  # reduced from 10
        
        # Operation Label
        operation_label = ctk.CTkLabel(
            operation_frame,
            text="Séléction une opération",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        operation_label.pack(fill="x", pady=(0, 4))  # reduced from 8
        
        # Radio buttons frame
        radio_frame = ctk.CTkFrame(operation_frame, fg_color="transparent")
        radio_frame.pack(fill="x")
        
        # Operation variable
        self.operation_var = ctk.StringVar(value="gcd")
        
        # GCD Radio Button
        self.gcd_radio = ctk.CTkRadioButton(
            radio_frame,
            text="Calculer le PGCD",
            variable=self.operation_var,
            value="gcd",
            font=ctk.CTkFont(size=12),
            command=self.on_operation_change
        )
        self.gcd_radio.pack(side="left", padx=(0, 30))
        
        # Inverse Radio Button
        self.inverse_radio = ctk.CTkRadioButton(
            radio_frame,
            text="Calculer l'inverse dans M(x)",
            variable=self.operation_var,
            value="inverse",
            font=ctk.CTkFont(size=12),
            command=self.on_operation_change
        )
        self.inverse_radio.pack(side="left")
        
        # Info text for operation
        operation_info = ctk.CTkLabel(
            operation_frame,
            text="Choisissez une option",
            font=ctk.CTkFont(size=10),
            text_color="gray60",
            anchor="w"
        )
        operation_info.pack(fill="x", pady=(4, 0))  # reduced from 8
        
        # GCD Frame (initially hidden)
        self.gcd_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        
        # GCD/Inverse Label (will change based on selection)
        self.result_label = ctk.CTkLabel(
            self.gcd_frame,
            text="Résultat du PGCD",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        self.result_label.pack(fill="x", pady=(0, 4))  # reduced from 8
        
        # GCD/Inverse Entry (for displaying/editing result)
        self.gcd_entry = ctk.CTkEntry(
            self.gcd_frame,
            placeholder_text="Result will be calculated here",
            font=ctk.CTkFont(size=13),
            height=45,
            corner_radius=10,
            border_width=2
        )
        self.gcd_entry.pack(fill="x")
        
        # Info text for result
        self.result_info = ctk.CTkLabel(
            self.gcd_frame,
            text="Le plus grand commun diviseur des deux polynômes",
            font=ctk.CTkFont(size=10),
            text_color="gray60",
            anchor="w"
        )
        self.result_info.pack(fill="x", pady=(2, 0))  # reduced from 4
        
        # Button Frame
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 15))
        
        # Configure grid
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Calculate Button
        self.calc_button = ctk.CTkButton(
            button_frame,
            text="Calculer",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=45,
            corner_radius=10,
            command=self.calculate
        )
        self.calc_button.grid(row=0, column=0, padx=(0, 6), sticky="ew")
        
        # Clear Button
        self.clear_button = ctk.CTkButton(
            button_frame,
            text="Supprimer",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=45,
            corner_radius=10,
            fg_color="#374151",
            hover_color="#4b5563",
            command=self.clear_all
        )
        self.clear_button.grid(row=0, column=1, padx=(6, 0), sticky="ew")
        
        # Demonstration Frame (initially hidden)
        self.demo_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        
        # Demonstration Title
        demo_title = ctk.CTkLabel(
            self.demo_frame,
            text="Démonstration étape par étape",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#10b981",
            anchor="w"
        )
        demo_title.pack(fill="x", padx=15, pady=(10, 8))
        
        # Demonstration Textbox
        self.demo_textbox = ctk.CTkTextbox(
            self.demo_frame,
            font=ctk.CTkFont(family="Courier New", size=11),
            wrap="word",
            corner_radius=8,
            height=300
        )
        self.demo_textbox.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Result Frame (initially hidden)
        self.result_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        
        # Result Title
        result_title = ctk.CTkLabel(
            self.result_frame,
            text="Result",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#3b82f6",
            anchor="w"
        )
        result_title.pack(fill="x", padx=15, pady=(10, 8))
        
        # Result Textbox
        self.result_textbox = ctk.CTkTextbox(
            self.result_frame,
            font=ctk.CTkFont(family="Courier New", size=11),
            wrap="word",
            corner_radius=8,
            height=150
        )
        self.result_textbox.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        # Keyboard shortcut
        self.root.bind('<Control-Return>', lambda e: self.calculate())
        
    def create_input_group(self, parent, label_text, placeholder):
        """Create an input group with label and entry"""
        group_frame = ctk.CTkFrame(parent, fg_color="transparent")
        group_frame.pack(fill="x", pady=(0, 15))
        
        # Label
        label = ctk.CTkLabel(
            group_frame,
            text=label_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        label.pack(fill="x", pady=(0, 8))
        
        # Entry
        entry = ctk.CTkEntry(
            group_frame,
            placeholder_text=placeholder,
            font=ctk.CTkFont(size=13),
            height=45,
            corner_radius=10,
            border_width=2
        )
        entry.pack(fill="x")
        
        # Info text
        info = ctk.CTkLabel(
            group_frame,
            text=f"Enter {label_text.lower()}",
            font=ctk.CTkFont(size=10),
            text_color="gray60",
            anchor="w"
        )
        info.pack(fill="x", pady=(4, 0))
        
        return entry
        

    def on_operation_change(self):
        """Update labels when operation selection changes"""
        if self.operation_var.get() == "gcd":
            self.result_label.configure(text="Résultat du PGCD")
            self.result_info.configure(text="PGCD des deux polynômes")
            self.gcd_entry.configure(placeholder_text="GCD will be calculated here")
        else:  # inverse
            self.result_label.configure(text="Résultat de l'inverse")
            self.result_info.configure(text="Le résultat de l'inverse du premier polynôme dans M(x)")
            self.gcd_entry.configure(placeholder_text="Inverse will be calculated here")
    
    def is_prime(self, num):
        """Check if a number is prime"""
        if num <= 1:
            return False
        if num <= 3:
            return True
        if num % 2 == 0 or num % 3 == 0:
            return False
        
        i = 5
        while i * i <= num:
            if num % i == 0 or num % (i + 2) == 0:
                return False
            i += 6
        return True
    
    def calculate(self):
        """Perform polynomial calculations"""
        # Get input values
        poly1_str = self.poly1_entry.get().strip()
        poly2_str = self.poly2_entry.get().strip()
        prime_str = self.prime_entry.get().strip()
        
        # Validate inputs
        if not poly1_str or not poly2_str:
            messagebox.showerror("Input Error", "Entrer les deux polynômes")
            return
        
        if not prime_str:
            messagebox.showerror("Input Error", "Entrer un nombre premier")
            return
        
        try:
            prime_num = int(prime_str)
        except ValueError:
            messagebox.showerror("Input Error", "Le nombre premier doit être un entier")
            return
        
        if not self.is_prime(prime_num):
            messagebox.showerror("Input Error", f"{prime_num} n'est pas premier")
            return
        
        try:
            # Parse polynomials
            try:
                poly1_vec = valider_polynome(poly1_str)
                poly2_vec = valider_polynome(poly2_str)

            except Exception as e:
                messagebox.showerror("Erreur de conversion", str(e))
                return

            # Show frames in correct order (gcd_frame first, then demo_frame, then result_frame)
            if not self.gcd_frame.winfo_ismapped():
                self.gcd_frame.pack(fill="x", pady=(0, 15), before=self.calc_button.master)
            
            if not self.demo_frame.winfo_ismapped():
                self.demo_frame.pack(fill="both", expand=True, pady=(0, 8))
            
            if not self.result_frame.winfo_ismapped():
                self.result_frame.pack(fill="both", expand=True)

            self.root.geometry("550x900")

            poly1 = Polynome(poly1_vec)
            poly2 = Polynome(poly2_vec)

            operation = self.operation_var.get()
            demonstration = []
            
            if operation == "gcd":
                try:
                    result, demonstration = PGCD(poly1, poly2, prime_num)
                except Exception as e:
                    messagebox.showerror("Erreur", str(e))
                    return
            else:
                try:
                    pgcd, _ = PGCD(poly1, poly2, prime_num)
                    result, inverse2 = inverse(poly1, poly2, prime_num)
                except Exception as e:
                    messagebox.showerror("Erreur", str(e))
                    return

            self.demo_textbox.configure(state='normal')
            self.gcd_entry.configure(state='normal')

            # Clear old content
            self.demo_textbox.delete("1.0", "end")
            self.gcd_entry.delete(0, "end")

            demo_placeholder = ""

            # Insert new content
            if operation == "gcd":
                self.gcd_entry.insert(0, f"PGCD({poly1}, {poly2}) = {result}")
                
                for d in demonstration:
                    demo_placeholder += f"{d}\n"
            else:
                self.gcd_entry.insert(0, f"L'inverse de {poly1} dans F{prime_num}/({poly2}) = {result}")

                a = poly1.multiplier(result, prime_num)
                b = poly2.multiplier(inverse2, prime_num)

                demo_placeholder += f"({poly1}) * ({result}) + ({poly2}) * ({inverse2}) = \n"
                demo_placeholder += f"  ({a}) + ({b}) \n"
                demo_placeholder += f"  = {pgcd}\n"

            self.demo_textbox.insert("1.0", demo_placeholder)

            self.demo_textbox.configure(state='disabled')
            self.gcd_entry.configure(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Calculation Error", f"Error: {str(e)}")
    
    def clear_all(self):
        """Clear all input fields and results"""
        self.poly1_entry.delete(0, "end")
        self.poly2_entry.delete(0, "end")
        self.prime_entry.delete(0, "end")
        self.gcd_entry.delete(0, "end")
        self.result_textbox.delete("0.0", "end")
        self.demo_textbox.delete("0.0", "end")
        
        # Hide GCD, demonstration, and result frames
        self.gcd_frame.pack_forget()
        self.demo_frame.pack_forget()
        self.result_frame.pack_forget()

        #
        self.root.geometry("550x600")


def main():
    # Create root window
    root = ctk.CTk()
    
    # Create application
    app = ModernPolynomialCalculator(root)
    
    # Run application
    root.mainloop()


if __name__ == "__main__":
    main()