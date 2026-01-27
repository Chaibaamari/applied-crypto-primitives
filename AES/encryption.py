from utils import key_expansion_layer, s_box, key_addition_layer, string_to_aes_blocks, gf_mul, poly

def substitution_layer(block: bytes):
    """
    Applique la substitution (SubBytes) sur un bloc de 16 octets
    """
    if len(block) != 16:
        raise Exception("Le bloc doit contenir 16 octets")
    
    return bytes(s_box[b] for b in block)

def shift_rows_layer(block: bytes) -> bytes:
    """
    Applique le décalage de lignes (ShiftRows) sur un bloc de 16 octets
    """
    if len(block) != 16:
        raise ValueError("Le bloc doit contenir 16 octets")

    # Extraire les lignes (ordre colonne-major)
    row0 = [block[0], block[4], block[8], block[12]]
    row1 = [block[1], block[5], block[9], block[13]]
    row2 = [block[2], block[6], block[10], block[14]]
    row3 = [block[3], block[7], block[11], block[15]]

    # Fonction pour faire une rotation à gauche
    def rotate_left(lst, n):
        return lst[n:] + lst[:n]

    # Appliquer la rotation pour chaque ligne
    row0 = rotate_left(row0, 0)  # pas de décalage
    row1 = rotate_left(row1, 1)  # décalage de 1
    row2 = rotate_left(row2, 2)  # décalage de 2
    row3 = rotate_left(row3, 3)  # décalage de 3

    # Reconstituer le bloc en ordre colonne-major
    new_block = []
    for i in range(4):
        new_block.append(row0[i])
        new_block.append(row1[i])
        new_block.append(row2[i])
        new_block.append(row3[i])

    return bytes(new_block)

def mix_single_column(col: list[int], poly: int) -> list[int]:
    """
    Applique MixColumns sur une colonne de 4 octets
    """
    a0, a1, a2, a3 = col
    return [
        gf_mul(a0, 2, poly) ^ gf_mul(a1, 3, poly) ^ a2 ^ a3,
        a0 ^ gf_mul(a1, 2, poly) ^ gf_mul(a2, 3, poly) ^ a3,
        a0 ^ a1 ^ gf_mul(a2, 2, poly) ^ gf_mul(a3, 3, poly),
        gf_mul(a0, 3, poly) ^ a1 ^ a2 ^ gf_mul(a3, 2, poly),
    ]

def mix_columns_layer(block: bytes) -> bytes:
    """
    Applique MixColumns sur un bloc de 16 octets
    """
    if len(block) != 16:
        raise ValueError("Le bloc doit contenir 16 octets")

    mixed = []

    # Traiter chaque colonne
    for c in range(4):
        column = [
            block[c * 4 + 0],
            block[c * 4 + 1],
            block[c * 4 + 2],
            block[c * 4 + 3],
        ]

        mixed_col = mix_single_column(column, poly)
        mixed.extend(mixed_col)

    return bytes(mixed)

def build_round_keys(words: list[bytes], nb: int = 4) -> list[bytes]:
    """
    Construit les clés de tour à partir des mots de la clé étendue
    """
    if len(words) % nb != 0:
        raise ValueError("Longueur de clé étendue invalide")

    round_keys = []

    # Regrouper les mots par 4 pour former les clés de 16 octets
    for i in range(0, len(words), nb):
        round_key = b''.join(words[i:i + nb])
        round_keys.append(round_key)

    return round_keys

def last_transformation(block: bytes, round_key: bytes):
    """
    Dernier tour AES : SubBytes -> ShiftRows -> AddRoundKey
    """
    subbed_block = substitution_layer(block)
    shifted = shift_rows_layer(subbed_block)
    added_key_block = key_addition_layer(shifted, round_key)

    return added_key_block

def encrypt_block(block: bytes, round_words: list[bytes]):
    """
    Chiffre un bloc de 16 octets avec la clé étendue
    """
    rounds_number = int(len(round_words) / 4)
    round_keys = build_round_keys(round_words)

    # Transformation initiale (AddRoundKey)
    added_key_block = key_addition_layer(block, round_keys[0])    
    
    # Boucle sur les tours intermédiaires
    for i in range(1, rounds_number - 1):
        subbed_block = substitution_layer(added_key_block)
        shifted = shift_rows_layer(subbed_block)
        mixed = mix_columns_layer(shifted)
        added_key_block = key_addition_layer(mixed, round_keys[i])

    # Dernier tour
    result_block = last_transformation(added_key_block, round_keys[-1])
    return result_block

def encrypt_text(text: str, key: str) -> bytes:
    """
    Chiffre un texte AES en blocs de 16 octets avec une clé hexadécimale
    """
    blocks = string_to_aes_blocks(text)
    round_words = key_expansion_layer(key)

    # Chiffrement bloc par bloc
    return b''.join(
        encrypt_block(block, round_words)
        for block in blocks
    )

text = "Hello world!"
key = "313233343536373839313233343536373931323334353637"
# 3132333435363738
# 3931323334353637

encoded = encrypt_text(text, key)

# print(encoded.hex())