
import pandas as pd
import numpy as np
from repositories import function

# Display data from json file
# tabulate format refer to https://github.com/astanin/python-tabulate#table-format
def df_shopee_purchase():
    shopee = function.load_json()
    df = pd.DataFrame(shopee['Purchase'])
    
    df['Subtotal'] = df['Subtotal'].apply(function.calculate_price)
    df['Shipping Fee'] = df['Shipping Fee'].apply(function.calculate_price)
    df['Total'] = df['Total'].apply(function.calculate_price)
    df['Created'] = pd.to_datetime(df['Created'], unit='s')

    return df

#get data from purchase dict key
def df_shopee_product():
    shopee = function.load_json()
    df = pd.DataFrame(shopee['Product'])
    
    df['Product Name'] = df['Product Name'].apply(function.accepted_product_name)
    #df['Product Name'] = df['Product Name'].str.slice(0,75)
    df['Price'] = list(map(function.has_original_price,df['Price'],df['Final Price']))
    df['Final Price'] = df['Final Price'].apply(function.calculate_price)
    df['Discount'] = list(map(function.calculate_discount, df['Price'], df['Final Price']))
    #re-arrange column
    df = df.reindex(columns=['Product ID','Product Name','Quantity','Price','Discount','Final Price'])

    return df

# Display purchase history
def purchase_history():
    df = df_shopee_purchase()
    #set new index and drop default index
    df.set_index('Order SN', drop=True, inplace=True) 
    #add empty row
    df.loc[''] = [np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN]
    #sum all numeric column 
    df.loc['Grand Total'] = df.sum(numeric_only=True, axis=0) #.apply('{:,.2f}'.format) 
    #remove all nan value
    df.replace({np.nan: None}, inplace = True)
    print(df.to_markdown(tablefmt='psql',floatfmt=',.2f'))

# display pivot table by month
def purchase_by_month():
    df = df_shopee_purchase()
    #convert from timestamp to datetime to get year and month
    df['Year'] = pd.to_datetime(df['Created'], unit='s').dt.year
    df['Month'] = pd.to_datetime(df['Created'], unit='s').apply(function.mapper)
    #get month index to sorting
    df['No_Month'] = pd.to_datetime(df['Created'], unit='s').dt.month
    #pivot table. remove last row of total and reset the index to drop later
    df_pivot = pd.pivot_table(
        df,
        index=['No_Month','Month'],
        columns='Year',
        values='Total',
        aggfunc=np.sum, 
        fill_value=0,
        margins=True, 
        margins_name='Total').iloc[:-1,:].reset_index() 
  
    #drop column
    df_pivot.drop('No_Month', axis=1, inplace=True)
    print(df_pivot.to_markdown(tablefmt='psql',floatfmt=',.2f',index=False))

# purchase history in summary format
def purchase_summary():
    df = df_shopee_purchase()
    df_product = df_shopee_product()
    #select specific column to sum and rename column header
    total = df.loc[:, ['Shipping Fee','Total']].sum().to_frame('Total')

    #add new row for different calculation
    total.loc['Highest Shipping Fee'] = df['Shipping Fee'].max()
    total.loc['Highest Purchase Amount'] = df['Total'].max()
    total.loc['Lowest Purchase Amount'] = df['Total'].min()
    total.loc['Highest Product Price'] = df_product['Final Price'].max()
    total.loc['Lowest Product Price'] = df_product['Final Price'].min()
    total.loc['Highest Product Quantity'] = df_product['Quantity'].max()
    total.loc['Total Purchase Transaction'] = df['Order ID'].count()
    total.loc['Total Product Transaction'] = df_product['Product ID'].count()

    #rename index value
    total.rename(index={'Shipping Fee': 'Total Shipping Fee'},inplace=True)
    total.rename(index={'Total': 'Total Purchase Amount'},inplace=True)
    #rename index header and reset
    total = total.rename_axis('Desription').reset_index()
    print(total.to_markdown(tablefmt='grid',floatfmt=',.2f',index=False))

def puchase_by_seller():
    df = df_shopee_purchase()
    #group by seller, calculate total sum and count transaction
    df_seller = df.groupby('Seller')['Total'].agg(Total='sum', Transaction='count')
    print(df_seller.to_markdown(tablefmt='psql',floatfmt=',.2f'))

def product_purchase_history():
    df = df_shopee_product()
    print(df.to_markdown(tablefmt='psql',floatfmt=',.2f'))