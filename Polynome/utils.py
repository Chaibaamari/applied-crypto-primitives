import re

def valider_syntax(poly_str: str):
    terms = re.findall(r'([+-]?[^+-]+)', poly_str.replace(" ", ""))
    for term in terms:
        if term.count('x') > 1:
            raise ValueError(f"Too many 'x' in term '{term}'")
        if term.count('^') > 1:
            raise ValueError(f"Too many '^' in term '{term}'")
        if '^' in term:
            exp = term.split('^')[1]
            if not exp.isdigit():
                raise ValueError(f"Invalid exponent '{exp}' in term '{term}'")
    return True

def valider_caracteres(poly_str: str):
    """
    Validates that the polynomial contains only digits, x, +, -, ^, and spaces.
    Raises ValueError if invalid characters are found, highlighting them.
    """
    allowed_chars = "0123456789xX+-^ "
    for i, char in enumerate(poly_str):
        if char not in allowed_chars:
            raise ValueError(f"Invalid character '{char}' at position {i+1}")
    return True

def polynome_to_vecteur(poly_str: str):
    """
    Convert a polynomial string like 'x^3 + 2x^2 - x + 5'
    into a list of coefficients [1, 2, -1, 5].
    """

    try:
        poly_str = poly_str.replace(" ", "").lower()  # remove spaces
        # Find all terms using regex
        term_pattern = r'([+-]?[^+-]+)'
        terms = re.findall(term_pattern, poly_str)
        
        
        # Determine the degree
        degree = 0
        for term in terms:
            if 'x^' in term:
                d = int(term.split('x^')[1])
                degree = max(degree, d)
            elif 'x' in term and '^' not in term:
                degree = max(degree, 1)

        # Initialize coefficient vector
        coeffs = [0]*(degree+1)

        # Fill coefficients
        for term in terms:
            if 'x^' in term:
                c, d = term.split('x^')
                c = c if c not in ('', '+', '-') else c+'1'
                coeffs[int(d)] += int(c)
            elif 'x' in term:
                c = term.replace('x', '')
                c = c if c not in ('', '+', '-') else c+'1'
                coeffs[1] += int(c)
            else:
                coeffs[0] += int(term)
        
        # Return in descending degree order
        return coeffs
    
    except Exception as e:
        print(e)

def valider_polynome(poly_str: str):
    # valider la chaîne de caractères en entrées
    valider_caracteres(poly_str)
    valider_syntax(poly_str)

    return polynome_to_vecteur(poly_str)

def calculer_degre_polynome(vecteur: list[int]):
    for i in range(len(vecteur) - 1, -1, -1):

        if (vecteur[i]) != 0:
            return i
        
    return 0

def fomatter_vecteur(vecteur: list[int], degre: int) -> list[int]:

    if len(vecteur) < degre:
        raise ValueError(f"La taille du vecteur doit être supérieure ou égale au degré")
    
    v = [0]*(degre+1)
    for i in range(degre, -1, -1):
        v[i] = vecteur[i]

    return v

# calcul l'inverse d'un nombre dans Z/pZ
def inv_zp(a, p):
    if a % p == 0:
        raise ValueError(f"{a} n'a pas d'inverse dans Z/pZ")
    return pow(a, p - 2, p)

# calcul le mod d'un nombre
def mod_zp(a, p) -> int:
    if p <= 0:
        raise ValueError(f"{p} doit être positif")
    return a % p


def appliquer_mod_sur_vec(vecteur: list[int], degre: int, mod: int):

    for i in range(0, degre + 1):
        vecteur[i] = mod_zp(vecteur[i], mod)

    degre = calculer_degre_polynome(vecteur)
    return fomatter_vecteur(vecteur, degre)