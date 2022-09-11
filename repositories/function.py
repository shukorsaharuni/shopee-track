import os
import emoji
import re
import json
import requests
import configparser

# Save data to json file
def save_json_file(data):
    with open('data/data.json', 'w') as fp:
        json.dump(data,fp)

def where_json_file(file_name):
    return os.path.exists(file_name)

def load_json():
    f = open('data/data.json')
    return json.loads(f.read()) 

# calculate price
def calculate_price(price):
    return price / 100000

# calculate discount
def calculate_discount(original_price,discount_price):
    return original_price - discount_price

# check if price have value
def has_original_price(original_price,item_price):
    if(original_price > 0):
        return calculate_price(original_price)
    else:
        return calculate_price(item_price)

#remove emoji
def remove_emoji(string):
    return emoji.replace_emoji(string, '')

#remove all character that isn't latin
def latin_character(string):
    regex = re.compile('[^\u0020-\u024F]')
    string = regex.sub('', string)
    return string

#truncate long text
def truncate_text(string):
    return string[:75]

#remove all in single function
def accepted_product_name(string):
    string = latin_character(string)
    string = remove_emoji(string)
    string = truncate_text(string)

    return string

# display full montah name. refer https://strftime.org/
def mapper(month):
   return month.strftime('%B') 

def cls():
    os.system('cls' if os.name in ('nt', 'dos') else 'clear')

# create json file if not exist
def check_json():
    if( where_json_file('data/data.json')):
        pass
    else:
        print ("Please wait. This may take a while depend on transaction.")
        shopeedict = get_shopee()
        save_json_file(shopeedict)

# Get shopee information from cookies
def get_shopee():
    seller=[]
    order_id=[]
    create_time=[]
    paid_amount=[]
    shipping_fee=[]
    merchandise_subtotal=[]
    itemid=[]
    name=[]
    item_price=[]
    price_before_discount=[]
    quantity=[]

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
                #get purchase history
                seller.append(details['seller']['username'])
                order_id.append(details['ordersn'])
                create_time.append(details['create_time'])
                paid_amount.append(details['paid_amount'])
                shipping_fee.append(details['shipping_fee'])
                merchandise_subtotal.append(details['merchandise_subtotal'])
                
                #get product purchase history
                for i in range(len(details['items'])):
                    item = details['items'][i]
                    if('name' in item):  
                        itemid.append(item['itemid'])
                        name.append(item['name'])
                        item_price.append(item['item_price'])
                        price_before_discount.append(item['price_before_discount'])
                        quantity.append(item['amount'])
                    else:
                        #for purchase with bundle product
                        item_detail=item['extinfo']['bundle_order_item']['item_list']
                        for j in range(len(item_detail)):
                            itemid.append(item_detail[j]['itemid'])
                            name.append(item_detail[j]['name'])
                            item_price.append(item_detail[j]['item_price'])
                            price_before_discount.append(item_detail[j]['price_before_discount'])
                            quantity.append(item_detail[j]['amount'])

        new_offset = res.json()['new_offset']

    #store in purchase dict key
    shopee_dict["Purchase"]={
        "Order ID": order_id,
        "Seller": seller, 
        "Created": create_time, 
        "Subtotal": merchandise_subtotal, 
        "Shipping Fee": shipping_fee, 
        "Total": paid_amount
        }

    #store in product dict key
    shopee_dict["Product"]={
        "Product ID": itemid,
        "Product Name": name, 
        "Quantity": quantity, 
        "Price": price_before_discount, 
        "Final Price": item_price
        }

    return shopee_dict