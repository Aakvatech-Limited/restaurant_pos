import frappe
from frappe import _
import json
import requests

@frappe.whitelist(allow_guest=True)
def get_items_by_group(item_group=None):
	"""
	Fetches items filtered by item group.
	Includes Item Name, Code, Image URL, Standard Rate, and Description.
	"""
	filters = {"show_in_website": 1}
	if item_group:
		filters["item_group"] = item_group
	
	items = frappe.get_all(
		"Item",
		filters=filters,
		fields=["name", "item_name", "item_group", "image", "standard_rate", "description"]
	)
	return items

@frappe.whitelist()
def search_or_create_customer(customer_name, tin_number=None, phone=None, email=None):
	"""
	Search for customer by phone/TIN or create a new customer.
	"""
	if phone:
		existing = frappe.get_all("Customer", filters={"mobile_no": phone}, limit=1)
		if existing:
			doc = frappe.get_doc("Customer", existing[0].name)
			if tin_number and doc.tax_id != tin_number:
				doc.tax_id = tin_number
				doc.save()
			return doc

	if tin_number:
		existing = frappe.get_all("Customer", filters={"tax_id": tin_number}, limit=1)
		if existing:
			return frappe.get_doc("Customer", existing[0].name)

	# Create new customer
	doc = frappe.new_doc("Customer")
	doc.customer_name = customer_name
	doc.customer_type = "Individual"
	doc.customer_group = "Individual"
	doc.territory = "All Territories"
	if phone:
		doc.mobile_no = phone
	if email:
		doc.email_id = email
	if tin_number:
		doc.tax_id = tin_number
	doc.insert(ignore_permissions=True)
	doc.submit()
	return doc

@frappe.whitelist()
def process_pos_checkout(items, customer_name, order_type="Take-Away", phone=None, tin_number=None, table_id=None, remarks=None):
	"""
	Deducts stock by creating a Delivery Note (without invoice).
	Supports Dine-In, Take-Away, and Delivery.
	Performs proactive peg conversions if stock is insufficient.
	"""
	items_list = json.loads(items) if isinstance(items, str) else items

	# Step 1: Resolve customer
	customer_doc = search_or_create_customer(customer_name, tin_number, phone)
	
	# Default warehouse
	warehouse = frappe.db.get_single_value("Restaurant POS Settings", "default_warehouse") or "Stores - A"

	# Step 2: Proactive Peg stock conversion check
	for item in items_list:
		check_and_convert_pegs(item["item_code"], item["qty"], warehouse)

	# Step 3: Create Delivery Note for Stock Only reduction
	dn = frappe.new_doc("Delivery Note")
	dn.customer = customer_doc.name
	dn.company = frappe.db.get_single_value("Restaurant POS Settings", "company") or frappe.get_all("Company", limit=1)[0].name
	dn.custom_order_type = order_type
	dn.custom_table = table_id
	dn.remarks = remarks

	for item in items_list:
		# Base items
		dn.append("items", {
			"item_code": item["item_code"],
			"qty": item["qty"],
			"warehouse": warehouse,
			"description": item.get("remarks") or item.get("item_name")
		})
		
		# Process dynamic extra toppings/sides as individual stock items
		if item.get("modifiers"):
			for mod in item["modifiers"]:
				dn.append("items", {
					"item_code": mod["item_code"],
					"qty": mod["qty"] * item["qty"],
					"warehouse": warehouse,
					"description": f"Modifier for {item['item_name']}"
				})

	dn.insert(ignore_permissions=True)
	dn.submit()
	
	# Send Receipt/Update via WhatsApp if number is provided
	if phone:
		send_whatsapp_invoice(dn, phone)

	return {"status": "success", "delivery_note": dn.name}

