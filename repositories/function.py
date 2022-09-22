from http import cookies
import os
import emoji
import re
import json
import requests
import browser_cookie3
import textwrap

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
def truncate_text(string,lgth):
    #return string[:75]
    return textwrap.fill(string,lgth)

#remove all in single function
def filtered_name(string,lgth):
    string = latin_character(string)
    string = remove_emoji(string)
    string = truncate_text(string,lgth)

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

def cookies_logger():
    cookies_dict = {}
    reject_cookies = ["AMP_TOKEN","G_AUTHUSER_H","G_ENABLED_IDPS"]

    try:
        cookies = list(browser_cookie3.chrome(domain_name='shopee.com.my'))
        if(len(cookies)>0):
            for i in range(len(cookies)):
                if not cookies[i].name in reject_cookies:
                    cookies_dict[cookies[i].name]=cookies[i].value
            
            return cookies_dict
    except:
        print("Error retrieving cookies.")

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
    variation=[]
    tracking_number=[]
    carrier_name=[]
    order_sn=[]

    shopee_dict={}
    new_offset=3

    while new_offset >= 0:
        url='https://shopee.com.my/api/v1/orders'
        params = {'limit':5,'order_type':3,'offset':new_offset}
        header = {
            'accept-encoding':'gzip, deflate, br',
            'accept-language':'en-GB,en-US;q=0.9,en;q=0.8,fil;q=0.7',
            'referer': 'https://shopee.com.my/user/purchase/?type=3',
            'sec-ch-ua':'"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
            'x-api-source': 'pc',
            'x-requested-with':'XMLHttpRequest',
            'x-shopee-language': 'en'
        }
        cookie = cookies_logger()

        res=requests.get(url,params,cookies=cookie,headers=header)
        data = res.json()['orders']
        
        for details in data:
            if isinstance(details, dict):
                #get purchase history
                seller.append(details['seller']['username'])
                order_id.append(details['orderid'])
                order_sn.append(details['ordersn'])
                create_time.append(details['create_time'])
                paid_amount.append(details['paid_amount'])
                shipping_fee.append(details['shipping_fee'])
                merchandise_subtotal.append(details['merchandise_subtotal'])
                tracking_number.append(details['forders'][0]['third_party_tn'])
                carrier_name.append(details['forders'][0]['carrier_name'])
                
                #get product purchase history
                for i in range(len(details['items'])):
                    item = details['items'][i]
                    if('name' in item):  
                        itemid.append(item['itemid'])
                        name.append(item['name'])
                        item_price.append(item['item_price'])
                        price_before_discount.append(item['price_before_discount'])
                        quantity.append(item['amount'])
                        if('model_name' in item):
                            variation.append(item['model_name'])
                        else:
                            variation.append('')
                    else:
                        #for purchase with bundle product
                        item_detail=item['extinfo']['bundle_order_item']['item_list']
                        for j in range(len(item_detail)):
                            itemid.append(item_detail[j]['itemid'])
                            name.append(item_detail[j]['name'])
                            item_price.append(item_detail[j]['item_price'])
                            price_before_discount.append(item_detail[j]['price_before_discount'])
                            quantity.append(item_detail[j]['amount'])
                            variation.append(item_detail[j]['model_name'])

        new_offset = res.json()['new_offset']

    #store in purchase dict key
    shopee_dict["Purchase"]={
        "Order SN": order_sn,
        "Order ID": order_id,
        "Seller": seller, 
        "Created": create_time, 
        "Tracking No": tracking_number, 
        "Carrier": carrier_name, 
        "Subtotal": merchandise_subtotal, 
        "Shipping Fee": shipping_fee, 
        "Total": paid_amount
        }

    #store in product dict key
    shopee_dict["Product"]={
        "Product ID": itemid,
        "Product Name": name, 
        "Variation": variation, 
        "Quantity": quantity, 
        "Price": price_before_discount, 
        "Final Price": item_price
        }

    return shopee_dict