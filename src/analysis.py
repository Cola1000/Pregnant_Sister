import numpy as np
import matplotlib.pyplot as plt
import os

from src.encrypt import encrypt
from src.decrypt import decrypt

def avalanche_test(plaintext, ciphertext, key):
    # Change 1 bit of the new plaintext
    flipped = bytearray(plaintext)
    flipped[0] ^= 0x80

    # Create second ciphertext
    ciphertext_2 = encrypt(bytes(flipped), key)

    # Menghitung persentase perubahan bit
    bin_cipher_1 = np.unpackbits(np.frombuffer(ciphertext, dtype=np.uint8))
    bin_cipher_2 = np.unpackbits(np.frombuffer(ciphertext_2, dtype=np.uint8))

    n = min(len(bin_cipher_1), len(bin_cipher_2))
    pct = np.count_nonzero(bin_cipher_1[:n] != bin_cipher_2[:n]) / n * 100


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
    entropy_ptx = entropy(plaintext)
    entropy_ctx = entropy(ciphertext)
    delta_crypt = round(abs(entropy_ptx - entropy_ctx), 4)

    print(f"Entropy Plaintext: {entropy_ptx:.4f}")
    print(f"Entropy Ciphertext: {entropy_ctx:.4f}")
    print(f"Difference in Entropy: {delta_crypt}")


    return entropy_ptx, entropy_ctx

def histogram_test(plaintext, ciphertext, path="test/histogram"):

    plt.figure()
    plt.hist(np.frombuffer(plaintext, dtype=np.uint8), bins=256, range=(0,256), color='skyblue', edgecolor='black')
    plt.xlabel('Values')
    plt.ylabel('Frequency')
    plt.title('Basic Histogram')
    plt.savefig(os.path.join(path, f"plaintext_histogram.jpg"))
    plt.close()

    plt.figure()
    plt.hist(np.frombuffer(ciphertext, dtype=np.uint8), bins=256, range=(0,256), color='green', edgecolor='black')
    plt.xlabel('Values')
    plt.ylabel('Frequency')
    plt.title('Basic Histogram')
    plt.savefig(os.path.join(path, f"ciphertext_histogram.jpg"))
    plt.close()

    pass

def analysis(binary: bytes, key: str, path = None):
    ciphertext = encrypt(binary, key)
    plaintext = decrypt(ciphertext, key) 

    print(plaintext[50:])
    print(ciphertext[50:])

    avalanche_test(plaintext, ciphertext, key)
    entrophy_test(plaintext, ciphertext)
    histogram_test(plaintext, ciphertext, path)

    return 0