def check_and_convert_pegs(item_code, requested_qty, warehouse):
	"""
	Checks current stock. If peg stock drops to/below 0 after order preparation,
	it dynamically triggers a Repack Stock Entry converting a Full Bottle.
	"""
	# Check if this item is a Peg and has a conversion rule
	rules = frappe.get_all("Pegs Conversion Rule", filters={"peg_item": item_code}, fields=["parent_bottle_item", "conversion_factor"])
	if not rules:
		return

	rule = rules[0]
	conversion_factor = float(rule.conversion_factor or 25)
	bottle_item = rule.parent_bottle_item

	# Get current stock of peg item
	current_stock = get_stock_balance(item_code, warehouse)

	# If stock after preparation is negative
	if current_stock - float(requested_qty) < 0:
		needed_pegs = abs(current_stock - float(requested_qty))
		needed_bottles = int(needed_pegs // conversion_factor) + 1
		
		# Verify we have enough bottles to repack
		bottle_stock = get_stock_balance(bottle_item, warehouse)
		if bottle_stock < needed_bottles:
			frappe.throw(_("Insufficient stock of Bottle item {0} to perform repack for {1} Pegs").format(bottle_item, needed_pegs))

		# Perform Repack
		se = frappe.new_doc("Stock Entry")
		se.purpose = "Repack"
		se.company = frappe.db.get_single_value("Restaurant POS Settings", "company") or frappe.get_all("Company", limit=1)[0].name
		
		# Source item (Consume full bottles)
		se.append("items", {
			"item_code": bottle_item,
			"qty": needed_bottles,
			"s_warehouse": warehouse,
			"t_warehouse": None,
			"purpose": "Repack"
		})

		# Target item (Produce pegs)
		se.append("items", {
			"item_code": item_code,
			"qty": needed_bottles * conversion_factor,
			"s_warehouse": None,
			"t_warehouse": warehouse,
			"purpose": "Repack"
		})

		se.insert(ignore_permissions=True)
		se.submit()
		frappe.logger().info(f"Auto-Repacked {needed_bottles} bottles of {bottle_item} into {needed_bottles * conversion_factor} pegs of {item_code}")

def get_stock_balance(item_code, warehouse):
	"""Helper to get stock balance from bin."""
	balance = frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty")
	return float(balance or 0)

# ==========================================
# WhatsApp Notification and Order Tracking
# ==========================================

def notify_order_status_update(doc, method):
	"""Triggered on Sales Order update. Pushes live order status updates to WhatsApp."""
	if doc.flags.updater_whatsapp_notified:
		return
	
	customer_phone = frappe.db.get_value("Customer", doc.customer, "mobile_no")
	if not customer_phone:
		return

	status_msg = f"Your order {doc.name} status has been updated to: *{doc.status}*."
	trigger_whatsapp_send(customer_phone, status_msg)
	doc.flags.updater_whatsapp_notified = True

def notify_delivery_submit(doc, method):
	"""Triggered when Delivery Note is submitted."""
	customer_phone = frappe.db.get_value("Customer", doc.customer, "mobile_no")
	if not customer_phone:
		return
	
	msg = f"Thank you! Your delivery note {doc.name} has been processed and items are out for dispatch."
	trigger_whatsapp_send(customer_phone, msg)

def send_whatsapp_invoice(dn_doc, phone):
	"""Formats and sends invoice details to customer WhatsApp."""
	msg = f"Hello {dn_doc.customer},\nYour invoice {dn_doc.name} details:\n"
	for item in dn_doc.items:
		msg += f"- {item.item_code}: {item.qty} pcs\n"
	msg += "\nEnjoy your meal!"
	trigger_whatsapp_send(phone, msg)

def trigger_whatsapp_send(phone, text):
	"""Sends message using the configured gateway (Meta Cloud API / Twilio)."""
	settings = frappe.get_single("Restaurant POS Settings")
	gateway = settings.whatsapp_gateway or "Meta"
	
	if gateway == "Meta":
		# Meta API configurations
		url = f"https://graph.facebook.com/v15.0/{settings.meta_phone_number_id}/messages"
		headers = {
			"Authorization": f"Bearer {settings.meta_access_token}",
			"Content-Type": "application/json"
		}
		data = {
			"messaging_product": "whatsapp",
			"to": phone,
			"type": "text",
			"text": {"body": text}
		}
		try:
			response = requests.post(url, json=data, headers=headers, timeout=10)
			response.raise_for_status()
		except Exception as e:
			frappe.logger().error(f"WhatsApp Meta Send Error: {e}")
	else:
		# Twilio API configurations
		url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_sid}/Messages.json"
		auth = (settings.twilio_sid, settings.twilio_auth_token)
		data = {
			"From": f"whatsapp:{settings.twilio_whatsapp_number}",
			"To": f"whatsapp:{phone}",
			"Body": text
		}
		try:
			response = requests.post(url, data=data, auth=auth, timeout=10)
			response.raise_for_status()
		except Exception as e:
			frappe.logger().error(f"WhatsApp Twilio Send Error: {e}")
