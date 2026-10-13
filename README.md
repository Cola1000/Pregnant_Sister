<p align="center"><img src="image.jpg"></p>

# Pregnant_Sister
Symmetric Key Cryptography Using Cellular Automaton

Symmetric block cipher menggunakan Conway's Game of Life (cellular automaton) saat generate keys dan dalam round function Feistel algorithm. Seatiap 256 bit block melewati 18 round Feistel network (2 GoL + 16 AES-style substitution-permutation). Round key didapatkan dari mix key (>=32 bytes) dengan nonce 32 bytes.

## Dokumentasi API
**https://cola1000.github.io/Pregnant_Sister/**

## Tech Stack
Python 3.13.

## Dependencies
- matplotlib: Plotting histogram
- numpy: byte/bit arrays for the analysis and tests


## Cara Menjalankan
Windows:
```powershell
python -m venv ./venv
./venv/Scripts/activate
pip install -r requirements.txt
```

Linux/macOS:
```bash
python3 -m venv ./venv
source ./venv/bin/activate
pip install -r requirements.txt
```

### Menjalankan Test
> Folder `test/` hanya ada di repositori GitHub, tidak ikut di arsip rilis. Clone/Fork repositori untuk menjalankan test.

```bash
python -m test.test_text        # analisis file teks
python -m test.test_image       # analisis file gambar
python -m test.test_video       # analisis file video
python -m test.test_security    # cipher security testing
python -m test.test_keygen      # unit test key schedule
python -m test.test_automaton   # unit test Game of Life
python -m test.test_encrypt     # round-trip semua mode untuk semua file
```
> Note: Ini dilakukan di root directory project