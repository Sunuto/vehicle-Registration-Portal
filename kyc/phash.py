from PIL import Image
import math

def resize_image(image_path, size=32):
    """Step 1 & 2: Resize and convert to grayscale"""
    image = Image.open(image_path)
    image = image.convert('L')
    image = image.resize((size, size), Image.LANCZOS)
    return image

def get_pixels(image):
    """Get pixel values as 2D list"""
    size = image.size[0]
    pixels = []
    for y in range(size):
        row = []
        for x in range(size):
            row.append(float(image.getpixel((x, y))))
        pixels.append(row)
    return pixels

def apply_dct(pixels, size=32):
    """
    Step 3: Apply Discrete Cosine Transform (DCT)
    Formula: DCT(u,v) = (2/N) * C(u) * C(v) * SUM[pixel(x,y) * cos((2x+1)*u*pi/2N) * cos((2y+1)*v*pi/2N)]
    """
    dct_result = []
    N = size

    for u in range(N):
        row = []
        for v in range(N):
            cu = 1.0 / math.sqrt(2) if u == 0 else 1.0
            cv = 1.0 / math.sqrt(2) if v == 0 else 1.0

            total = 0.0
            for x in range(N):
                for y in range(N):
                    cos_x = math.cos((2 * x + 1) * u * math.pi / (2 * N))
                    cos_y = math.cos((2 * y + 1) * v * math.pi / (2 * N))
                    total += pixels[x][y] * cos_x * cos_y

            dct_val = (2.0 / N) * cu * cv * total
            row.append(dct_val)
        dct_result.append(row)

    return dct_result

def get_top_left(dct_result, keep=8):
    """Step 4: Take top-left 8x8 values (low frequency components)"""
    top_left = []
    for y in range(keep):
        for x in range(keep):
            top_left.append(dct_result[y][x])
    return top_left

def compute_phash(image_path):
    """
    Full pHash algorithm:
    1. Resize to 32x32
    2. Grayscale
    3. DCT
    4. Take top-left 8x8
    5. Calculate mean
    6. Build hash bits
    7. Return hex hash string
    """
    image = resize_image(image_path, size=32)
    pixels = get_pixels(image)
    dct_result = apply_dct(pixels, size=32)
    top_left = get_top_left(dct_result, keep=8)

    mean = sum(top_left[1:]) / len(top_left[1:])

    bits = []
    for val in top_left:
        bits.append('1' if val > mean else '0')

    bit_string = ''.join(bits)
    while len(bit_string) % 4 != 0:
        bit_string += '0'

    hex_hash = ''
    for i in range(0, len(bit_string), 4):
        chunk = bit_string[i:i+4]
        hex_hash += hex(int(chunk, 2))[2:]

    return hex_hash

def hamming_distance(hash1, hash2):
    """
    Hamming Distance = number of bit positions that differ.
    Distance 0 = identical
    Distance < 10 = likely duplicate
    """
    def hex_to_bits(hex_str):
        bits = ''
        for char in hex_str:
            bits += bin(int(char, 16))[2:].zfill(4)
        return bits

    bits1 = hex_to_bits(hash1)
    bits2 = hex_to_bits(hash2)

    min_len = min(len(bits1), len(bits2))
    bits1 = bits1[:min_len]
    bits2 = bits2[:min_len]

    distance = sum(b1 != b2 for b1, b2 in zip(bits1, bits2))
    return distance

def check_duplicate(new_hash, existing_docs, threshold=10):
    """
    Compare new hash against all existing hashes.
    Returns (is_duplicate, reason, matching_doc)
    """
    for doc in existing_docs:
        if not doc.phash_value:
            continue

        distance = hamming_distance(new_hash, doc.phash_value)

        if distance < threshold:
            reason = (
                f'Possible duplicate or tampered document detected! '
                f'Similar to document uploaded by {doc.user.username} '
                f'(Hamming distance: {distance} — threshold: {threshold})'
            )
            return True, reason, doc

    return False, None, None