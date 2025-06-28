BASE = 85
ASCII_OFFSET = 33
BYTES_PER_BLOCK = 4
CHARS_PER_BLOCK = 5
BITS_PER_BYTE = 8


def encode_ascii85(data: bytes) -> str:
    partial_block_bytes = len(data) % BYTES_PER_BLOCK
    byte_block_size = BYTES_PER_BLOCK

    def encode_block(begin: int):
        int_val = 0
        for j in range(byte_block_size):
            int_val += data[begin + j] << BITS_PER_BYTE * (BYTES_PER_BLOCK - 1 - j)

        encoded_block = [None] * CHARS_PER_BLOCK
        for j in range(CHARS_PER_BLOCK - 1, -1, -1):
            encoded_block[j] = chr((int_val % BASE) + ASCII_OFFSET)
            int_val //= BASE
        return encoded_block

    encoded_chars = []
    bulk_bytes = len(data) - len(data) % BYTES_PER_BLOCK

    for i in range(0, bulk_bytes, BYTES_PER_BLOCK):
        encoded_chars.extend(encode_block(i))

    if partial_block_bytes:
        byte_block_size = partial_block_bytes
        partial_block_size = partial_block_bytes + (CHARS_PER_BLOCK - BYTES_PER_BLOCK)
        encoded_chars.extend(encode_block(bulk_bytes)[:partial_block_size])

    return ''.join(encoded_chars)
