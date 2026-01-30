from utils import key_expansion_layer, inv_s_box, key_addition_layer, gf_mul, poly

def build_round_keys(words: list[bytes], nb: int = 4) -> list[bytes]:
    """
    Construit les clés de chaque tour à partir des mots de la clé étendue.

    :param words: mots de la clé étendue (longueur 44, 52 ou 60)
    :param nb: nombre de mots par clé de tour (AES = 4)
    :return: liste des clés de tour (bytes)
    """
    if len(words) % nb != 0:
        raise ValueError("Longueur de clé étendue invalide")

    round_keys = []

    # Construire chaque clé de 16 octets (4 mots)
    for i in range(0, len(words), nb):
        round_key = b''.join(words[i:i + nb])
        round_keys.append(round_key)

    return round_keys

def inverse_mix_single_column(col: list[int], poly: int) -> list[int]:
    """
    Applique l'inverse de MixColumns sur une colonne (4 octets)
    """
    a0, a1, a2, a3 = col
    return [
        gf_mul(a0, 14, poly) ^ gf_mul(a1, 11, poly) ^ gf_mul(a2, 13, poly) ^ gf_mul(a3, 9, poly),
        gf_mul(a0, 9, poly)  ^ gf_mul(a1, 14, poly) ^ gf_mul(a2, 11, poly) ^ gf_mul(a3, 13, poly),
        gf_mul(a0, 13, poly) ^ gf_mul(a1, 9, poly)  ^ gf_mul(a2, 14, poly) ^ gf_mul(a3, 11, poly),
        gf_mul(a0, 11, poly) ^ gf_mul(a1, 13, poly) ^ gf_mul(a2, 9, poly)  ^ gf_mul(a3, 14, poly),
    ]

def inverse_substitution_layer(block: bytes) -> bytes:
    """
    Applique l'inverse de la substitution (InvSubBytes) sur un bloc de 16 octets
    """
    if len(block) != 16:
        raise Exception("Le bloc doit contenir 16 octets")
    
    return bytes(inv_s_box[b] for b in block)

def inverse_shift_rows_layer(block: bytes) -> bytes:
    """
    Applique l'inverse du décalage de lignes (InvShiftRows) sur un bloc de 16 octets
    """
    if len(block) != 16:
        raise ValueError("Le bloc doit contenir 16 octets")

    # Extraire les lignes (ordre colonne-major)
    row0 = [block[0], block[4], block[8], block[12]]
    row1 = [block[1], block[5], block[9], block[13]]
    row2 = [block[2], block[6], block[10], block[14]]
    row3 = [block[3], block[7], block[11], block[15]]

    # Fonction pour faire une rotation à droite
    def rotate_right(lst, n):
        return lst[-n:] + lst[:-n] if n != 0 else lst

    # Appliquer la rotation inverse
    row0 = rotate_right(row0, 0)
    row1 = rotate_right(row1, 1)
    row2 = rotate_right(row2, 2)
    row3 = rotate_right(row3, 3)

    # Reconstituer le bloc en ordre colonne-major
    new_block = []
    for i in range(4):
        new_block.append(row0[i])
        new_block.append(row1[i])
        new_block.append(row2[i])
        new_block.append(row3[i])

    return bytes(new_block)

