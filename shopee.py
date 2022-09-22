
import sys
from repositories import function
from repositories import datatable

#display menu option
def display_menu():
    menu_options = {
        1: 'Purchase History',
        2: 'Purchase History Pivot By Month and Year',
        3: 'Summary',
        4: 'Purchase History Group By Seller',
        5: 'Product Purchase History',
        6: 'Transaction Group By Courier',
        0: 'Exit Program',
    }

    print("-----------------------------------------------------------------")
    #print("Before you continue, make sure that you logged in to shopee.com.my using google chrome browser\n")
    print("Main Menu\n")
    for key in menu_options.keys():
        print (key, '--', menu_options[key] )

# Main menu
def main():
    function.check_json()
    function.cls()
    while(True):
        #cls()
        display_menu()
        
        try:
            option = int(input('\nEnter your choice: '))
        except:
            print('Wrong input. Please enter a number ...')
        if option == 1:
           datatable.purchase_history()
        elif option == 2:
           datatable.purchase_by_month()
        elif option == 3:
           datatable.purchase_summary()
        elif option == 4:
           datatable.purchase_by_seller()
        elif option == 5:
           datatable.product_purchase_history()
        elif option == 6:
           datatable.purchase_by_carrier()
        elif option == 0:
            sys.exit(0)
        else:
            print('Invalid option. Please enter a number between 1 and 5.')
    
if __name__ == "__main__":
    main()