import frappe
import json
from frappe.permissions import add_permission

#api/method/pos_api_app.pos_api_app.api.api.update_or_insert_user_role
# add new role 
@frappe.whitelist()
def update_or_insert_user_role():
    try:
        role = frappe.get_all('Role',{'name':'Franchise Data API role'})
        if not role:
            new_role = frappe.get_doc({
                'doctype': 'Role',
                'role_name':'Franchise Data API role',
                'bulk_actions':1
            })
            
            # Insert the new role
            new_role.insert()
            frappe.db.commit()
            # Insert the new role
            new_role.insert()
            frappe.db.commit()
    except Exception:
        pass

    return {"message": "successfull"}



#api/method/pos_api_app.pos_api_app.api.api.add_roles_per_doctype
# add doctype read permission to that role 
@frappe.whitelist()
def add_roles_per_doctype():
    doctypes=["Item","POS Invoice","Sales Invoice","Customer"]
    for doc in doctypes:
        try:
            frappe.only_for("System Manager")
            add_permission(doc,"Franchise Data API role",0)
            frappe.db.commit()
        except Exception:
            pass
    return {"message": "successfull"}


#api/method/pos_api_app.pos_api_app.api.api.create_franchise_user
# add franchise user 
@frappe.whitelist()
def create_franchise_user():
    try:
        # Fetch the user by email
        user = frappe.get_all('User', {'email': "franchise_user@jibu.com"})
        
        if not user:
            # User does not exist, insert a new user
            new_user = frappe.get_doc({
                'doctype': 'User',
                'first_name': "Franchise User",
                'email': "franchise_user@jibu.com",
                'enabled': 1,
                'send_welcome_email':0,
                'roles': [{
                    "parent": "franchise_user@jibu.com",
                    "parentfield": "roles",
                    "parenttype": "User",
                    "role": "Franchise Data API role"
                }]
            })
            
            # Insert the new user
            new_user.insert()
            frappe.db.commit()
    except Exception:
        pass
    return {"message": "successfull"}
        


#api/method/pos_api_app.pos_api_app.api.api.after_install
# after install the app create user and role
@frappe.whitelist()
def after_install():
    update_or_insert_user_role()
    create_franchise_user()
    return {"message": "successfull"}


#api/method/pos_api_app.pos_api_app.api.api.post_pos_data
# Send Doctypes data to master app
@frappe.whitelist()
def post_pos_data():
    customer_groups = fetch_customer_group()

    customers = fetch_customer()
    
    item_groups = fetch_item_group()

    items =  fetch_item()

    [expenses_entry , expenses_items] = fetch_expenses_entry()

    meter_reading = fetch_meter_reading()

    [damaged_bottles, damaged_bottle_items] = fetch_damaged_bottles()

    [stock_entry , stock_entry_detail] = fetch_stock_entry()
    
    [pos_invoices,pos_invoice_items,sales_invoices,sales_invoice_packed_items,sales_invoice_items] =  fetch_pos_sales_invoice()

    return {"item_group":item_groups,"item":items,'customer_group':customer_groups, 'customer':customers,"pos_invoice":pos_invoices,"pos_invoice_item":pos_invoice_items,"sales_invoice":sales_invoices,"packed_item":sales_invoice_packed_items,"sales_invoice_item":sales_invoice_items ,"expenses_entry":expenses_entry , "expenses_item":expenses_items , "meter_reading":meter_reading , "damaged_bottles":damaged_bottles , "damaged_bottle_items":damaged_bottle_items , "stock_entry":stock_entry , "stock_entry_detail":stock_entry_detail}


customer_fields = ['customer_name', 'customer_type', 'customer_group', 'territory', 'type_of_customer', 'account_manager', 'address_description', 
                   'average_purchase_time', 'default_commission_rate', 'credit_status', 'default_price_list', 'disabled', 'posa_discount', 'email_id', 
                   'first_purchase_date', 'lead_name', 'gender', 'gps_location', 'last_purchase_date', 'lead_source', 'loyalty_program', 'loyalty_program_tier', 
                   'market_segment', 'mobile_no', 'next_projected_purchase_date', 'outstanding_amount', 'pending_bottles', 'pending_bottles_count', 
                   'primary_address', 'posa_referral_company', 'default_sales_partner', 'time_since_last_purchase', 'status', 'creation', 'modified', 'name']


def fetch_customer():
    all_customers = frappe.db.get_all("Customer", fields=customer_fields,order_by="creation")
    return all_customers



#fetch Customer Group List
def fetch_customer_group():     
    customer_groups = frappe.db.get_all("Customer Group", fields=["*"],order_by="creation")
    return customer_groups