def inverse_mix_columns_layer(block: bytes) -> bytes:
    """
    Applique l'inverse de MixColumns sur un bloc de 16 octets
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

        mixed_col = inverse_mix_single_column(column, poly)
        mixed.extend(mixed_col)

    return bytes(mixed)

def last_transformation(block: bytes, round_key: bytes):
    """
    Transformation finale du dernier tour (InvShiftRows -> InvSubBytes -> AddRoundKey)
    """
    shifted = inverse_shift_rows_layer(block)
    subbed_block = inverse_substitution_layer(shifted)
    added_key_block = key_addition_layer(subbed_block, round_key)

    return added_key_block

def decrypt_block(block: bytes, round_words: list[bytes]):
    """
    Déchiffre un bloc de 16 octets avec la clé étendue
    """
    rounds_number = int(len(round_words) / 4)
    round_keys = build_round_keys(round_words)

    # Transformation initiale (AddRoundKey)
    mixed = key_addition_layer(block, round_keys[-1])    

    # Boucle sur les tours intermédiaires
    for i in range(rounds_number - 2, 0, -1):
        shifted = inverse_shift_rows_layer(mixed)
        subbed_block = inverse_substitution_layer(shifted)
        added_key_block = key_addition_layer(subbed_block, round_keys[i])
        mixed = inverse_mix_columns_layer(added_key_block)

    # Dernier tour
    result_block = last_transformation(mixed, round_keys[0])
    return result_block

def split_blocks(data: bytes, block_size: int = 16) -> list[bytes]:
    """
    Découpe les données en blocs de 16 octets
    """
    if len(data) % block_size != 0:
        raise ValueError("La longueur du texte chiffré doit être un multiple de 16 octets")
    
    return [data[i:i+block_size] for i in range(0, len(data), block_size)]

def pkcs7_unpad(data: bytes, block_size: int = 16) -> bytes:
    """
    Retire le padding PKCS#7 d'un texte déchiffré
    """
    pad_len = data[-1]

    if pad_len < 1 or pad_len > block_size:
        raise ValueError("Padding PKCS#7 invalide")

    if data[-pad_len:] != bytes([pad_len] * pad_len):
        raise ValueError("Padding PKCS#7 invalide")

    return data[:-pad_len]

def decrypt_text(ciphertext: str, key: str) -> bytes:
    """
    Déchiffre un texte chiffré AES en hexadécimal avec une clé hexadécimale
    """
    ciphertext_bytes = bytes.fromhex(ciphertext)
    blocks = split_blocks(ciphertext_bytes)
    round_words = key_expansion_layer(key)

    # Déchiffrement bloc par bloc
    plaintext_padded = b''.join(
        decrypt_block(block, round_words)
        for block in blocks
    )

    # Retirer le padding après déchiffrement
    return pkcs7_unpad(plaintext_padded)


# encoded_text = "7E5DEF551B569D66C55A65B3C23705CAA48350617D801AFCD6668BD044A02FEE9C007D955B27542DFC64E6B4AEB45BEE6182353F8955A793400B0A2C01AB1C0999F33E0EDB1DD1B38C2A3BCDFDDB33FED79B89DD26A497EE573AB936D14E2EE0C88E4C5DB435F2B650C2020946590343C03E263E09E8B168F0ADB31958D5C19534D2CFE47CE6930F05C8FF413A246167AB25910052CEF1E3BFFEF58BC28C3572E9E6B66AF188BBCC911D181D14FF4241FD36BD5271D9C9EF0D53813748AB1CD923BBFD9679E55F9A709F0998FC33FD564947823EEA0A094550552F666B616101E45023428F3B0084C04202014D2552CC79FC5AD7F2E18958B98B7B28476999D783DD0E4BF9C866C88362989D8C505CDCED7E80E3813FD551ACD30323B9A4ECCE71B2718405A54A3F77E9DDB433B1B2D79B45D4B19990E2580EF9E5E6E44FE8779171ED2F0B1128E589361D3C7088669B2D928055A4FDCF1523D0E0EF23FF8A4D156DD4DE405DDA2D686EF9FC438278AA5AAD9018CD6294CC821995A5A8BAB72B5AF90E44E59647BF39CF4B0B35A329A88A9A0B0C00E49F33925B4949C6BE47229FD6C99B660FFC173B0309754159D32AD59347CA340F8857E359E68332A4E61F31939EFC21BEFBBC003D8F09D96176D5ED645A2468293DF0ABB7DA8B44CBF3383807F040C227B1DFE4979E0872DB6D56027AD9F3DC156A4B7ED053E657B290D6D972B2EB39724FF017F7CE7F487EEFC940A1655318E56A9DB6934FB0A68557B5B0C759782883984294E6DA7138F8391EE3447B5826C796F85795474C786BE33D03C2CD15D7A3A78A6C375871131D0220C4EDCF5264CC8CA89A5319F09EE6A5AAF690202A3260E3B36EB6B702B743B13EF40AED4404B9A3140D01D9E6CA49EA1E9EC9C897F9F235E904081BE813E0DE0235D0EEC5A93D11C7C65D136B52B3E10E4FBACAAA138CAF3CDA8B1E9605DFE7E4B84D7A18E2619832ECE600968FE5A181E5C1AFA5DBEBB716BB72E02A0711BC07C13CEC338A1341817DDF8332D1CB7C1E972FA7EEFB9383499908C2BF84CBF28648A77958FAE967DD8A2550BD982C3242345C28136AA6C78D9D4B24186448C69391E1EC7E5B8B6BFFCE92E132E74BD5AFBA76014BB6ACF8BB261377E6956DF3851202F98FFED60E2552C7BD8D3B53790068DD01C1E26C5885E94DDD3FE5EB7404DCB076FD0E325A5DC822AAE5C07D03FE0D77DDCB42ED191A15854BE5A9B1AD5EE60DAD76E07BDBDF3E48B001D22692F816A236A1B8CE0FD9F05DCC05247BF8C2EF3942CF3C61739B1BD183433EE4E1727EC97E47167485EF08A4946EA6B2F0C9746B4D0E589C70C9AB74575AD452FAE8E61A911DB1B9400E7423DE91C58C62971BEB21930F13D5D7D68515179076DBED0BFF341B411EDF832E512546F9BCD7B5A7D19B75BCA754C3F78A7DFA9A92144D2922412AEDB19F7078B5423758EB5FEDBECB0023B8CE4863CCB4D38425B94FC5621F1B7ED86BD5A9595E1CD8F79C5D1CF90F77138B231267928E92C09361802B0ABAC2ED0063381F39E8F37FCA3F381B3E3972FBEBAADE99198090CE49551DA72260870E95F1A4804B9CE71384F487AF705120850261388CCC764847C5C1FB0A124A036FFCA95337E5C4D5CE2772C8648B5F93086FF4EE5BB6EBFC6E95351A3190C01058CA9E9A26216D3CCF139C343A5AD20F1FDD7FE525EE015A6CB7CF9E2A2EBA9A736492F40C9655898C81BCFB966428D34E4D2A7DF0695441F4E9B06B22C8838E25E168C17896FE51DB25EE71DA55B092D459EB2132531FCE759B09E4F5267226FBF930B4DF88B5F15F51A86D252E3A7AC3CA53E00F8AAE24E8329F4A6FE9DBCE52B8D8535A08D299B36C672A4C4DD0C7790219AB546D302F754A33D3F940EB590BABC216D2820C5A2C17AA932AAC9DB157DB6507EF5CB05BDD46F20388"
# key = "31323334353637383931323334353637"

# print(decrypt_text(encoded_text, key))