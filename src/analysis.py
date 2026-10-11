import base64
import numpy as np
import matplotlib.pyplot as plt
import os
import time

from src.encrypt import encrypt
from src.decrypt import decrypt
from src.keygen import derive_round_keys
from src.modes import encrypt_blocks
from src.padding import pad

NONCE_SIZE = 32
AVALANCHE_BYTES = 2048

def avalanche_test(plaintext, ciphertext, key, mode="CBC"):
    nonce, ciphertext = ciphertext[:NONCE_SIZE], ciphertext[NONCE_SIZE:]

    # Change 1 bit of the new plaintext
    flipped = bytearray(plaintext[:AVALANCHE_BYTES])
    flipped[0] ^= 0x80
    flipped = pad(bytes(flipped))[:AVALANCHE_BYTES]

    ciphertext_2 = encrypt_blocks(flipped, derive_round_keys(key, nonce), mode, nonce)

    # Menghitung persentase perubahan bit
    bin_cipher_1 = np.unpackbits(np.frombuffer(ciphertext, dtype=np.uint8))
    bin_cipher_2 = np.unpackbits(np.frombuffer(ciphertext_2, dtype=np.uint8))

    n = min(len(bin_cipher_1), len(bin_cipher_2))
    pct = np.count_nonzero(bin_cipher_1[:n] != bin_cipher_2[:n]) / n * 100

    # Print to terminal
    print(f"Avalanche: {pct:.2f}% bits changed")

    return pct

def entropy(data):
    # Source - https://stackoverflow.com/q/15450192
    # Posted by blueSurfer, modified by community. See post 'Timeline' for change history
    # Retrieved 2026-09-28, License - CC BY-SA 3.0

    # I changed it a bit from the source

    arr = np.frombuffer(data, dtype=np.uint8)
    if arr.size == 0 : return 0.0

    probs = np.bincount(arr, minlength=256) / arr.size
    probs = probs[probs>0]

    return float(-np.sum(probs * np.log2(probs)))

def entrophy_test(plaintext, ciphertext):
    # Calculate Entropy
    entropy_ptx = entropy(plaintext)
    entropy_ctx = entropy(ciphertext)
    delta_crypt = round(entropy_ctx - entropy_ptx, 4) # Technically ctx SHOULD be higher than ptx, so yeah

    # Print to Terminal
    print(f"Entropy Plaintext (max 8.0) : {entropy_ptx:.4f}")
    print(f"Entropy Ciphertext (max 8.0): {entropy_ctx:.4f}")
    print(f"Difference in Entropy: {delta_crypt}")

    return entropy_ptx, entropy_ctx

def histogram_test(plaintext, ciphertext, path="test/histogram"):
    # Make directory if not exist
    os.makedirs(path, exist_ok=True)

    # Create The Histograms
    plt.figure()
    plt.hist(np.frombuffer(plaintext, dtype=np.uint8), bins=256, range=(0,256), color='skyblue', edgecolor='black')
    plt.xlabel('Values')
    plt.ylabel('Frequency')
    plt.title('Basic Histogram')
    plt.savefig(os.path.join(path, "plaintext_histogram.jpg"))
    plt.close()

    plt.figure()
    plt.hist(np.frombuffer(ciphertext, dtype=np.uint8), bins=256, range=(0,256), color='green', edgecolor='black')
    plt.xlabel('Values')
    plt.ylabel('Frequency')
    plt.title('Basic Histogram')
    plt.savefig(os.path.join(path, "ciphertext_histogram.jpg"))
    plt.close()

def analysis(binary: bytes, key: str, path = "test/histogram", save_path: str = None):
    start_encrypt = time.time()
    ciphertext = encrypt(binary, key)
    encrypt_time = time.time() - start_encrypt

    start_decrypt = time.time()
    plaintext = decrypt(ciphertext, key)
    decrypt_time = time.time() - start_decrypt

    print(f"Plaintext: {plaintext[:50]}")
    print(f"Ciphertext: {ciphertext[:50]}")
    print(f"Decrypted matches original: {plaintext == binary}")

    raw = base64.b64decode(ciphertext)

    avalanche_test(plaintext, raw, key)
    entrophy_test(plaintext, raw[NONCE_SIZE:])
    histogram_test(plaintext, raw[NONCE_SIZE:], path)

    print(f"Encryt + Decrypt Time (seconds): {encrypt_time:.2f} + {decrypt_time:.2f}")

    if save_path:
        writeFiles(ciphertext, plaintext, save_path)

    return 0

def writeFiles(ciphertext: bytes, restored: bytes | None, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(ciphertext)

    if restored is not None:
        os.makedirs("test/decrypted_message", exist_ok=True)
        with open("test/decrypted_message/restored"+os.path.splitext(path)[1], "wb") as f:
            f.write(restored)

def saveCipher(plaintext: bytes, key: str, path: str, save_decrypt : bool = False):
    msg = encrypt(plaintext,key)
    writeFiles(msg, decrypt(msg,key) if save_decrypt else None, path)

    return 0