#fetch Item Group List
def fetch_item_group():
    item_groups = frappe.db.get_all("Item Group", fields=["*"],order_by="creation")
    return item_groups

#fetch Item List
def fetch_item():
    item_list = frappe.get_all("Item", fields=["stock_uom","item_group","disabled","name","item_code","item_name","description","creation","modified"],order_by="creation")
    return item_list



pos_invoice_fields = ['company', 'currency', 'posting_date', 'grand_total', 'selling_price_list', 'discount_amount', 'additional_discount_percentage',
                        'amount_eligible_for_commission', 'coupon_code', 'current_loyalty_points', 'customer_group','customer', 'customer_name', 'delivery_date',
                        'is_discounted', 'is_opening', 'is_return', 'loyalty_amount', 'loyalty_points', 'loyalty_program', 'contact_mobile',
                        'mpesa_receipt_number', 'net_total', 'delivery_option_status', 'previous_outstanding_amount', 'paid_amount', 'due_date',
                        'picking_date', 'pos_profile', 'posting_time', 'redeem_loyalty_points', 'remarks', 'return_against', 'status'
                        , 'territory', 'delivered_by', 'picked_by', 'to_date', 'total', 'total_qty', 'total_taxes_and_charges', 'name', 'creation', 'modified']

sales_invoice_fields = ['company', 'currency', 'posting_date', 'grand_total', 'selling_price_list', 'discount_amount', 'additional_discount_percentage', 
                        'amount_eligible_for_commission', 'customer_group','customer','customer_name', 'net_total', 'outstanding_amount', 'paid_amount', 'due_date', 
                        'pos_profile', 'posting_time', 'redeem_loyalty_points', 'remarks', 'rounded_total', 'status', 'territory', 'total', 'total_qty', 
                        'total_taxes_and_charges','name', 'creation', 'modified']


#fetch POS Invoice,POS Invoice Item, Sales Invoice, Sales Invoice Item List
def fetch_pos_sales_invoice():
    # Fetch POS Invoices and Sales Invoice Payments in a single query to minimize database hits
    pos_invoice_list = frappe.get_all("POS Invoice", fields=pos_invoice_fields, order_by="creation")
    sales_invoice_payments = frappe.db.get_all("Sales Invoice Payment", fields=["parent", "name", "account", "amount", "default", "mode_of_payment", "type"])
    
    # Create a dictionary mapping parent to its payment for quick lookup
    sales_invoice_payment_dict = {payment['parent']: payment for payment in sales_invoice_payments}
    
    # Process POS Invoices and attach payment data
    pos_invoice_dict = {pos_invoice['name']: pos_invoice for pos_invoice in pos_invoice_list}
    
    # Attach payment data to POS Invoices
    for pos_invoice in pos_invoice_list:
        payment_data = sales_invoice_payment_dict.get(pos_invoice['name'], {})
        pos_invoice_dict[pos_invoice['name']].update({
            'id_sales_invoice_payment': payment_data.get("name"),
            'account_sales_invoice_payment': payment_data.get("account"),
            'amount_sales_invoice_payment': payment_data.get("amount", 0),
            'default_sales_invoice_payment': payment_data.get("default"),
            'mode_of_payment_sales_invoice_payment': payment_data.get("mode_of_payment"),
            'type_sales_invoice_payment': payment_data.get("type"),
        })
    
    # Fetch POS Invoice Items
    pos_invoice_items = frappe.db.get_all("POS Invoice Item", fields=["name", "parent", "amount", "description", "item_name", "rate", "uom", "discount_percentage", "discount_amount", "item_code", "item_group", "net_amount", "net_rate", "price_list_rate", "qty", "stock_uom", "creation", "modified"], order_by="creation")
    
    # Update company for each item
    for item in pos_invoice_items:
        item['company'] = pos_invoice_dict.get(item['parent'], {}).get('company')
    
    # Fetch Sales Invoices and Sales Invoice Payments in a single query to minimize database hits
    sales_invoice_list = frappe.get_all("Sales Invoice", fields=sales_invoice_fields, order_by="creation")
    sales_invoice_packed_items = frappe.db.get_all("Packed Item", fields=["description", "warehouse", "item_name", "item_code", "ordered_qty", "packed_qty", "parent_detail_docname", "qty", "name", "parent","parent_item", "creation", "modified"], order_by="creation")
    sales_invoice_items = frappe.db.get_all("Sales Invoice Item", ["name", "parent", "amount", "description", "item_name", "rate", "uom", "discount_percentage", "discount_amount", "item_code", "item_group", "net_amount", "net_rate", "price_list_rate", "qty", "stock_uom", "creation", "modified"], order_by="creation")

    # Process Sales Invoices and attach payment data
    sales_invoice_dict = {sales_invoice['name']: sales_invoice for sales_invoice in sales_invoice_list}
    
    # Attach payment data to Sales Invoices
    for sales_invoice in sales_invoice_list:
        payment_data = sales_invoice_payment_dict.get(sales_invoice['name'], {})
        sales_invoice_dict[sales_invoice['name']].update({
            'id_sales_invoice_payment': payment_data.get("name"),
            'account_sales_invoice_payment': payment_data.get("account"),
            'amount_sales_invoice_payment': payment_data.get("amount", 0),
            'default_sales_invoice_payment': payment_data.get("default"),
            'mode_of_payment_sales_invoice_payment': payment_data.get("mode_of_payment"),
            'type_sales_invoice_payment': payment_data.get("type"),
        })
    
    # Update company for each packed item
    for item in sales_invoice_packed_items:
        item['company'] = sales_invoice_dict.get(item['parent'], {}).get('company')

    # Update company for each Sales Invoice item
    for item in sales_invoice_items:
        item['company'] = sales_invoice_dict.get(item['parent'], {}).get('company')
        
    return [pos_invoice_list, list(pos_invoice_items), sales_invoice_list, list(sales_invoice_packed_items),list(sales_invoice_items)]


