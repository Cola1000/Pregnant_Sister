from src.analysis import analysis as anal
from src.encrypt import encrypt
from src.decrypt import decrypt

with open("test/berkas/image.jpg", "rb") as f: 
    data = f.read()

kunci = "00000000000000000000000000000000000"

ciphertext = encrypt(data, kunci)
print(ciphertext)
plaintext = decrypt(ciphertext, kunci)
print(plaintext)

anal(plaintext, ciphertext)