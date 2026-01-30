from __future__ import annotations
from utils import mod_zp, calculer_degre_polynome, fomatter_vecteur, inv_zp, polynome_to_vecteur, appliquer_mod_sur_vec

class Polynome:
    
    def __init__(self, vecteur_init: list[int]):
        self.degre = calculer_degre_polynome(vecteur_init)
        self.vecteur = fomatter_vecteur(vecteur_init, self.degre)

    # vérifier si le polynôme actuel est le pôlynome 0
    def est_nil(self) -> bool:
        for i in range(0, self.degre + 1):
            if self.vecteur[i] != 0:
                return False
            
        return True
    
    # normalise le polynôme dans Z/pZ
    # applique le mod sur tous les éléments du polynôme
    def appliquer_mod(self, mod: int):

        for i in range(0, self.degre + 1):
            self.vecteur[i] = mod_zp(self.vecteur[i], mod)

        self.degre = calculer_degre_polynome(self.vecteur)
        self.vecteur = fomatter_vecteur(self.vecteur, self.degre)
        
    # cette méthode divise le polynome sur un autre, elle retourne un quotient "q" et un reste "r"
    # tels que p = poly_diviseur * q + r
    def diviser(self, poly_diviseur: Polynome, mod: int = 100) -> tuple[Polynome, Polynome]:
        # le degré du polynôme 'poly_diviseur' est supérieure au polynôme actuel
        if poly_diviseur.degre > self.degre:
            return Polynome([0]), self
        
        if poly_diviseur.est_nil():
            raise Exception("On ne peut diviser sur le polynôme 0")
        
        # normaliser les polynômes dans Z/pZ
        self.appliquer_mod(mod)
        poly_diviseur.appliquer_mod(mod)

        # déterminer le degré du quotient
        degre_quotient = self.degre - poly_diviseur.degre
        # if self.vecteur[-1] % poly_diviseur.vecteur[-1] != 0:
        #     raise Exception(f"Les polynomes {self} et {poly_diviseur} ne sont pas divisables sur Z")
        
        # calculer le quotient
        quotient = [0]*(degre_quotient + 1)

        # in Z/pZ
        inverse_coef_poly_diviseur = inv_zp(poly_diviseur.vecteur[-1], mod)
        coef_quotient = (inverse_coef_poly_diviseur * self.vecteur[-1]) % mod

        # coef_quotient = int(self.vecteur[-1] / poly_diviseur.vecteur[-1])
        quotient[-1] = coef_quotient

        temp = [0]*(self.degre + 1) # ce vecteur stocke le résultat de poly_diviseur * quotient pour déterminer le reste
        for i in range(0, poly_diviseur.degre + 1):
            temp[i + degre_quotient] = poly_diviseur.vecteur[i] * coef_quotient

        temp = appliquer_mod_sur_vec(temp, self.degre, mod)

        reste = [0] * (self.degre + 1)
        for i in range(0, self.degre + 1):
            reste[i] = self.vecteur[i] - temp[i]
        
        poly_quotient = Polynome(quotient)
        poly_reste = Polynome(reste)

        poly_quotient.appliquer_mod(mod)
        poly_reste.appliquer_mod(mod)

        # min_degre = min(poly_quotient.degre, poly_diviseur.degre)
        # si le degré du reste est inférieure au degré du 'poly_diviseur' alors on a trouvé le bon quotient et le bon reste
        if poly_diviseur.degre > poly_reste.degre:
            return poly_quotient, poly_reste
        
        # si le degré du reste est égale au degré du 'poly_diviseur'
        # cela veut dire qu'il a une nouvelle itération
        # exception: le reste est 0
        if poly_quotient.degre == 0 and poly_reste.degre == 0:
            if poly_reste.vecteur[0] == 0:
                return poly_quotient, poly_reste

        # la prochaine itération
        poly_quotient_suivant, poly_reste_suivant = poly_reste.diviser(poly_diviseur, mod)
        return poly_quotient.additionner(poly_quotient_suivant, mod), poly_reste_suivant # en additionne le quotient actuel avec ceux des itérations qui viennent après
        
    # cette méthode additionne deux polynômes: le polyôme actuel et 'poly'
    def additionner(self, poly: Polynome, mod: int) -> Polynome:
        degre_max = max(poly.degre, self.degre)
        degre_min = min(poly.degre, self.degre)
        resultat = [0]*(degre_max + 1)

        for i in range(0, degre_min + 1):
            resultat[i] = poly.vecteur[i] + self.vecteur[i]

        for i in range(degre_min + 1, degre_max + 1):
            resultat[i] = poly.vecteur[i] if poly.degre == degre_max else self.vecteur[i]

        add = Polynome(resultat)
        add.appliquer_mod(mod)
        return add
    
    def soustraire(self, poly: Polynome, mod: int) -> Polynome:
        degre_max = max(poly.degre, self.degre)
        degre_min = min(poly.degre, self.degre)
        resultat = [0]*(degre_max + 1)

        for i in range(0, degre_min + 1):
            resultat[i] = self.vecteur[i] - poly.vecteur[i]

        for i in range(degre_min + 1, degre_max + 1):
            resultat[i] = -poly.vecteur[i] if poly.degre == degre_max else self.vecteur[i]

        sous = Polynome(resultat)
        sous.appliquer_mod(mod)
        return sous
    
    def multiplier(self, poly: Polynome, mod) -> Polynome:
        degre = self.degre + poly.degre
        result = [0]*(degre + 1)

        for i in range(0, self.degre + 1):
            for j in range(0, poly.degre + 1):
                result[i + j] += self.vecteur[i] * poly.vecteur[j]

        mul = Polynome(result)
        mul.appliquer_mod(mod)
        return mul
    
    def __eq__(self, value: Polynome):
        if not isinstance(value, Polynome):
            raise TypeError("On ne peut pas comparer un polynôme avec une autre instance")
        
        if value.degre != self.degre:
            return False
        
        for i in range(0, self.degre + 1):
            if self.vecteur[i] != value.vecteur[i]:
                return False
                
        return True

    def __lt__(self, value: Polynome):
        if not isinstance(value, Polynome):
            raise TypeError("On ne peut pas comparer un polynôme avec une autre instance")

        if value.degre > self.degre:
            return True
        
        if value.degre < self.degre:
            return False
        
        for i in range(0, self.degre + 1):
            if value.vecteur[i] > self.vecteur[i]:
                return True
            
            if value.vecteur[i] < self.vecteur[i]:
                return False
                
        return False
    
    def __gt__(self, value: Polynome):
        if not isinstance(value, Polynome):
            raise TypeError("On ne peut pas comparer un polynôme avec une autre instance")

        if self.degre > value.degre:
            return True
        
        if self.degre < value.degre:
            return False
        
        for i in range(0, self.degre + 1):
            if value.vecteur[i] < self.vecteur[i]:
                return True
            
            if value.vecteur[i] > self.vecteur[i]:
                return False
                
        return False
    
    def __str__(self):

        # il y a un seul terme. Par exemple les polynômes: 5, 3, 8, ...
        if self.degre == 0:
            return f"{self.vecteur[0]}"
        
        s = ""
        coef = self.vecteur[-1]

        if self.degre > 0:
            if coef == 1:
                s = f"x^{self.degre}" if self.degre != 1 else "x"

            elif coef == -1:
                s = f"- x^{self.degre}" if self.degre != 1 else "x"

            elif coef < 0:
                s = f"- {abs(coef)}{f"x^{self.degre}" if self.degre != 1 else "x"}"
            
            elif coef > 0:
                s = f"{coef}{f"x^{self.degre}" if self.degre != 1 else "x"}"

        for i in range(self.degre-1, 0, -1):
            coef = self.vecteur[i]
            if coef == 0:
                continue
            s += f" {"+" if coef > 0 else "-"} {f"{abs(coef) if coef != 1 and coef != -1 else ""}"}{f"x^{i}" if i != 1 else "x"}"

        coef = self.vecteur[0]
        
        if coef < 0:
            s += f" - {abs(coef)}"
        elif coef > 0:
            s += f" + {coef}"

        return s.replace("  ", " ").strip()
    
    def normaliser(self, mod):
        lc = self.vecteur[-1] % mod
        inv_lc = pow(lc, -1, mod)  # inverse mod p
        vec = [(c * inv_lc) % mod for c in self.vecteur]

        return Polynome(vec)

