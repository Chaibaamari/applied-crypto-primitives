"""
Modern AES Encryption/Decryption Tool using CustomTkinter

Requirements:
    pip install customtkinter

Usage:
    python aes_crypto_app.py
    
Note: Replace the encrypt_text() and decrypt_text() functions with your own implementations
"""

import customtkinter as ctk
from tkinter import messagebox
import base64
from encryption import encrypt_text
from decryption import decrypt_text
from utils import derive_aes_key
from ecdh import generate_keypair, compute_shared_secret


class ModernAESCryptoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AES Encryption/Decryption Tool")
        self.root.geometry("900x900")
        self.root.resizable(False, False)
        
        # Set theme and color
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Variables pour le chat
        self.chaiba_private = None
        self.chaiba_public = None
        self.houdaifa_private = None
        self.houdaifa_public = None
        
        # Create main frame
        main_frame = ctk.CTkFrame(root, corner_radius=0, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Outil de Chiffrement AES",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#3b82f6"
        )
        title_label.pack(pady=(0, 20))

        # Create Tabview
        self.tabview = ctk.CTkTabview(main_frame, height=750)
        self.tabview.pack(fill="both", expand=True)
        
        # Add tabs
        self.tabview.add("Chiffrement")
        self.tabview.add("Chat Sécurisé")
        
        # Build tabs
        self.build_encryption_tab()
        self.build_chat_tab()

    def build_encryption_tab(self):
        tab = self.tabview.tab("Chiffrement")

        # Operation Selection Frame
        operation_frame = ctk.CTkFrame(tab, fg_color="transparent")
        operation_frame.pack(fill="x", pady=(0, 15))
        
        # Operation Label
        operation_label = ctk.CTkLabel(
            operation_frame,
            text="Sélectionner l'opération",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        operation_label.pack(fill="x", pady=(0, 12))
        
        # Radio buttons frame
        radio_frame = ctk.CTkFrame(operation_frame, fg_color="transparent")
        radio_frame.pack(fill="x")
        
        # Operation variable
        self.operation_var = ctk.StringVar(value="encrypt")
        
        # Encrypt Radio Button
        self.encrypt_radio = ctk.CTkRadioButton(
            radio_frame,
            text="Chiffrer",
            variable=self.operation_var,
            value="encrypt",
            font=ctk.CTkFont(size=12),
            command=self.on_operation_change
        )
        self.encrypt_radio.pack(side="left", padx=(0, 30))
        
        # Decrypt Radio Button
        self.decrypt_radio = ctk.CTkRadioButton(
            radio_frame,
            text="Déchiffrer",
            variable=self.operation_var,
            value="decrypt",
            font=ctk.CTkFont(size=12),
            command=self.on_operation_change
        )
        self.decrypt_radio.pack(side="left")
        
        # Frame pour le choix de la taille de clé AES (maintenant après l'opération)
        key_size_frame = ctk.CTkFrame(tab, fg_color="transparent")
        key_size_frame.pack(fill="x", pady=(0, 15))
        
        key_size_label = ctk.CTkLabel(
            key_size_frame,
            text="Taille de la clé AES",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        key_size_label.pack(fill="x", pady=(0, 12))
        
        # Radio buttons frame pour la taille de clé
        key_size_radio_frame = ctk.CTkFrame(key_size_frame, fg_color="transparent")
        key_size_radio_frame.pack(fill="x")
        
        # Variable pour stocker la taille choisie (en nombre de caractères hex)
        self.key_size_var = ctk.StringVar(value="32")
        
        # AES-128 Radio Button
        self.aes128_radio = ctk.CTkRadioButton(
            key_size_radio_frame,
            text="AES-128 (32 hex)",
            variable=self.key_size_var,
            value="32",
            font=ctk.CTkFont(size=12)
        )
        self.aes128_radio.pack(side="left", padx=(0, 20))
        
        # AES-192 Radio Button
        self.aes192_radio = ctk.CTkRadioButton(
            key_size_radio_frame,
            text="AES-192 (48 hex)",
            variable=self.key_size_var,
            value="48",
            font=ctk.CTkFont(size=12)
        )
        self.aes192_radio.pack(side="left", padx=(0, 20))
        
        # AES-256 Radio Button
        self.aes256_radio = ctk.CTkRadioButton(
            key_size_radio_frame,
            text="AES-256 (64 hex)",
            variable=self.key_size_var,
            value="64",
            font=ctk.CTkFont(size=12)
        )
        self.aes256_radio.pack(side="left")
        
        # Key Input Frame (avec bouton Generate ECDH sur la même ligne)
        key_input_frame = ctk.CTkFrame(tab, fg_color="transparent")
        key_input_frame.pack(fill="x", pady=(0, 15))
        
        # Label
        key_label = ctk.CTkLabel(
            key_input_frame,
            text="Clé de chiffrement (Hex)",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        key_label.pack(fill="x", pady=(0, 8))
        
        # Frame pour l'entrée et le bouton sur la même ligne
        key_row_frame = ctk.CTkFrame(key_input_frame, fg_color="transparent")
        key_row_frame.pack(fill="x")
        
        # Entry (prend la majorité de l'espace)
        self.key_entry = ctk.CTkEntry(
            key_row_frame,
            placeholder_text="Entrez votre clé en hexadécimal",
            font=ctk.CTkFont(size=13),
            height=45,
            corner_radius=10,
            border_width=2
        )
        self.key_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Bouton Generate ECDH Key (à côté de l'entrée)
        self.generate_button = ctk.CTkButton(
            key_row_frame,
            text="GÉNÉRER ECDH",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=45,
            width=150,
            corner_radius=10,
            fg_color="#6366f1",
            hover_color="#4f46e5",
            command=self.generate_ecdh_key
        )
        self.generate_button.pack(side="left")
        
        # Input Text Area
        input_frame = ctk.CTkFrame(tab, fg_color="transparent")
        input_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        input_label = ctk.CTkLabel(
            input_frame,
            text="Texte d'entrée",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        input_label.pack(fill="x", pady=(0, 8))
        
        self.input_textbox = ctk.CTkTextbox(
            input_frame,
            font=ctk.CTkFont(size=12),
            wrap="word",
            corner_radius=10,
            height=200,
            border_width=2
        )
        self.input_textbox.pack(fill="both", expand=True)
        
        # Button Frame
        button_frame = ctk.CTkFrame(tab, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 15))
        
        # Configure grid
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        
        # Process Button
        self.process_button = ctk.CTkButton(
            button_frame,
            text="CHIFFRER",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=45,
            corner_radius=10,
            command=self.process
        )
        self.process_button.grid(row=0, column=0, padx=(0, 6), sticky="ew")
        
        # Copy Button
        self.copy_button = ctk.CTkButton(
            button_frame,
            text="COPIER",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=45,
            corner_radius=10,
            fg_color="#10b981",
            hover_color="#059669",
            command=self.copy_output
        )
        self.copy_button.grid(row=0, column=1, padx=(3, 3), sticky="ew")
        
        # Clear Button
        self.clear_button = ctk.CTkButton(
            button_frame,
            text="EFFACER",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=45,
            corner_radius=10,
            fg_color="#374151",
            hover_color="#4b5563",
            command=self.clear_all
        )
        self.clear_button.grid(row=0, column=2, padx=(6, 0), sticky="ew")
        
        # Output Frame
        output_frame = ctk.CTkFrame(tab, fg_color="transparent")
        output_frame.pack(fill="both", expand=True)
        
        # Output Title
        self.output_title = ctk.CTkLabel(
            output_frame,
            text="Sortie chiffrée",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#10b981",
            anchor="w"
        )
        self.output_title.pack(fill="x", pady=(0, 8))
        
        # Output Textbox
        self.output_textbox = ctk.CTkTextbox(
            output_frame,
            font=ctk.CTkFont(family="Courier New", size=11),
            wrap="word",
            corner_radius=10,
            height=200,
            border_width=2
        )
        self.output_textbox.pack(fill="both", expand=True)
        
        # Keyboard shortcuts
        self.root.bind('<Control-Return>', lambda e: self.process())
    
    # Build Chat Tab
    def build_chat_tab(self):
        """Build the secure chat tab"""
        tab = self.tabview.tab("Chat Sécurisé")
        
        # Title
        title = ctk.CTkLabel(
            tab,
            text="💬 Communication sécurisée (chaiba ↔ houdaifa)",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#8b5cf6"
        )
        title.pack(pady=(0, 15))
        
        # Container for chaiba and houdaifa
        users_frame = ctk.CTkFrame(tab, fg_color="transparent")
        users_frame.pack(fill="both", expand=True)
        
        # Configure columns
        users_frame.grid_columnconfigure(0, weight=1)
        users_frame.grid_columnconfigure(1, weight=1)
        
        # ====== chaiba SECTION ======
        chaiba_frame = ctk.CTkFrame(users_frame, corner_radius=15, border_width=2, border_color="#3b82f6")
        chaiba_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        chaiba_header = ctk.CTkLabel(
            chaiba_frame,
            text="👤 chaiba",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#3b82f6"
        )
        chaiba_header.pack(pady=10)
        
        # chaiba info
        chaiba_info = ctk.CTkFrame(chaiba_frame, fg_color="#1e293b", corner_radius=10)
        chaiba_info.pack(fill="x", padx=10, pady=(0, 10))
        
        self.chaiba_pub_lbl = ctk.CTkLabel(
            chaiba_info,
            text="🔑 Clé publique : non générée",
            font=ctk.CTkFont(size=11),
            wraplength=350,
            justify="left"
        )
        self.chaiba_pub_lbl.pack(pady=8, padx=8)
        
        self.chaiba_recv_lbl = ctk.CTkLabel(
            chaiba_info,
            text="📩 Reçue de houdaifa : aucune",
            font=ctk.CTkFont(size=11),
            wraplength=350,
            justify="left"
        )
        self.chaiba_recv_lbl.pack(pady=8, padx=8)
        
        ctk.CTkButton(
            chaiba_frame,
            text="🔐 Générer mes clés",
            command=self._gen_chaiba_keys,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            height=35
        ).pack(pady=10, padx=10, fill="x")
        
        # chaiba input
        ctk.CTkLabel(
            chaiba_frame,
            text="✍️ Message à envoyer :",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.chaiba_input = ctk.CTkTextbox(chaiba_frame, height=80, corner_radius=10)
        self.chaiba_input.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(
            chaiba_frame,
            text="📤 Envoyer à houdaifa →",
            command=self._send_from_chaiba,
            fg_color="#10b981",
            hover_color="#059669",
            height=35
        ).pack(pady=10, padx=10, fill="x")
        
        # chaiba chat
        ctk.CTkLabel(
            chaiba_frame,
            text="💬 Conversation :",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.chaiba_chat = ctk.CTkTextbox(chaiba_frame, height=200, corner_radius=10)
        self.chaiba_chat.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        # ====== houdaifa SECTION ======
        houdaifa_frame = ctk.CTkFrame(users_frame, corner_radius=15, border_width=2, border_color="#10b981")
        houdaifa_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        houdaifa_header = ctk.CTkLabel(
            houdaifa_frame,
            text="👤 houdaifa",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#10b981"
        )
        houdaifa_header.pack(pady=10)
        
        # houdaifa info
        houdaifa_info = ctk.CTkFrame(houdaifa_frame, fg_color="#1e293b", corner_radius=10)
        houdaifa_info.pack(fill="x", padx=10, pady=(0, 10))
        
        self.houdaifa_pub_lbl = ctk.CTkLabel(
            houdaifa_info,
            text="🔑 Clé publique : non générée",
            font=ctk.CTkFont(size=11),
            wraplength=350,
            justify="left"
        )
        self.houdaifa_pub_lbl.pack(pady=8, padx=8)
        
        self.houdaifa_recv_lbl = ctk.CTkLabel(
            houdaifa_info,
            text="📩 Reçue d'chaiba : aucune",
            font=ctk.CTkFont(size=11),
            wraplength=350,
            justify="left"
        )
        self.houdaifa_recv_lbl.pack(pady=8, padx=8)
        
        ctk.CTkButton(
            houdaifa_frame,
            text="🔐 Générer mes clés",
            command=self._gen_houdaifa_keys,
            fg_color="#10b981",
            hover_color="#059669",
            height=35
        ).pack(pady=10, padx=10, fill="x")
        
        # houdaifa input
        ctk.CTkLabel(
            houdaifa_frame,
            text="✍️ Message à envoyer :",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.houdaifa_input = ctk.CTkTextbox(houdaifa_frame, height=80, corner_radius=10)
        self.houdaifa_input.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(
            houdaifa_frame,
            text="← 📤 Envoyer à chaiba",
            command=self._send_from_houdaifa,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            height=35
        ).pack(pady=10, padx=10, fill="x")
        
        # houdaifa chat
        ctk.CTkLabel(
            houdaifa_frame,
            text="💬 Conversation :",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.houdaifa_chat = ctk.CTkTextbox(houdaifa_frame, height=200, corner_radius=10)
        self.houdaifa_chat.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        # Exchange button at bottom
        exchange_frame = ctk.CTkFrame(tab, fg_color="transparent")
        exchange_frame.pack(fill="x", pady=15)
        
        ctk.CTkButton(
            exchange_frame,
            text="🔄 Échanger les clés publiques",
            command=self._exchange_public_keys_chat,
            fg_color="#8b5cf6",
            hover_color="#7c3aed",
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)
        
        # Transit log
        ctk.CTkLabel(
            tab,
            text="📡 Messages chiffrés en transit :",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=0, pady=(10, 5))
        
        self.transit_log = ctk.CTkTextbox(tab, height=100, corner_radius=10, fg_color="#0f172a")
        self.transit_log.pack(fill="x", pady=(0, 10))

    def on_operation_change(self):
        """Update labels when operation selection changes"""
        if self.operation_var.get() == "encrypt":
            self.process_button.configure(text="CHIFFRER")
            self.output_title.configure(text="Sortie chiffrée", text_color="#10b981")
        else:
            self.process_button.configure(text="DÉCHIFFRER")
            self.output_title.configure(text="Sortie déchiffrée", text_color="#3b82f6")
    
    def encrypt_text(self, plaintext, key):
        return encrypt_text(plaintext, key)
    
    def decrypt_text(self, ciphertext, key):
        try:
            return decrypt_text(ciphertext, key)
        except:
            raise Exception("Échec du déchiffrement : données ou clé invalide")
    
    def generate_ecdh_key(self):
        try:
            # Récupérer la taille choisie
            key_length = int(self.key_size_var.get())
            
            # Simule échange ECDH
            my_private, my_public = generate_keypair()
            
            # Pour démo : un autre participant fictif
            _, other_public = generate_keypair()
            
            shared = compute_shared_secret(my_private, other_public)
            
            # Dérive la clé avec la bonne longueur
            aes_key = derive_aes_key(shared, key_length_chars=key_length)
            
            # Insère dans le champ clé
            self.key_entry.delete(0, "end")
            self.key_entry.insert(0, aes_key)
            
            # Détermine le type AES
            aes_type = {32: "AES-128", 48: "AES-192", 64: "AES-256"}[key_length]
            
            messagebox.showinfo(
                "Success",
                f"Clé ECDH générée ({aes_type}) et insérée dans le champ clé !"
            )
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de la génération ECDH :\n{str(e)}")
    
    def process(self):
        """Process encryption or decryption"""
        # Get input values
        key = self.key_entry.get().strip()
        input_text = self.input_textbox.get("1.0", "end-1c").strip()
        
        # Validate inputs
        if not key:
            messagebox.showerror("Erreur de saisie", "Veuillez entrer une clé de chiffrement")
            return
        
        if not input_text:
            messagebox.showerror("Erreur de saisie", "Veuillez entrer le texte à traiter")
            return
        
        try:
            operation = self.operation_var.get()
            
            if operation == "encrypt":
                # Encrypt using your function - returns bytes
                result_bytes = self.encrypt_text(input_text, key)
                # Convert bytes to string for display (as hex or base64)
                result = result_bytes.hex()  # Display as hexadecimal
                # Alternative: result = base64.b64encode(result_bytes).decode()  # Display as base64
            else:
                # Decrypt using your function - returns bytes
                result_bytes = self.decrypt_text(input_text, key)
                # Convert bytes to string for display
                try:
                    result = result_bytes.decode('utf-8')  # Try to decode as UTF-8 text
                except:
                    result = result_bytes.hex()  # If not text, display as hex
            
            # Display output
            self.output_textbox.delete("1.0", "end")
            self.output_textbox.insert("1.0", result)
                
        except Exception as e:
            messagebox.showerror("Erreur de traitement", str(e))
    
    def copy_output(self):
        """Copy output to clipboard"""
        output = self.output_textbox.get("1.0", "end-1c").strip()
        if output:
            self.root.clipboard_clear()
            self.root.clipboard_append(output)
            messagebox.showinfo("Succès", "Sortie copiée dans le presse-papiers !")
        else:
            messagebox.showwarning("Attention", "Aucune sortie à copier")
    
    def clear_all(self):
        """Clear all input fields and results"""
        self.key_entry.delete(0, "end")
        self.input_textbox.delete("1.0", "end")
        self.output_textbox.delete("1.0", "end")
    
    # chat entre deux utlisateurs
    def _gen_chaiba_keys(self):
        self.chaiba_private, self.chaiba_public = generate_keypair()
        self.chaiba_pub_lbl.configure(text=f"🔑 Clé publique : x={self.chaiba_public.x} y={self.chaiba_public.y}")
        messagebox.showinfo("Succès", "Clés de chaiba générées !")
    
    def _gen_houdaifa_keys(self):
        self.houdaifa_private, self.houdaifa_public = generate_keypair()
        self.houdaifa_pub_lbl.configure(text=f"🔑 Clé publique : x={self.houdaifa_public.x} y={self.houdaifa_public.y}")
        messagebox.showinfo("Succès", "Clés d'houdaifa générées !")
    
    def _exchange_public_keys_chat(self):
        if not (self.chaiba_public and self.houdaifa_public):
            messagebox.showwarning("Attention", "Générez les clés des deux participants d'abord !")
            return
        
        self.chaiba_recv_lbl.configure(text=f"📩 Reçue d'houdaifa : x={self.houdaifa_public.x} y={self.houdaifa_public.y}")
        
        self.houdaifa_recv_lbl.configure(text=f"📩 Reçue de chaiba : x={self.chaiba_public.x} y={self.chaiba_public.y}")
        
        self._log_transit("🔄 Clés publiques échangées (visibles par tous)")
        messagebox.showinfo("Succès", "Clés publiques échangées avec succès !")
    
    def _send_from_chaiba(self):
        if not (self.chaiba_private and self.houdaifa_public):
            messagebox.showwarning("Erreur", "Échangez d'abord les clés publiques !")
            return
        
        msg = self.chaiba_input.get("1.0", "end-1c").strip()
        if not msg:
            messagebox.showwarning("Attention", "Entrez un message à envoyer !")
            return
        
        try:
            shared = compute_shared_secret(self.chaiba_private, self.houdaifa_public)
            key_len = int(self.key_size_var.get())
            aes_key = derive_aes_key(shared, key_length_chars=key_len)
            
            ct = encrypt_text(msg, aes_key)
            ct_hex = ct.hex().upper()
            
            preview = ct_hex[:60] + "..." if len(ct_hex) > 60 else ct_hex
            self._log_transit(f"📤 chaiba → houdaifa (chiffré) : {preview}")
            
            dec = decrypt_text(ct_hex, aes_key).decode('utf-8')
            self.houdaifa_chat.insert("end", f"💬 chaiba : {dec}\n\n")
            self.houdaifa_chat.see("end")
            
            self.chaiba_chat.insert("end", f"✅ Moi : {msg}\n\n")
            self.chaiba_chat.see("end")
            self.chaiba_input.delete("1.0", "end")
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec envoi : {str(e)}")
    
    def _send_from_houdaifa(self):
        if not (self.houdaifa_private and self.chaiba_public):
            messagebox.showwarning("Erreur", "Échangez d'abord les clés publiques !")
            return
        
        msg = self.houdaifa_input.get("1.0", "end-1c").strip()
        if not msg:
            messagebox.showwarning("Attention", "Entrez un message à envoyer !")
            return
        
        try:
            shared = compute_shared_secret(self.houdaifa_private, self.chaiba_public)
            key_len = int(self.key_size_var.get())
            aes_key = derive_aes_key(shared, key_length_chars=key_len)
            
            ct = encrypt_text(msg, aes_key)
            ct_hex = ct.hex().upper()
            
            preview = ct_hex[:60] + "..." if len(ct_hex) > 60 else ct_hex
            self._log_transit(f"📤 houdaifa → chaiba (chiffré) : {preview}")
            
            dec = decrypt_text(ct_hex, aes_key).decode('utf-8')
            self.chaiba_chat.insert("end", f"💬 houdaifa : {dec}\n\n")
            self.chaiba_chat.see("end")
            
            self.houdaifa_chat.insert("end", f"✅ Moi : {msg}\n\n")
            self.houdaifa_chat.see("end")
            self.houdaifa_input.delete("1.0", "end")
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec envoi : {str(e)}")
    
    def _log_transit(self, msg: str):
        self.transit_log.insert("end", msg + "\n")
        self.transit_log.see("end")
    
def main():
    # Create root window
    root = ctk.CTk()
    
    # Create application
    app = ModernAESCryptoApp(root)
    
    # Run application
    root.mainloop()


if __name__ == "__main__":
    main()