#!/usr/bin/env python3
"""
HASH Creator - Miraç
MD5/SHA1/SHA256/SHA512 Generator
"""
import hashlib
import sys
from colorama import init, Fore, Style

init(autoreset=True)

def print_banner():
    print("=" * 20)
    print("BY Miraç")
    print("HASH creator!!")
    print("=" * 20)

def hash_create(algo, text):
    """Hash generator"""
    algos = {
        'md5': hashlib.md5(text.encode()).hexdigest(),
        'sha1': hashlib.sha1(text.encode()).hexdigest(),
        'sha256': hashlib.sha256(text.encode()).hexdigest(),
        'sha512': hashlib.sha512(text.encode()).hexdigest()
    }
    return algos.get(algo, "")

def print_result(text, algo, hash_value):
    print("\n" + "=" * 50)
    print(f"[+] Metin:     '{text}'")
    print(f"[+] Algoritma: {algo.upper()}")
    print(f"[+] Hash:      {hash_value}")
    print("=" * 50)
    print(f"{Fore.CYAN}💡 HX Cracker ile test et:{Style.RESET_ALL}")
    print(f"   python3 main.py {hash_value}")

def main():
    print_banner()
    
    # Input
    text = input(f"{Fore.WHITE}Metin gir: {Style.RESET_ALL}").strip()
    if not text:
        print("❌ Boş metin!")
        sys.exit(1)
    
    print("\nAlgoritma seç:")
    print("1. MD5    (32 char)")
    print("2. SHA1   (40 char)")
    print("3. SHA256 (64 char)")
    print("4. SHA512 (128 char)")
    
    choice = input(f"{Fore.YELLOW}Seçim (1-4): {Style.RESET_ALL}").strip()
    
    algos = {'1': 'md5', '2': 'sha1', '3': 'sha256', '4': 'sha512'}
    algo = algos.get(choice)
    
    if not algo:
        print("❌ Geçersiz seçim!")
        sys.exit(1)
    
    # Generate
    hash_value = hash_create(algo, text)
    print_result(text, algo, hash_value)

if __name__ == "__main__":
    main()