def PGCD(poly_a: Polynome, poly_b: Polynome, mod: int):
    demonstration = []

    poly_max = max(poly_a, poly_b)
    poly_min = min(poly_a, poly_b)

    if poly_min.est_nil():
        return poly_min, [f"{poly_max} = ({poly_min}) * ({poly_q}) + ({poly_r})"]
    
    (poly_q, poly_r) = poly_max.diviser(poly_min, mod)
    demonstration.append(f"{poly_max} = ({poly_min}) * ({poly_q}) + ({poly_r})")

    if not isinstance(poly_q, Polynome) or not isinstance(poly_r, Polynome):
        raise Exception("Erreur inconnue!")
    
    while not poly_r.est_nil():
        poly_max = max(poly_min, poly_r)
        poly_min = min(poly_min, poly_r)

        (poly_q, poly_r) = poly_max.diviser(poly_min, mod)
        demonstration.append(f"{poly_max} = ({poly_min}) * ({poly_q}) + ({poly_r})")

    return poly_min, demonstration

def inverse(poly_a: Polynome, poly_b: Polynome, mod: int) -> tuple[Polynome, Polynome]:
    
    if poly_a.est_nil():
        return Polynome([0]), Polynome([1])
    
    pgcd = PGCD(poly_a, poly_b, mod)[0]

    if len(pgcd.vecteur) > 1:
        raise Exception(f"Le polynome {poly_a} n'a pas d'inverse sur {poly_b} car PGCD({poly_a}, {poly_b}) = {pgcd}")
    
    q, r = poly_b.diviser(poly_a, mod)
    if r.est_nil():
        q.vecteur[0] = 0

    x1, y1 = inverse(r, poly_a, mod)

    x = y1.soustraire(
        q.multiplier(
            x1, 
            mod
        ), 
        mod
    )
    y = x1
    
    return x, y