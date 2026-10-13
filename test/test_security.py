import base64
import math
import random
import time

import numpy as np

from src.decrypt import decrypt
from src.encrypt import encrypt
from src.feistel import process_block, round_function
from src.keygen import derive_round_keys
from src.spn import SBOX, f_spn, xor_bytes

rng = random.Random(69420)
MODES = ["ECB", "CBC", "CFB", "OFB", "CTR"]


def rand_bytes(n):
    return rng.randbytes(n)

def weight(b):
    return sum(x.bit_count() for x in b)

def flip_bit(b, i):
    b = bytearray(b)
    b[i // 8] ^= 0x80 >> (i % 8)
    return bytes(b)

def reduced_block(block, round_keys, rounds):
    l, r = block[:16], block[16:]
    for i in rounds:
        l, r = r, xor_bytes(l, round_function(r, round_keys[i - 1], i))
    return r + l

def report(ok, msg):
    print(f"[{'OK' if ok else 'WEAK'}] {msg}")


def test_roundtrip():
    fails = 0
    for mode in MODES:
        for length in [0, 1, 31, 32, 33, 100]:
            key, pt = rand_bytes(32 + rng.randrange(40)), rand_bytes(length)
            fails += decrypt(encrypt(pt, key, mode), key, mode) != pt
    report(fails == 0, f"Round-trip in all modes and lengths: {fails} failures")


def test_avalanche():
    # compare raw blocks under the same round keys, otherwise the random nonce dominates
    round_keys = derive_round_keys(rand_bytes(32), rand_bytes(32))
    dists = []
    for _ in range(20):
        pt = rand_bytes(32)
        ct = process_block(pt, round_keys)
        dists += [weight(xor_bytes(ct, process_block(flip_bit(pt, i), round_keys))) for i in range(256)]
    pct = np.mean(dists) / 256 * 100
    report(abs(pct - 50) < 1, f"Plaintext avalanche (block level): {pct:.2f}% (min {min(dists)}, max {max(dists)} of 256 bits)")

    key, nonce, pt = rand_bytes(32), rand_bytes(32), rand_bytes(32)
    ct = process_block(pt, derive_round_keys(key, nonce))
    dists = [weight(xor_bytes(ct, process_block(pt, derive_round_keys(flip_bit(key, i), nonce)))) for i in range(0, 256, 4)]
    pct = np.mean(dists) / 256 * 100
    report(abs(pct - 50) < 2, f"Key avalanche (block level): {pct:.2f}% (min {min(dists)} bits)")

    for n_rounds in [2, 3, 4]:
        dists = []
        for _ in range(10):
            pt = rand_bytes(32)
            ct = reduced_block(pt, round_keys, range(1, n_rounds + 1))
            dists += [weight(xor_bytes(ct, reduced_block(flip_bit(pt, i), round_keys, range(1, n_rounds + 1)))) for i in range(0, 256, 4)]
        print(f"       full diffusion check, {n_rounds} rounds: {np.mean(dists) / 256 * 100:.1f}%")


def test_ciphertext_stats():
    data = bytes(65536)
    start = time.perf_counter()
    ct_b64 = encrypt(data, rand_bytes(32))
    elapsed = time.perf_counter() - start

    raw = np.frombuffer(base64.b64decode(ct_b64), np.uint8)
    counts = np.bincount(raw, minlength=256)
    probs = counts[counts > 0] / raw.size
    ent = float(-np.sum(probs * np.log2(probs)))
    chi2 = float((((counts - raw.size / 256) ** 2) / (raw.size / 256)).sum())
    report(ent > 7.99 and chi2 < 293, f"Raw ciphertext of 64 KB zeros: entropy {ent:.4f}/8, chi2 {chi2:.1f} (df=255, pass < 293)")
    print(f"       note: base64 output can never exceed 6.0 bits entropy, so measure on raw bytes")
    print(f"       throughput: {len(data) / elapsed / 1024:.1f} KB/s")


def test_sbox():
    affine = all(SBOX[x] == (167 * x + 91) % 256 for x in range(256))
    ddt_max = max(
        max(np.bincount([SBOX[x] ^ SBOX[x ^ d] for x in range(256)], minlength=256))
        for d in range(1, 256)
    )
    lat_max = max(
        abs(sum(((a & x).bit_count() + (b & SBOX[x]).bit_count()) % 2 == 0 for x in range(256)) - 128)
        for a in range(1, 256) for b in range(1, 256)
    )
    report(not affine, f"S-box is affine (167x + 91 mod 256): {affine}")
    report(ddt_max <= 8, f"S-box max differential count: {ddt_max}/256 (AES: 4/256)")
    report(lat_max <= 32, f"S-box max linear bias: {lat_max}/256 (AES: 16/256)")


def test_differential():
    # 0x80 in every byte passes S-box, MixColumns and mod-add with probability 1,
    # and the data-dependent rotation keeps it whenever amount % 8 == 0
    delta, zero = b"\x80" * 16, b"\x00" * 16
    hits, n = 0, 4000
    for _ in range(n):
        x, k = rand_bytes(16), rand_bytes(16)
        hits += xor_bytes(f_spn(x, k), f_spn(xor_bytes(x, delta), k)) == delta
    p_round = max(hits, 1) / n
    report(hits / n < 0.01, f"f_spn: P[0x80..80 -> 0x80..80] = {hits}/{n} (<= 2^{math.log2(p_round):.2f})")

    # 3-round iterative Feistel
    for spn_rounds, n in [(1, 2000), (4, 20000)]:
        rounds = [1] + list(range(2, 2 + spn_rounds)) + [18]
        active = sum((j - 1) % 3 != 0 for j in range(2, 2 + spn_rounds))
        hits = 0
        for i in range(n):
            if i % 1000 == 0:
                round_keys = derive_round_keys(rand_bytes(32), rand_bytes(32))
            pt = rand_bytes(32)
            diff = xor_bytes(reduced_block(pt, round_keys, rounds), reduced_block(xor_bytes(pt, delta + zero), round_keys, rounds))
            hits += diff[16:] == delta
        observed = f"2^{math.log2(hits / n):.2f}" if hits else "0"
        print(f"       GoL + {spn_rounds} SPN + GoL: predicted 2^-{3 * active}, observed {observed} ({hits}/{n})")
    full = 11 * math.log2(p_round)
    report(full < -128, f"Full 18-round cipher: 11 active SPN rounds -> distinguisher with probability <= 2^{full:.0f} (need < 2^-128)")


def test_key_schedule():
    round_keys = [rk for _ in range(100) for rk in derive_round_keys(rand_bytes(32), rand_bytes(32))]
    density = sum(weight(rk) for rk in round_keys) / (128 * len(round_keys))
    report(abs(density - 0.5) < 0.02, f"Round-key bit density: {density:.4f} (ideal 0.5)")

    counts = np.bincount(np.frombuffer(b"".join(round_keys), np.uint8), minlength=256)
    probs = counts[counts > 0] / counts.sum()
    ent = float(-np.sum(probs * np.log2(probs)))
    report(ent > 7.98, f"Round-key byte entropy: {ent:.4f}/8 (random bytes, same sample size: ~7.99)")

    ct = encrypt(b"top secret", b"my secret key that is 32 bytes!!" * 2)
    try:
        leaked = decrypt(ct, b"A" * 64)
    except ValueError:
        leaked = None
    if leaked == b"top secret":
        report(False, f"Key X||X decrypted with unrelated key 'A'*64 (both fold to zero): {leaked}")
    else:
        report(True, "Keys X||X and 'A'*64 are not interchangeable")


test_roundtrip()
test_avalanche()
test_ciphertext_stats()
test_sbox()
test_differential()
test_key_schedule()