# Expenses Entry and Expenses Item
expenses_entry_fields = ['company', 'posting_date' , 'is_payment' ,'book_an_expense' , 'mode_of_payment' ,'liability_or_asset_account' ,'payment_currency', 'project', 'default_cost_center', 'total' , 'name' , 'creation' , 'modified']

expenses_item_fields = ['account' , 'qty' ,'rate' , 'description' ,'project' ,'cost_center', 'account_currency', 'amount', 'parent','party_type' , 'name' , 'creation' , 'modified']

# Fetch Expenses Entry
def fetch_expenses_entry():
    expenses_entry_list = frappe.get_all("Expenses Entry", fields=expenses_entry_fields, order_by="creation")
    expenses_items = frappe.db.get_all("Expenses Item", fields=expenses_item_fields, order_by="creation")

    # Update company for each expenses item
    expenses_dict = {expense['name']: expense for expense in expenses_entry_list}
    for item in expenses_items:
        item['company'] = expenses_dict.get(item['parent'], {}).get('company')
    
    return [expenses_entry_list, list(expenses_items)]


# Fetch Meter Reading
def fetch_meter_reading():
    meter_reading = frappe.get_all("Meter Reading" , fields=['company' , 'posting_date' , 'opening_meter_reading' ,'closing_meter_reading', 'total' , 'name' , 'creation' , 'modified'], order_by="creation")
    return meter_reading

# Fetch Damaged Bottles and Damaged bottle items
def fetch_damaged_bottles():
    damaged_bottles = frappe.get_all("Damaged Bottles" , fields=['company', 'warehouse', 'posted_by' , 'posting_date' , 'name' , 'creation' , 'modified'],  order_by="creation")
    damaged_bottle_items = frappe.db.get_all("Damaged Bottle Items", fields=['bottle_type' , 'item_code' , 'type_of_damage' , 'qty', 'remarks' ,'warehouse' , 'parent', 'name' , 'creation' , 'modified' ], order_by="creation")

    # Update company for each Damaged Bottle Item
    damaged_bottles_dict = {damaged_bottle['name']: damaged_bottle for damaged_bottle in damaged_bottles}
    for item in damaged_bottle_items:
        item['company'] = damaged_bottles_dict.get(item['parent'], {}).get('company')

    return [damaged_bottles , list(damaged_bottle_items)]


# Stock Entry and Stock Entry Detail
stock_entry_fields = ['naming_series', 'stock_entry_type','purpose','customer','pending_bottle_ref','damaged_bottle','type_of_damage','from_warehouse','to_warehouse','posting_date','posting_time','remarks','supplier','supplier_name','company', 'name' , 'creation' , 'modified']

stock_entry_detail_fields = ['item_code','qty','amount','basic_rate','batch_no','description','expense_account','item_group','item_name','s_warehouse','t_warehouse','parent', 'name' , 'creation' , 'modified' , 'serial_no']


def fetch_stock_entry():
    stock_entry = frappe.get_all("Stock Entry" , fields=stock_entry_fields,  order_by="creation")
    stock_entry_detail = frappe.db.get_all("Stock Entry Detail", fields=stock_entry_detail_fields, order_by="creation")

    # Update company for each Stock Entry Detail
    stock_entry_dict = {stock_entry['name']: stock_entry for stock_entry in stock_entry}
    for entry in stock_entry_detail:
        entry['company'] = stock_entry_dict.get(entry['parent'], {}).get('company')

    return [stock_entry , list(stock_entry_detail)]