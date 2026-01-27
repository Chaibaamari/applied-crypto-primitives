import random
from utils import derive_aes_key
from encryption import encrypt_text
from decryption import decrypt_text


# définition de la courbe elliptique y^2 = x^3 + ax + b  mode [p] sur GF(p)  
class EllipticCurve:
    def __init__(self, p, a, b):
        self.p = p
        self.a = a
        self.b = b

# Représente un point sur la courbe elliptique
class Point:
    def __init__(self, ec, x, y):
        self.ec = ec
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return self.ec.p == other.ec.p and self.x == other.x and self.y == other.y

    def is_inf(self):
        return self.x is None and self.y is None

# Retourne le point neutre du groupe
def inf_point(ec):
    return Point(ec, None, None)

# Addition de deux points sur la courbe elliptique
# P et Q sont des objets Point
# P + Q
def add_points(P, Q):
    if P.is_inf():
        return Q
    if Q.is_inf():
        return P
    p = P.ec.p
    if P.x == Q.x and P.y == (p - Q.y) % p:
        return inf_point(P.ec)
    if P == Q:
        if P.y == 0:
            return inf_point(P.ec)
        lam = (3 * (P.x ** 2) + P.ec.a) * pow(2 * P.y, p - 2, p) % p
    else:
        lam = (Q.y - P.y) * pow(Q.x - P.x, p - 2, p) % p
    x3 = (lam ** 2 - P.x - Q.x) % p
    y3 = (lam * (P.x - x3) - P.y) % p
    return Point(P.ec, x3, y3)

# Utilisé pour générer des clés et calculer le secret partagé en ECDH
def scalar_mul(k, P):
    if k == 0:
        return inf_point(P.ec)
    res = inf_point(P.ec)
    addend = P
    while k:
        if k & 1:
            res = add_points(res, addend)
        addend = add_points(addend, addend)
        k >>= 1
    return res

# Paramètres de la courbe (fixés pour GF(17), y² = x³ + x + 1)
p = 17   # corps fini GF(17) (les valeurs x et y sont modulo 17).
a = 1
b = 1
ec = EllipticCurve(p, a, b)
G = Point(ec, 0, 1)  # Point base (générateur d'ordre 18) utilisé pour générer des clés.
n = 18  # Ordre du groupe

def generate_keypair():
    """
    Génère une paire de clés ECDH (privée, publique).
    """
    private = random.randint(1, n - 1)
    public = scalar_mul(private, G)
    return private, public

def compute_shared_secret(private, other_public):
    """
    Calcule le secret partagé.
    """
    shared = scalar_mul(private, other_public)
    if shared.is_inf():
        raise ValueError("Secret partagé invalide")
    return shared

# # Exemple ECDH (simule Alice et Bob)
# alice_private, alice_public = generate_keypair()
# bob_private, bob_public = generate_keypair()

# alice_shared = compute_shared_secret(alice_private, bob_public)
# bob_shared = compute_shared_secret(bob_private, alice_public)

# # Vérifiez que c'est le même
# assert alice_shared.x == bob_shared.x and alice_shared.y == bob_shared.y

# # Dérivez la clé AES (e.g., pour 128 bits)
# aes_key = derive_aes_key(alice_shared, key_length=32)
# print("Clé AES partagée via ECDH :", aes_key)

# # Testez avec votre AES
# text = "Hello world!"
# encoded = encrypt_text(text, aes_key)
# print("Chiffré :", encoded.hex())

# decoded = decrypt_text(encoded.hex(), aes_key)
# print("Déchiffré :", decoded.decode('utf-8'))