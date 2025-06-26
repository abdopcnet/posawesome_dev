# Copyright (c) 2021, Youssef Restom and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import strip
import sys


class ReferralCode(Document):
    def autoname(self):
        try:
            print(
                f"[INFO] Running autoname for ReferralCode: customer={getattr(self, 'customer', '')}",
                file=sys.stdout,
            )
            if not self.referral_name:
                self.referral_name = (
                    strip(self.customer) + "-" + frappe.generate_hash()[:5].upper()
                )
                self.name = self.referral_name
            else:
                self.referral_name = strip(self.referral_name)
                self.name = self.referral_name

            if not self.referral_code:
                self.referral_code = frappe.generate_hash()[:10].upper()
        except Exception as e:
            print(f"[ERROR] Exception in autoname: {e}", file=sys.stderr)
            raise

    def validate(self):
        try:
            print(
                f"[INFO] Running validate for ReferralCode: name={getattr(self, 'name', '')}",
                file=sys.stdout,
            )
        except Exception as e:
            print(f"[ERROR] Exception in validate: {e}", file=sys.stderr)
            raise


def create_referral_code(
    company, customer, customer_offer, primary_offer=None, campaign=None
):
    try:
        print(
            f"[INFO] Creating referral code for customer={customer}", file=sys.stdout
        )
        doc = frappe.new_doc("Referral Code")
        doc.company = company
        doc.customer = customer
        doc.customer_offer = customer_offer
        doc.primary_offer = primary_offer
        doc.campaign = campaign
        doc.save(ignore_permissions=True)
        return doc
    except Exception as e:
        print(f"[ERROR] Exception in create_referral_code: {e}", file=sys.stderr)
        raise
