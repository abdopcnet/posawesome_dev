# -*- coding: utf-8 -*-
# Copyright (c) 2021, Youssef Restom and contributors
# For license information, please see license.txt


from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, add_days
from posawesome.posawesome.doctype.pos_coupon.pos_coupon import update_coupon_code_count
from posawesome.posawesome.api.posapp import get_company_domain
from posawesome.posawesome.doctype.delivery_charges.delivery_charges import (
    get_applicable_delivery_charges,
)


def validate(doc, method):
    validate_shift(doc)
    set_patient(doc)
    auto_set_delivery_charges(doc)
    calc_delivery_charges(doc)


def before_submit(doc, method):
    add_loyalty_point(doc)
    update_coupon(doc, "used")


def before_cancel(doc, method):
    update_coupon(doc, "cancelled")


def add_loyalty_point(invoice_doc):
    for offer in invoice_doc.posa_offers:
        if offer.offer == "Loyalty Point":
            original_offer = frappe.get_doc("POS Offer", offer.offer_name)
            if original_offer.loyalty_points > 0:
                loyalty_program = frappe.get_value(
                    "Customer", invoice_doc.customer, "loyalty_program"
                )
                if not loyalty_program:
                    loyalty_program = original_offer.loyalty_program
                doc = frappe.get_doc(
                    {
                        "doctype": "Loyalty Point Entry",
                        "loyalty_program": loyalty_program,
                        "loyalty_program_tier": original_offer.name,
                        "customer": invoice_doc.customer,
                        "invoice_type": "Sales Invoice",
                        "invoice": invoice_doc.name,
                        "loyalty_points": original_offer.loyalty_points,
                        "expiry_date": add_days(invoice_doc.posting_date, 10000),
                        "posting_date": invoice_doc.posting_date,
                        "company": invoice_doc.company,
                    }
                )
                doc.insert(ignore_permissions=True)


def update_coupon(doc, transaction_type):
    for coupon in doc.posa_coupons:
        if not coupon.applied:
            continue
        update_coupon_code_count(coupon.coupon, transaction_type)


def set_patient(doc):
    domain = get_company_domain(doc.company)
    if domain != "Healthcare":
        return
    patient_list = frappe.get_all(
        "Patient", filters={"customer": doc.customer}, page_length=1
    )
    if len(patient_list) > 0:
        doc.patient = patient_list[0].name


def auto_set_delivery_charges(doc):
    if not doc.pos_profile:
        return
    if not frappe.get_cached_value(
        "POS Profile", doc.pos_profile, "posa_auto_set_delivery_charges"
    ):
        return

    delivery_charges = get_applicable_delivery_charges(
        doc.company,
        doc.pos_profile,
        doc.customer,
        doc.shipping_address_name,
        doc.posa_delivery_charges,
        restrict=True,
    )

    if doc.posa_delivery_charges:
        if doc.posa_delivery_charges_rate:
            return
        else:
            if len(delivery_charges) > 0:
                doc.posa_delivery_charges_rate = delivery_charges[0].rate
    else:
        if len(delivery_charges) > 0:
            doc.posa_delivery_charges = delivery_charges[0].name
            doc.posa_delivery_charges_rate = delivery_charges[0].rate
        else:
            doc.posa_delivery_charges = None
            doc.posa_delivery_charges_rate = None


def calc_delivery_charges(doc):
    if not doc.pos_profile:
        return

    old_doc = None
    calculate_taxes_and_totals = False
    if not doc.is_new():
        old_doc = doc.get_doc_before_save()
        if not doc.posa_delivery_charges and not old_doc.posa_delivery_charges:
            return
    else:
        if not doc.posa_delivery_charges:
            return
    if not doc.posa_delivery_charges:
        doc.posa_delivery_charges_rate = 0

    charges_doc = None
    if doc.posa_delivery_charges:
        charges_doc = frappe.get_cached_doc(
            "Delivery Charges", doc.posa_delivery_charges
        )
        doc.posa_delivery_charges_rate = charges_doc.default_rate
        charges_profile = next(
            (i for i in charges_doc.profiles if i.pos_profile == doc.pos_profile), None
        )
        if charges_profile:
            doc.posa_delivery_charges_rate = charges_profile.rate

    if old_doc and old_doc.posa_delivery_charges:
        old_charges = next(
            (
                i
                for i in doc.taxes
                if i.charge_type == "Actual"
                and i.description == old_doc.posa_delivery_charges
            ),
            None,
        )
        if old_charges:
            doc.taxes.remove(old_charges)
            calculate_taxes_and_totals = True

    if doc.posa_delivery_charges:
        doc.append(
            "taxes",
            {
                "charge_type": "Actual",
                "description": doc.posa_delivery_charges,
                "tax_amount": doc.posa_delivery_charges_rate,
                "cost_center": charges_doc.cost_center,
                "account_head": charges_doc.shipping_account,
            },
        )
        calculate_taxes_and_totals = True

    if calculate_taxes_and_totals:
        doc.calculate_taxes_and_totals()


def validate_shift(doc):
    try:
        frappe.logger().info(f'[invoice.py] validate_shift called for doc: {getattr(doc, "name", None)}')
        if doc.posa_pos_opening_shift and doc.pos_profile and doc.is_pos:
            # check if shift is open
            shift = frappe.get_cached_doc("POS Opening Shift", doc.posa_pos_opening_shift)
            frappe.logger().info(f'[invoice.py] Checking shift: {shift.name}, status: {shift.status}')
            if shift.status != "Open":
                frappe.logger().error(f'[invoice.py] POS Shift {shift.name} is not open')
                frappe.throw(_("POS Shift {0} is not open").format(shift.name))
            # check if shift is for the same profile
            if shift.pos_profile != doc.pos_profile:
                frappe.logger().error(f'[invoice.py] POS Opening Shift {shift.name} is not for the same POS Profile')
                frappe.throw(
                    _("POS Opening Shift {0} is not for the same POS Profile").format(
                        shift.name
                    )
                )
            # check if shift is for the same company
            if shift.company != doc.company:
                frappe.logger().error(f'[invoice.py] POS Opening Shift {shift.name} is not for the same company')
                frappe.throw(
                    _("POS Opening Shift {0} is not for the same company").format(
                        shift.name
                    )
                )
    except Exception as e:
        frappe.logger().error(f'[invoice.py] Error in validate_shift: {e}')
        raise
