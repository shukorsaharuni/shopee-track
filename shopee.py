import os
import sys
import requests
import pandas as pd
import json
import tabulate
import configparser
from datetime import datetime

# Save data to json file
def save_json_file(data):
    with open('data/data.json', 'w') as fp:
        json.dump(data,fp)

# Get shopee information from cookies
def get_shopee():
    seller=[]
    order_id=[]
    create_time=[]
    paid_amount=[]
    shipping_fee=[]
    merchandise_subtotal=[]

    shopee_dict={}
    new_offset=0

    config  = configparser.ConfigParser()
    config.read('config/credential.ini')
    SPC_EC = config['SHOPEE']['SPC_EC']

    while new_offset >= 0:
        url='https://shopee.com.my/api/v1/orders'
        params = {'limit':5,'order_type':3,'offset':new_offset}
        header = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
        }
        cookie = {"SPC_EC":SPC_EC}
        
        res=requests.get(url,params,cookies=cookie,headers=header)
        data = res.json()['orders']

        for details in data:
            if isinstance(details, dict):
                seller.append(details['seller']['username'])
                order_id.append(details['ordersn'])
                create_time.append(datetime.fromtimestamp(details['create_time']).strftime('%d-%m-%Y %H:%M:%S'))
                paid_amount.append(details['paid_amount'] / 100000)
                shipping_fee.append(details['shipping_fee'] / 100000)
                merchandise_subtotal.append(details['merchandise_subtotal'] / 100000)

        new_offset = res.json()['new_offset']

    shopee_dict["Order ID"]=order_id
    shopee_dict["Seller"]=seller
    shopee_dict["Created"]=create_time
    shopee_dict["Amount"]=merchandise_subtotal
    shopee_dict["Shipping Fee"]=shipping_fee
    shopee_dict["Total"]=paid_amount

    save_json_file(shopee_dict)

# Display data from json file
def df_shopee():
    f = open('data/data.json')
    shopee_json = json.loads(f.read()) 
    df = pd.DataFrame(shopee_json)
    #df.loc['total'] = df.sum(numeric_only=True, axis=0)
    print(tabulate.tabulate(df, tablefmt='grid',headers=list(df)))

# Main menu
def mainmenu():
    # Clear console
    os.system('cls' if os.name in ('nt', 'dos') else 'clear')

    while(True):
        print("Main Menu : \n")
        menu_options = {
            1: 'Show all purchase by order transaction',
            0: 'Exit Program',
        }

        for key in menu_options.keys():
            print (key, '--', menu_options[key] )
        
        try:
            option = int(input('\nEnter your choice: '))
        except:
            print('Wrong input. Please enter a number ...')
        if option == 1:
           print('ok')
        elif option == 0:
            sys.exit(0)
        else:
            print('Invalid option. Please enter a number between 1 and 4.')
    
if __name__ == "__main__":
    mainmenu()