import random
import requests
import json
import time
import subprocess
from urllib.parse import parse_qs
import base64
import socket
from datetime import datetime, timedelta
# URL dan headers

headers = {
    'accept': 'application/json; indent=2',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://lfg.supermeow.vip',
    'priority': 'u=1, i',
    'referer': 'https://lfg.supermeow.vip/',
    'sec-ch-ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24", "Microsoft Edge WebView2";v="125"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
}

# Fungsi untuk membaca initData dari file
def read_initdata_from_file(filename):
    initdata_list = []
    with open(filename, 'r') as file:
        for line in file:
            initdata_list.append(line.strip())
    return initdata_list

def read_serial_from_file(filename):
    initdata_list = []
    with open(filename, 'r') as file:
        for line in file:
            initdata_list.append(line.strip())
    return initdata_list

initdata_file = "initdata.txt"
serial_file = "serial.txt"
initdata_list = read_initdata_from_file(initdata_file)
serial_list = read_serial_from_file(serial_file)
last_claim_time = [0] * len(initdata_list)  # Initialize last claim times
interval = 86400
# Fungsi untuk mengambil nama dari init_data
def get_nama_from_init_data(auth_data):
    parsed_data = parse_qs(auth_data)
    auth_data_json_str = parsed_data.get('auth_data', [None])[0]

    if auth_data_json_str:
        try:
            auth_data_json = json.loads(auth_data_json_str)

            user_info_str = auth_data_json.get('user')
            if user_info_str:
                user_info = json.loads(user_info_str)

                first_name = user_info.get('first_name', '')
                last_name = user_info.get('last_name', '')
                username = user_info.get('username', '')

                # Combine first name, last name, and username in a specific format
                data = ""
                if first_name:
                    data += first_name
                if last_name:
                    data += " " + last_name
                if username:
                    data += f" ({username})"

                return data.strip()
            else:
                return "user info not found in auth_data"
        except json.JSONDecodeError as e:
            return f"Invalid JSON format in auth_data: {e}"
    else:
        return "auth_data not found in the query parameters"

# Fungsi untuk melakukan start session
def start_session(auth_data):
    parsed_data = parse_qs(auth_data)
    auth_data_json_str = parsed_data.get('auth_data', [None])[0]
    try:
        auth_data_json = json.loads(auth_data_json_str)
       
        user_info_str = auth_data_json.get('user')
        user_info = json.loads(user_info_str)


        json_data = {
            'user': {
                'id': int(user_info.get('id', '')),
                'first_name': user_info.get('first_name', ''),
                'last_name': user_info.get('last_name', ''),
                'username': user_info.get('username', ''),
                'language_code':user_info.get('language_code', ''),
                'allows_write_to_pm': user_info.get('allows_write_to_pm', ''),
            }
        }

        response = requests.post(
            f'https://api.supermeow.vip/meow/info?{auth_data}',
            headers=headers,
            json=json_data,
        )
        return response
    except json.JSONDecodeError:
        return "Invalid JSON format in init_data"
    except KeyError:
        return "Missing required fields in user info"

# Fungsi untuk melakukan claim harian
def claim_harian(init_data):
    try:
        response = requests.post(
            f'https://api.supermeow.vip/meow/claim?{init_data}',
            headers=headers,
        )
        return response
    except Exception as e:
        return f"An error occurred: {e}"

def checkin_daily(init_data):
    start_pos = init_data.find('auth_data')
    if start_pos != -1:
        result_string = init_data[start_pos:]
    else:
        print("auth_data not found in the input string")
    try:
        response = requests.post(
            f'https://api.supermeow.vip/meow/serial-checkin?{result_string}',
            headers=headers,
        )
        return response
    except Exception as e:
        return f"An error occurred: {e}"

# Fungsi untuk menjalankan operasi untuk setiap initData
def process_initdata(init_data, i):
    current_time = time.time()
    try:
        nama = get_nama_from_init_data(init_data)
        print(f"Nama: {nama}")

        start_response = start_session(init_data)
        if start_response.status_code == 200:
            try:
                start_data = start_response.json()['balance']
            except KeyError:
                print("Key 'balance' not found in response")
        else:
            print('Belum Waktunya Claim')

        daily_response = claim_harian(init_data)
        if daily_response.status_code == 200:
            try:
                daily_data = daily_response.json()['last_claim']
                print("Sukses Claim")
            except KeyError:
                print("Belum Waktunya Claim")
        else:
            print('Sudah Ambil Daily')

        if current_time - last_claim_time[i] >= interval:
            daily_checkin = checkin_daily(init_data)
            last_claim_time[i] = current_time
            if daily_checkin.status_code == 200:
                try:
                    print(daily_checkin)
                    print("Sukses Claim Daily")
                except KeyError:
                    print("Belum Waktunya Claim Daily")
            else:
                print("Checkin Daily Sudah Claim")
            now = current_time - last_claim_time[i]
            print(f"waiting {now/60} mins to 1440 mins to claim daily")
        else:
            print("checkin daily belum siap")
    except Exception as e:
        print(f"An error occurred: {e}")

