class SBox:
    def __init__(self, irreducible_poly: int, affine_matrix: list[int], affine_const: int):
        self.irreducible = irreducible_poly  
        self.matrix = affine_matrix           
        self.const = affine_const             
        self.table = self._generate_sbox()   

    def byte_to_bits(self, byte: int) -> list[int]:
        return [(byte >> i) & 1 for i in range(8)]

    def gf_mul(self, a: int, b: int) -> int:
        result = 0
        for _ in range(8):
            if b & 1:
                result ^= a
            carry = a & 0x80
            a <<= 1
            if carry:
                a ^= self.irreducible
            a &= 0xFF
            b >>= 1
        return result

    # inverse multiplicatif en utlisent a^(2^8-2)
    def gf_inverse(self, byte: int) -> int:
        if byte == 0:
            return 0
        result = 1
        a = byte
        power = 254  # 2^8-2  11111110
        while power > 0:
            if power & 1:
                result = self.gf_mul(result, a)
            a = self.gf_mul(a, a)
            power >>= 1
        return result

    # affine
    def affine_transform(self, byte: int) -> int:
        result = 0
        bits = self.byte_to_bits(byte)
        for i in range(8):
            bit = 0
            for j in range(8):
                if (self.matrix[i] >> j) & 1:
                    bit ^= bits[j]
            bit ^= (self.const >> i) & 1
            result |= (bit << i)
        return result

    # S-box génération
    def _generate_sbox(self) -> list[int]:
        sbox = []
        for x in range(256):
            inv = self.gf_inverse(x)
            s = self.affine_transform(inv)
            sbox.append(s)
        return sbox

    # S-box bijective vérification
    def is_bijective(self) -> bool:
        return len(set(self.table)) == 256


IRREDUCIBLE = 0x12D  # x^8 + x^5 + x^3 + x^2 + 1

AFFINE_MATRIX = [
    0b10101101,
    0b11010110,
    0b01101011,
    0b10110101,
    0b01011010,
    0b00101101,
    0b10010110,
    0b11001011,
]

# AFFINE_CONST = 0xA5

# sbox = SBox(IRREDUCIBLE, AFFINE_MATRIX, AFFINE_CONST)

# print(sbox.table[:16])
# print("Bijective:", sbox.is_bijective())

sbox = SBox(0x12D, AFFINE_MATRIX, 0xA5)

inv = sbox.gf_inverse(0x53)
print(hex(inv))
# print(len(sbox.table))  #