import os
from src.encrypt import encrypt
from src.decrypt import decrypt

key = b"LG 24U411A-B FHD IPS Monitor 120Hz, 1ms, with 4 Side Borderless - LG 24U411B-B 144hz"
nonce_size = 32
modes = ["ECB", "CBC", "CFB", "OFB", "CTR"]

files = ["glasses.txt", "image.jpg", "video.mp4"]

for f in files:
    print(f"=====================================")
    print(f"Testing File: {f}")
    
    with open("test/berkas/" + f, "rb") as fi:
        data = fi.read()
        
    print(f"File Size: {len(data)} bytes")

    for mode in modes:
        print(f"\nTesting Mode: {mode}")
        try:
            ct = encrypt(data, key, mode=mode, nonce_size=nonce_size)
            dec = decrypt(ct, key, mode=mode, nonce_size=nonce_size)
            if data == dec:
                print(f"Tests succesfull")
            else:
                print(f"Decrypted data invalid")

            dec_f = f"test/output/decrypted_{mode}_{f}"
            with open(dec_f, "wb") as f_out_dec:
                f_out_dec.write(dec)
                
        except Exception as e:
            print(f"{mode} failed: {e}")
