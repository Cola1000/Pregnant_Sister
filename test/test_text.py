from src.analysis import analysis as anal
from src.analysis import saveCipher as sc

with open("test/berkas/glasses.txt", "rb") as f: 
    data = f.read()

kunci = "00000000000000000000000000000000000"

anal(data, kunci, "test/histogram/text")
sc(data, kunci, "test/encrypted_message/encrypted_text.txt", True)