#!/usr/bin/env python3
"""
HX Hash Cracker 6 Char Ready
Miraç - Advanced CTF Engine
"""
import hashlib
import itertools
import string
import sys
import time
import os
from multiprocessing import cpu_count, Pool
from datetime import datetime
from colorama import init, Fore, Style
import argparse

init(autoreset=True)

def print_banner():
    print("=" * 60)
    print("HX Hash Cracker!!")
    print("by Miraç")
    print("=" * 60)

def print_summary(target_hash, algo, wordlist_path, max_length, result, elapsed, total_checked):
    print("=" * 60)
    print("[+] Hedef hash:              ", target_hash)
    print("[+] Algoritma:               ", algo.upper())
    print("[+] CPU Core:                ", cpu_count())
    print("[+] Max uzunluk:             ", max_length)
    print("[+] Wordlist:                ", wordlist_path or "dahili")
    print("[+] Hash kırıldı?:           ", "true" if result else "false")
    if result:
        print("[+] Decode edildi:           ", f'"{result}"')
    print("[+] Süre:                    ", f"{elapsed:.2f}s")
    print("[+] Toplam hash:             ", f"{total_checked:,}")
    print("=" * 60)

class Logger:
    def __init__(self):
        self.start = time.time()
        self.total = 0

    def log(self, msg, count=0):
        self.total += count
        elapsed = time.time() - self.start
        speed = self.total / elapsed / 1e6 if elapsed > 0.1 else 0
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {speed:.2f}M/h | {msg}")

logger = Logger()

def hash_check(args):
    algo, pwd_bytes, target = args
    if algo == "md5": h = hashlib.md5(pwd_bytes).hexdigest()
    elif algo == "sha1": h = hashlib.sha1(pwd_bytes).hexdigest()
    elif algo == "sha256": h = hashlib.sha256(pwd_bytes).hexdigest()
    else: return None
    return pwd_bytes.decode() if h == target.lower() else None

def detect_hash(h):
    l = len(h.lower())
    return {32: "md5", 40: "sha1", 64: "sha256"}.get(l)

# ----------------- L6 STRATEGY ----------------- #
def hybrid_attack(algo, target, max_len=6):
    """L6 için hybrid: rules + mutations + brute"""
    logger.log(f"Hybrid L{max_len} attack başlatılıyor")
    
    # Phase 1: Rules (CTF patterns)
    rules = generate_rules(target[:8])  # Hash prefix pruning
    if rules:
        result = rule_attack(algo, target, rules)
        if result: return result
    
    # Phase 2: Progressive brute
    for length in range(1, max_len + 1):
        logger.log(f"Progressive L{length}")
        result = progressive_brute(algo, target, length)
        if result: return result
    
    return None

def generate_rules(prefix):
    """Hash prefix'e göre pruning"""
    common_patterns = [
        "pass", "admin", "test", "user", "root", "guest",
        "123", "abc", "qwe", "asd", "zxc", "kanka"
    ]
    return common_patterns[:10]  # limitli

def rule_attack(algo, target, rules):
    """Rule-based mutations"""
    mutations = []
    for base in rules:
        mutations.extend([
            base, base+"1", base+"123", "1"+base,
            base.upper(), base+"!", base+"@"
        ])
    
    tasks = [(algo, m.encode(), target) for m in mutations[:1000]]
    
    with Pool(cpu_count()) as pool:
        results = pool.map(hash_check, tasks)
        for result in results:
            if result:
                logger.log(f"RULE HIT: {result}")
                return result
    return None

def progressive_brute(algo, target, length):
    """Smart chunked brute L1-L6"""
    charset = "abcdefghijklmnopqrstuvwxyz0123456789"  # 36 chars
    
    # Chunk size by length (memory safe)
    chunk_sizes = {1: 10000, 2: 5000, 3: 2000, 4: 1000, 5: 500, 6: 200}
    chunk_size = chunk_sizes.get(length, 100)
    
    total_checked = 0
    combos = itertools.product(charset, repeat=length)
    
    chunk = []
    for combo in combos:
        pwd = ''.join(combo).encode()
        chunk.append((algo, pwd, target))
        
        if len(chunk) >= chunk_size:
            with Pool(min(6, cpu_count())) as pool:
                results = pool.map(hash_check, chunk)
                total_checked += len(chunk)
                
                for result in results:
                    if result:
                        logger.log(f"L{length} BRUTE HIT: {result}")
                        return result
            
            logger.log(f"L{length}: {total_checked:,} checked")
            chunk = []
    
    # Final chunk
    if chunk:
        with Pool(min(6, cpu_count())) as pool:
            results = pool.map(hash_check, chunk)
            total_checked += len(chunk)
    
    return None

def wordlist_attack(algo, target, path=None):
    logger.log(f"{algo.upper()} wordlist")
    
    ctf_words = [
        "password", "123456", "qwerty", "admin", "letmein", "welcome",
        "monkey", "dragon", "master", "hello", "abc123", "password1",
        "trustno1", "ninja", "shadow", "football", "6969"
    ]
    
    words = ctf_words[:]
    if path and os.path.exists(path):
        try:
            with open(path, "rb") as f:
                words.extend(line.decode('utf-8', errors='ignore').strip()
                           for _, line in zip(range(50000), f) if line.strip())
        except: pass
    
    tasks = [(algo, pwd.encode(), target) for pwd in words[:20000]]
    
    chunk_size = max(2000, len(tasks) // cpu_count())
    
    with Pool(cpu_count()) as pool:
        for i in range(0, len(tasks), chunk_size):
            chunk = tasks[i:i+chunk_size]
            results = pool.map(hash_check, chunk)
            
            for result in results:
                if result:
                    logger.log(f"WORDLIST HIT: {result}")
                    return result
    
    return None

def main():
    parser = argparse.ArgumentParser(description="HX v7.0 - L6 Capable")
    parser.add_argument("hash", help="Hedef hash")
    parser.add_argument("-a", "--algo", choices=['md5', 'sha1', 'sha256', 'auto'], default='auto')
    parser.add_argument("-w", "--wordlist", help="Wordlist")
    parser.add_argument("-l", "--length", type=int, default=6, help="Max length (1-6)")
    
    args = parser.parse_args()
    
    target_hash = args.hash.strip()
    algo = detect_hash(target_hash) if args.algo == 'auto' else args.algo
    
    if algo not in ["md5", "sha1", "sha256"]:
        print("❌ Geçersiz hash tipi!")
        sys.exit(1)
    
    print_banner()
    
    start_time = time.time()
    total_checked = 0
    
    # Attack chain
    result = wordlist_attack(algo, target_hash, args.wordlist)
    if not result:
        result = hybrid_attack(algo, target_hash, args.length)
    
    elapsed = time.time() - start_time
    
    print_summary(target_hash, algo, args.wordlist or "dahili", 
                 args.length, result, elapsed, logger.total)

if __name__ == "__main__":
    main()


