# PKCS#7 with slight mod
# ref: https://pentesterlab.com/glossary/pkcs7-padding
def pad(data, block_size=32):
    p = block_size - (len(data) % block_size )
    return data + (p.to_bytes(1, "big") * p)



def unpad(data, block_size=32):
    if not data or len(data) % block_size != 0:
        print("Unpad fail: data invalid") # TODO: error msg
        return b""

    p = data[-1]

    if p < 1 or p > block_size:
        raise ValueError("Invalid padding length")

    if data[-p:] != bytes([p]) * p:
        raise ValueError("Invalid padding sequence")

    return data[:-p]
