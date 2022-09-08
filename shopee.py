import os
import sys
import requests
import pandas as pd
import numpy as np
import json
import configparser

# Save data to json file
def save_json_file(data):
    with open('data/data.json', 'w') as fp:
        json.dump(data,fp)

def where_json_file(file_name):
    return os.path.exists(file_name)

# calculate price
def calculate_price(price):
    return price / 100000

# display full montah name. refer https://strftime.org/
def mapper(month):
   return month.strftime('%B') 

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
                #create_time.append(datetime.fromtimestamp(details['create_time']).strftime('%d-%m-%Y %H:%M:%S'))
                create_time.append(details['create_time'])
                paid_amount.append(details['paid_amount'])
                shipping_fee.append(details['shipping_fee'])
                merchandise_subtotal.append(details['merchandise_subtotal'])
                #paid_amount.append(calculate_price(details['paid_amount']))
                #shipping_fee.append(calculate_price(details['shipping_fee']))
                #merchandise_subtotal.append(calculate_price(details['merchandise_subtotal']))

        new_offset = res.json()['new_offset']

    shopee_dict["Order ID"]=order_id
    shopee_dict["Seller"]=seller
    shopee_dict["Created"]=create_time
    shopee_dict["Amount"]=merchandise_subtotal
    shopee_dict["Shipping Fee"]=shipping_fee
    shopee_dict["Total"]=paid_amount

    return shopee_dict

# create json file if not exist
def check_json():
    if( where_json_file('data/data.json')):
        pass
    else:
        print ("Please wait. This may take a while depend on transaction.")
        shopeedict = get_shopee()
        save_json_file(shopeedict)

# Display data from json file
# tabulate format refer to https://github.com/astanin/python-tabulate#table-format
def df_shopee():
    f = open('data/data.json')
    shopee_json = json.loads(f.read()) 
    df = pd.DataFrame(shopee_json)
    
    df['Amount'] = df['Amount'].apply(calculate_price)
    df['Shipping Fee'] = df['Shipping Fee'].apply(calculate_price)
    df['Total'] = df['Total'].apply(calculate_price)
    df['Created'] = pd.to_datetime(df['Created'], unit='s')

    return df

# Display purchase history
def purchase_history():
    df = df_shopee()
    df.set_index('Order ID', drop=True, inplace=True) 
    df.loc['Grand Total'] = df.sum(numeric_only=True, axis=0).apply('{:,.2f}'.format) 
    print(df.to_markdown(tablefmt='psql'))

# display pivot table by month
def purchase_by_month():
    df = df_shopee()
    df['Year'] = pd.to_datetime(df['Created'], unit='s').dt.year
    df['Month'] = pd.to_datetime(df['Created'], unit='s').apply(mapper)
    df['No_Month'] = pd.to_datetime(df['Created'], unit='s').dt.month
    df_pivot = pd.pivot_table(
        df,
        index=['No_Month','Month'],
        columns='Year',
        values='Total',
        aggfunc=np.sum, 
        fill_value=0,
        margins=True, 
        margins_name='Total').iloc[:-1,:].reset_index()
        
    df_pivot.drop('No_Month', axis=1, inplace=True)
    print(df_pivot.to_markdown(tablefmt='psql',index=False))

# purchase history in summary format
def purchase_summary():
    df = df_shopee()
    total = df.loc[:, ['Shipping Fee','Total']].sum().to_frame('Total')
    total.loc['Transaction'] = df['Order ID'].count()
    total.rename(index={'Total': 'Purchase Amount'},inplace=True)
    total = total.rename_axis('Desription').reset_index()
    print(total.to_markdown(tablefmt='psql',index=False))

# Main menu
def mainmenu():
    # Clear console
    os.system('cls' if os.name in ('nt', 'dos') else 'clear')

    while(True):
        check_json()
        print("\nMain Menu : \n")
        menu_options = {
            1: 'Purchase History',
            2: 'Purchase By Month',
            3: 'Summary',
            0: 'Exit Program',
        }

        for key in menu_options.keys():
            print (key, '--', menu_options[key] )
        
        try:
            option = int(input('\nEnter your choice: '))
        except:
            print('Wrong input. Please enter a number ...')
        if option == 1:
           purchase_history()
        elif option == 2:
           purchase_by_month()
        elif option == 3:
           purchase_summary()
        elif option == 0:
            sys.exit(0)
        else:
            print('Invalid option. Please enter a number between 1 and 4.')
    
if __name__ == "__main__":
    mainmenu()