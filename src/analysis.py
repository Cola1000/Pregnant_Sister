import numpy as np

from src.encrypt import encrypt
from src.decrypt import decrypt

def avalanche_test(plaintext, ciphertext, key):
    # Change 1 bit of the new plaintext
    new_plaintext = '0' if plaintext[-1] == '1' else '1'

    # Create second ciphertext
    ciphertext_2 = encrypt(new_plaintext, key)

    # Menghitung persentase perubahan bit
    bin_cipher_1 = ' '.join(format(ord(char), '08b') for char in ciphertext)
    bin_cipher_2 = ' '.join(format(ord(char), '08b') for char in ciphertext_2)

    cipher_1_percentage = [
        (bin_cipher_1.count("0")/len(bin_cipher_1))*100,
        (bin_cipher_1.count("1")/len(bin_cipher_1))*100
    ]

    cipher_2_percentage = [
        ((bin_cipher_2.count("0"))/len(bin_cipher_1))*100,
        ((bin_cipher_2.count("1"))/len(bin_cipher_1))*100
    ]

    print("Cipher (Unchanged) 0's percentage: " + cipher_1_percentage[0])
    print("Cipher (Unchanged) 1's percentage: " + cipher_1_percentage[1])
    print("Cipher (Changed) 0's percentage: " + cipher_2_percentage[0])
    print("Cipher (Changed) 1's percentage: " + cipher_2_percentage[1])

    return 0

def entropy(labels):
    # Source - https://stackoverflow.com/q/15450192
    # Posted by blueSurfer, modified by community. See post 'Timeline' for change history
    # Retrieved 2026-09-28, License - CC BY-SA 3.0
    """ Computes entropy of 0-1 vector. """
    n_labels = len(labels)

    if n_labels <= 1:
        return 0

    counts = np.bincount(labels)
    probs = counts[np.nonzero(counts)] / n_labels
    n_classes = len(probs)

    if n_classes <= 1:
        return 0
    return - np.sum(probs * np.log(probs)) / np.log(n_classes)

def entrophy_test(plaintext, ciphertext):
    entropy_ptx = entropy(plaintext)
    entropy_ctx = entropy(ciphertext)
    delta_crypt = abs(entropy_ptx - entropy_ctx)

    print("Entropy Plaintext: " + entropy_ptx)
    print("Entropy Ciphertext: " + entropy_ctx)
    print("Difference in Entropy: "+ delta_crypt)

    return 0

def analysis(binary, key):
    ciphertext = encrypt(binary, key)
    plaintext = decrypt(ciphertext, key) 

    avalanche_test(plaintext, ciphertext, key)
    entrophy_test(plaintext, ciphertext)
    histogram_test()

    return 0