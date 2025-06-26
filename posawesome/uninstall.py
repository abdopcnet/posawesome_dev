import frappe


def after_uninstall():
    try:
        print("[INFO] Running after_uninstall...")
        clear_custom_fields_and_properties()
    except Exception as e:
        print(f"[ERROR] Exception in after_uninstall: {e}")
        raise


def clear_custom_fields_and_properties():
    try:
        print("[INFO] Clearing custom fields and property setters...")
        fixtures = frappe.get_hooks("fixtures", app_name="posawesome")
        for fixture in fixtures:
            if fixture.get("doctype") == "Custom Field":
                filters = fixture.get("filters")
                if filters:
                    for filter in filters:
                        frappe.db.delete("Custom Field", filter)
                        print("[INFO] Deleted Custom Fields: ", filter)
            if fixture.get("doctype") == "Property Setter":
                filters = fixture.get("filters")
                if filters:
                    for filter in filters:
                        frappe.db.delete("Property Setter", filter)
                        print("[INFO] Deleted Property Setter: ", filter)

        frappe.db.commit()
        print("[INFO] Database commit done.")
    except Exception as e:
        print(f"[ERROR] Exception in clear_custom_fields_and_properties: {e}")
        raise
