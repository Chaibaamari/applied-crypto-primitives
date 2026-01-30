import random

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

# PGCD function
def pgcd(a, b):
    if b == 0:
        return a 
    else:
        return pgcd(b, a % b)

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



