# ========= Field definition =========
IRREDUCIBLE_POLY = 0x12D  # x^8 + x^5 + x^3 + x^2 + 1

def gf_mult(a, b):
    res = 0
    for _ in range(8):
        if b & 1:
            res ^= a
        carry = a & 0x80
        a = (a << 1) & 0xFF
        if carry:
            a ^= IRREDUCIBLE_POLY & 0xFF
        b >>= 1
    return res

def gf_pow(a, p):
    r = 1
    for _ in range(p):
        r = gf_mult(r, a)
    return r

def gf_inverse(a):
    if a == 0:
        return 0
    return gf_pow(a, 254)

# ========= Affine / polynomial transform =========
def affine_transform(x):
    c = 0x63
    y = 0
    for i in range(8):
        bit = (
            ((x >> i) & 1) ^
            ((x >> ((i + 4) % 8)) & 1) ^
            ((x >> ((i + 5) % 8)) & 1) ^
            ((x >> ((i + 6) % 8)) & 1) ^
            ((x >> ((i + 7) % 8)) & 1) ^
            ((c >> i) & 1)
        )
        y |= bit << i
    return y

# ========= S-box generation =========
def generate_sbox():
    return [affine_transform(gf_inverse(x)) for x in range(256)]

def generate_inverse_sbox(sbox):
    inv = [0] * 256
    for i, v in enumerate(sbox):
        inv[v] = i
    return inv

# ========= Pretty printing =========
def print_sbox(name, box):
    print(f"{name} = [")
    for i in range(0, 256, 8):
        row = ", ".join(f"0x{b:02x}" for b in box[i:i+8])
        print(f"    {row},")
    print("]\n")

# ========= Run =========
s_box = generate_sbox()
inv_s_box = generate_inverse_sbox(s_box)

print_sbox("s_box", s_box)
print_sbox("inv_s_box", inv_s_box)