def get_serial(current_date, getpcname, name, status):
    formatted_current_date = current_date.strftime("%d-%m-%Y")
    # Encode each value using base64
    getpcname += "knjt"
    name    += "knjt"
    encoded_getpcname = base64.b64encode(getpcname.encode()).decode().replace("=", "")
    encoded_current_date = base64.b64encode(formatted_current_date.encode()).decode().replace("=", "")
    encoded_name = base64.b64encode(name.encode()).decode().replace("=", "")
    encoded_status = base64.b64encode(str(status).encode()).decode().replace("=", "")

    # Calculate the length of each encoded value
    getpcname_len = len(encoded_getpcname)
    current_date_len = len(encoded_current_date)
    name_len = len(encoded_name)
    status_len = len(encoded_status)

    # Concatenate the encoded values with their lengths
    serial = "S4NS-"
    serial += str(getpcname_len).zfill(2) + encoded_getpcname
    serial += str(current_date_len).zfill(2) + encoded_current_date
    serial += str(name_len).zfill(2) + encoded_name
    serial += str(status_len).zfill(2) + encoded_status
    return serial

def decode_pc(serial, getpcname, name, current_date):
    try:
        getpcname_len = int(serial[5:7])
        encoded_getpcname = serial[7:7+getpcname_len]
        current_date_len = int(serial[7+getpcname_len:9+getpcname_len])
        encoded_current_date = serial[9+getpcname_len:9+getpcname_len+current_date_len]
        name_len = int(serial[9+getpcname_len+current_date_len:11+getpcname_len+current_date_len])
        encoded_name = serial[11+getpcname_len+current_date_len:11+getpcname_len+current_date_len+name_len]
        status_len = int(serial[11+getpcname_len+current_date_len+name_len:13+getpcname_len+current_date_len+name_len])
        encoded_status = serial[13+getpcname_len+current_date_len+name_len:13+getpcname_len+current_date_len+name_len+status_len]

        # Decode each value using base64
        decoded_getpcname = base64.b64decode(encoded_getpcname + "==").decode()
        decoded_current_date = base64.b64decode(encoded_current_date + "==").decode()
        decoded_name = base64.b64decode(encoded_name + "==").decode()
        decoded_status = base64.b64decode(encoded_status + "==").decode()
        
        dates = compare_dates(decoded_current_date)

        if decoded_status != '1':
            print("Key Not Generated")
            return None
            
        elif decoded_getpcname.replace("knjt", "") != getpcname:
            print("Different devices registered")
            return None
        
        elif decoded_name.replace("knjt", "") != name:
            print("Different bot registered")
            return None
        
        elif dates > 7:
            print("Key Expired")
            return None
        else:
            print(f"key alive until : {decoded_current_date}")
            return dates
    except Exception as e:
        print(f'Key Error : {e}')

def compare_dates(date_str):
    tanggal_compare_dt = datetime.strptime(date_str, '%d-%m-%Y')
    tanggal_now = datetime.now()
    perbedaan_hari = (tanggal_compare_dt - tanggal_now).days
    return perbedaan_hari

# Main program
def main():
    getpcname = socket.gethostname()
    name = "SuperMeow"
    current_date = datetime.now() # Get the current date
    status = '0'
    
    if len(serial_list) == 0:
        serial = get_serial(current_date, getpcname, name, status)
        print(r"""
              
            Created By Snail S4NS Group
    find new airdrop & bot here: t.me/sanscryptox
              
          """)
        print(f"Your key : {serial}")
        print(f"Copy, tag bot @SnailHelperBot and paste this key in discussion group t.me/sanscryptox")
    else:
        print(r"""
              
            Created By Snail S4NS Group
    find new airdrop & bot here: t.me/sanscryptox
              
          """)
        
        serial = serial_list[0]
        decodeds = decode_pc(serial, getpcname, name, current_date)
        if decodeds is not None:
            time.sleep(10)
            while True:
                for i, init_data in enumerate(initdata_list):
                    process_initdata(init_data, i)
                    time.sleep(5)
                timer = random.randint(1800, 3600)
                min = timer/60
                print(f"waiting {min} mins")
                if decodeds == 0 :
                    serial = get_serial(current_date, getpcname, name, status)
                    print(r"""
              
            Created By Snail S4NS Group
    find new airdrop & bot here: t.me/sanscryptox
              
                    """)
                    print(f"Your key : {serial}")
                    print(f"Copy, tag bot @SnailHelperBot and paste this key in discussion group t.me/sanscryptox")
                    break
                time.sleep(timer)
        else:
            print("Please submit the key to get new key")
            serial = get_serial(current_date, getpcname, name, status)
            print(f"This Your key : {serial}")
            print(f"Copy, tag bot @SnailHelperBot and paste this key in discussion group t.me/sanscryptox")
    

if __name__ == "__main__":  
    main()
