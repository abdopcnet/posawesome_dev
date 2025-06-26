# Copyright (c) 2022, Youssef Restom and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json
from frappe.model.document import Document


class DeliveryCharges(Document):
    def validate(self):
        print(f"[INFO] validate called for DeliveryCharges: {self.name if hasattr(self, 'name') else ''}")
        try:
            if not self.default_rate or self.default_rate <= 0:
                print(f"[ERROR] Default Rate is required or <= 0")
                frappe.throw(_("Default Rate is required"))
            self.validate_profiles()
        except Exception as e:
            print(f"[ERROR] Exception in validate: {e}")
            raise

    def validate_profiles(self):
        print(f"[INFO] validate_profiles called for DeliveryCharges: {self.name if hasattr(self, 'name') else ''}")
        try:
            profiles = []
            for row in self.profiles:
                if row.pos_profile not in profiles:
                    profiles.append(row.pos_profile)
                else:
                    print(f"[ERROR] Duplicate POS Profile in Delivery Charges: {row.pos_profile}")
                    frappe.throw("Duplicate POS Profile in Delivery Charges")
            self.set_profiles_list(profiles)
        except Exception as e:
            print(f"[ERROR] Exception in validate_profiles: {e}")
            raise

    def set_profiles_list(self, profiles_list):
        print(f"[INFO] set_profiles_list called with profiles_list: {profiles_list}")
        try:
            if len(profiles_list) > 0:
                self.profiles_list = json.dumps(profiles_list)
            else:
                self.profiles_list = None
        except Exception as e:
            print(f"[ERROR] Exception in set_profiles_list: {e}")
            raise


def get_applicable_delivery_charges(
    company,
    pos_profile=None,
    customer=None,
    address=None,
    delivery_charges=None,
    restrict=False,
):
    print(f"[INFO] get_applicable_delivery_charges called with company={company}, pos_profile={pos_profile}, customer={customer}, address={address}, delivery_charges={delivery_charges}, restrict={restrict}")
    try:
        charges = []
        address_list = []
        delivery_charges_list = []
        if address:
            address_list.append(address)
        if customer:
            address_list.extend(
                frappe.get_all(
                    "Dynamic Link",
                    filters={
                        "link_doctype": "Customer",
                        "link_name": customer,
                        "parentfield": "links",
                        "parenttype": "Address",
                    },
                    pluck="parent",
                )
            )
        for address in address_list:
            address_charges = frappe.get_cached_value(
                "Address", address, "posa_delivery_charges"
            )
            if address_charges:
                delivery_charges_list.append(address_charges)

        delivery_charges_filters = {"disabled": 0, "company": company}
        if delivery_charges:
            delivery_charges_list.append(delivery_charges)

        if len(delivery_charges_list) > 0:
            delivery_charges_filters["name"] = ["in", delivery_charges_list]
        if restrict:
            delivery_charges_filters["profiles_list"] = ["not in", ["", None]]

        delivery_charges_items = frappe.get_all(
            "Delivery Charges",
            filters=delivery_charges_filters,
            fields=["*"],
        )
        delivery_charges_list = [i.name for i in delivery_charges_items]

        delivery_profiels_filters = {"parent": ("in", delivery_charges_list)}
        if pos_profile:
            delivery_profiels_filters["pos_profile"] = pos_profile
        delivery_profiels = frappe.get_all(
            "Delivery Charges POS Profile",
            filters=delivery_profiels_filters,
            fields=["*"],
        )
        for charge in delivery_charges_items:
            profile = next((i for i in delivery_profiels if i.parent == charge.name), None)
            if profile:
                charge.rate = profile.rate
                charges.append(charge)
            else:
                if not restrict:
                    if not charge.profiles_list:
                        charge.rate = charge.default_rate
                        charges.append(charge)

        print(f"[INFO] Applicable delivery charges: {[c.name for c in charges]}")
        return charges
    except Exception as e:
        print(f"[ERROR] Exception in get_applicable_delivery_charges: {e}")
        raise
