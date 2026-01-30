import random
import math
import array as arr


# PGCD function
def pgcd(a, b):
    if b == 0:
        return a 
    else:
        return pgcd(b, a % b)

def puissanceParfait(n):
    """Checks if number is a power of another integer, 
        if it returns true, then it is composite.
    """
    for b in range(2,int(math.log2(n))+1):       
        a=n**(1/b)
        if a-int(a) == 0:    
            return(True)    
    return(False)


# --------------------------------------------------
# Étape 2 AKS : Recherche du paramètre r
# --------------------------------------------------
# Cette fonction cherche le plus petit entier r tel que
# l'ordre multiplicatif de n modulo r soit STRICTEMENT
# supérieur à (log2(n))^2.
#
# Intuition :
# - Si n est premier → ses puissances modulo r ont un bon comportement
# - Si n est composé → les puissances "retombent" trop vite sur 1
# --------------------------------------------------
def trouver_r(n):
    """
    Trouve le plus petit entier r tel que
    l'ordre multiplicatif de n modulo r > (log2(n))^2
    """
    max_k = math.log2(n) ** 2   # borne théorique sur k
    r = 1
    continuer = True

    while continuer:
        r += 1
        continuer = False
        k = 0

        # On vérifie si n^k ≡ 1 (mod r) trop rapidement
        while k <= max_k and not continuer:
            k += 1
            reste = exponentiation_modulaire_rapide(n, k, r)
            if reste == 0 or reste == 1:
                continuer = True

    return r

# --------------------------------------------------
# Exponentiation modulaire rapide
# --------------------------------------------------
# Calcule : base^puissance mod n
# de manière efficace (méthode binaire)
# --------------------------------------------------
def exponentiation_modulaire_rapide(base, puissance, n):
    """
    Calcule (base^puissance) mod n efficacement
    """
    resultat = 1

    while puissance > 0:
        if puissance % 2 == 1:
            resultat = (resultat * base) % n
        base = (base * base) % n
        puissance = puissance // 2

    return resultat

# --------------------------------------------------
# Étape 5 AKS : Exponentiation polynomiale rapide
# --------------------------------------------------
# Cette fonction calcule :
# (x + a)^n - x^n - a   mod (x^r - 1, n)
#
# Si le résultat est le polynôme nul → test réussi
# --------------------------------------------------
def exponentiation_polynomiale_rapide(polynome_base, puissance, r):
    """
    Élève un polynôme à une grande puissance modulo (x^r - 1, n)
    """
    x = arr.array('d', [])
    a = polynome_base[0]   # coefficient constant

    # Initialisation du polynôme unité
    for _ in range(len(polynome_base)):
        x.append(0)
    x[0] = 1

    n = puissance

    while puissance > 0:
        if puissance % 2 == 1:
            x = multiplication_polynomiale(x, polynome_base, n, r)
        polynome_base = multiplication_polynomiale(polynome_base, polynome_base, n, r)
        puissance = puissance // 2

    # Soustraction de x^n + a
    x[0] -= a
    x[n % r] -= 1

    return x


# --------------------------------------------------
# Multiplication polynomiale modulo (x^r - 1, n)
# --------------------------------------------------
def multiplication_polynomiale(p1, p2, n, r):
    """
    Multiplie deux polynômes modulo (x^r - 1, n)
    """
    resultat = arr.array('d', [])

    for _ in range(len(p1) + len(p2) - 1):
        resultat.append(0)

    for i in range(len(p1)):
        for j in range(len(p2)):
            resultat[(i + j) % r] += p1[i] * p2[j]
            resultat[(i + j) % r] %= n

    # On tronque le polynôme à degré < r
    while len(resultat) > r:
        resultat = resultat[:-1]

    return resultat


# --------------------------------------------------
# Fonction indicatrice d'Euler φ(r)
# --------------------------------------------------
# Calcule le nombre d'entiers ≤ r premiers avec r
# --------------------------------------------------
def fonction_phi_euler(r):
    """
    Calcule la fonction indicatrice d'Euler φ(r)
    """
    compteur = 0
    for i in range(1, r + 1):
        if pgcd(r, i) == 1:
            compteur += 1
    return compteur


def miller_robin(n,k):
    # Étape 1 : gérer les cas particuliers
    if n < 4:
        return True  # 2 et 3 sont premiers
        # return "Le nombre est premier"  # 2 et 3 sont premiers

    if n % 2 == 0:
        return False
        # return "Le nombre est composé"

    # Trouver k et m tels que n-1 = 2^k * m avec m impair
    m = n - 1
    k = 0
    while m % 2 == 0:
        k += 1
        m //= 2
    
    for _ in range(k):
    # Etape 2 : choisir un a aléatoirement dans [2, n-2]  si a = n - 1 = -1 [n] n'apporte rien
        a = random.randrange(2, n - 1)
    # Etape 3 : calculer b = a^m mod n
        b = pow(a, m, n)
        if b == 1 or b == n - 1:
            continue #"Le nombre est probablement premier"
        for i in range(k):
            b = pow(b, 2, n)
            if b == n - 1:  # le modulo ne donne jamais de négatif pour le résultat.
                break
        else:
            return False #"Le nombre est composé"
    return True #"Le nombre est probablement premier"

# fermat primality test

def fermat(n, k):
    
    # Étape 1 : gérer les cas particuliers
    if n < 4:
        return True # 2 et 3 sont premiers
    if n % 2 == 0:
        return False # les nombres pairs sont composés
    
    for _ in range(k):
        # choisir un a aléatoirement dans [2, n-2]
        a = random.randrange(2, n - 1)
        # calculer a^(n-1) mod n
        return pow(a, n - 1, n) == 1

# calcul de symbole de Jacobi
def symbole_jacobi(a, n):
    if n <= 0 or n % 2 == 0:
        return 0

    a = a % n
    result = 1

    while a != 0:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5):
                result = -result
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            result = -result
        a %= n

    return result if n == 1 else 0

# function solovay strassen
def solovay_strassen(n, k):
    
    # Étape 1 : gérer les cas particuliers
    if n < 4:
        return True

    if n % 2 == 0:
        return False

    for _ in range(k):
        # choisir un entier aleatoire k dans [1, n-1]
        a = random.randrange(2, n - 1)
        # tester le pgcd 
        result = pgcd(n, a)
        if result > 1:
            return False
    
        # calculer le symbole de Jacobi
        symbole = symbole_jacobi(a, n)
        # calculer d'euler function mod n
        euler = pow(a, (n - 1) // 2, n)
        if euler != symbole % n:
            return False
    return True

""" AKS primality test
"""
def aks(n):
    """ The main AKS algorithm
    """
    if puissanceParfait(n) == True:                 #step 1
        return False
    
    r = trouver_r(n)                                #step 2

    for a in range(2,min(r,n)):                     #step 3
        if math.gcd(a,n) > 1:                       
            return False

    if n <= r:                                      #step 4
        return True

    x = arr.array('l',[],)                          #step 5
    for a in range(1,math.floor((fonction_phi_euler(r))**(1/2)*math.log2(n))):      
        x = exponentiation_polynomiale_rapide(arr.array('l',[a,1]),n,r)
        if  any(x):
            return False
    return True                                     #step 6


if __name__ == "__main__":
    n = 561
    k = 10
    print("Miller-Robin:", miller_robin(n, k))
    print("Fermat:", fermat(n, k))
    print("Solovay-Strassen:", solovay_strassen(n, k))
    print("AKS:", aks(n))



