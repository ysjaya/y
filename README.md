
# MASS: VCC Checker Stripe Charge $3

VCC Checker $3 is a powerful Python-based tool designed to bulk-check virtual credit cards (VCC) by charging $3 on each card using the Stripe API. It supports proxy rotation for enhanced security, provides detailed error handling, and logs every transaction attempt. The tool outputs live and failed cards to separate files, ensuring optimal results.


## Terminal Preview
When executed, the tool provides real-time feedback directly in the terminal:
```bash
    ███████╗ ██████╗  ██████╗ ███████╗
    ██╔════╝██╔═══██╗██╔════╝ ██╔════╝
    █████╗  ██║   ██║██║  ███╗███████╗
    ██╔══╝  ██║   ██║██║   ██║╚════██║
    ██║     ╚██████╔╝╚██████╔╝███████║
    ╚═╝      ╚═════╝  ╚═════╝ ╚══════╝
    Author: Mh. Taufiq Hidayatulloh
    Github: https://github.com/taufiqdayat211
    Telegram: https://t.me/aswggg77

Masukkan path file kartu (cc.txt): cc.txt
Masukkan path file proxy (proxy.txt) atau kosongkan jika tidak ingin menggunakan proxy: proxy.txt

Success: ['4111111111111111', '12', '25', '123']
Failed: ['5500000000000004', '11', '26', '456'] - Proxy error/die
````
## Installation Instructions

**Linux, Windows, Termux:**
```sh
git clone https://github.com/yourgithub/vcc_checker.git
cd vcc_checker
pip install -r requirements.txt
```
Create a `.env` file and add yourStripe API key:

```sh
echo "STRIPE_API_KEY=your_stripe_secret_key" > .env
```

Run the script:
```sh
python vcc_checker.py
```


## Required Packages
Before running the script, ensure you have the following Python packages installed:

- **stripe**
- **requests**
- **colorama**
- **dotenv**

You can install all dependencies with:
```sh
pip install -r requirements.txt
```

## How the Script Works

**Card Input:** The user provides a `.txt` file containing a list of credit cards in the format `card|mm|yy|cvv` .

**Proxy Support:** Optionally, a proxy file can be provided in the format `ip:port` for each line, ensuring you avoid IP blocks during the charge process.

**Charge Process:** The tool checks each card against the Stripe API, charging $3. If a proxy fails, the script switches to the next one in the list and retries.

**Logging:** All results, both successful and failed charges, are logged in separate files ( `Live charger $3.txt` and ` Failed charger $3.txt` ), while errors are printed in the terminal.

**Real-time Output:** Each success is displayed in green and each failure in red, offering clear visual feedback during execution.


## Error Handling

- **Proxy Errors:** If a proxy fails, the tool will attempt to rotate through proxies from the provided list, ensuring minimal disruptions.

- **Network/Timeout Issues:** Timeout and connection errors will be flagged in red in the terminal, and corresponding cards will be marked as failed.

- **Invalid File Format:** The tool will alert users if the credit card or proxy files do not adhere to the required format.

Make sure to monitor the logs ( `vcc_checker.log` ) for detailed troubleshooting and performance insights.
