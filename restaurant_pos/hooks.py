app_name = "restaurant_pos"
app_title = "Restaurant POS"
app_publisher = "Aakvatech"
app_description = "A premium Restaurant POS custom app for ERPNext v15 using Frappe UI"
app_email = "info@aakvatech.com"
app_license = "mit"

# Document Events
# Hook order update events to trigger WhatsApp tracking notifications
doc_events = {
	"Sales Order": {
		"on_update": "restaurant_pos.api.notify_order_status_update"
	},
	"Delivery Note": {
		"on_submit": "restaurant_pos.api.notify_delivery_submit"
	}
}

# Website Configurations
website_route_rules = [
	{"from_route": "/menu", "to_route": "menu"}
]

# Fixtures for custom print formats, roles, and settings
fixtures = [
	"Custom Field",
	"Property Setter",
	"Print Format"
]
