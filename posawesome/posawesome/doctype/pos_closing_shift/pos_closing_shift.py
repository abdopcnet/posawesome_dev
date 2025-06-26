# -*- coding: utf-8 -*-
# Copyright (c) 2020, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class POSClosingShift(Document):
    def validate(self):
        print(f"[INFO] validate called for POSClosingShift: {self.name if hasattr(self, 'name') else ''}")
        try:
            user = frappe.get_all(
                "POS Closing Shift",
                filters={
                    "user": self.user,
                    "docstatus": 1,
                    "pos_opening_shift": self.pos_opening_shift,
                    "name": ["!=", self.name],
                },
            )

            if user:
                print(f"[ERROR] POS Closing Shift already exists for user: {self.user}")
                frappe.throw(
                    _(
                        "POS Closing Shift {} against {} between selected period".format(
                            frappe.bold("already exists"), frappe.bold(self.user)
                        )
                    ),
                    title=_("Invalid Period"),
                )

            if (
                frappe.db.get_value("POS Opening Shift", self.pos_opening_shift, "status")
                != "Open"
            ):
                print(f"[ERROR] Selected POS Opening Shift should be open.")
                frappe.throw(
                    _("Selected POS Opening Shift should be open."),
                    title=_("Invalid Opening Entry"),
                )
            self.update_payment_reconciliation()
        except Exception as e:
            print(f"[ERROR] Exception in validate: {e}")
            raise

    def update_payment_reconciliation(self):
        print(f"[INFO] update_payment_reconciliation called for POSClosingShift: {self.name if hasattr(self, 'name') else ''}")
        try:
            precision = (
                frappe.get_cached_value("System Settings", None, "currency_precision") or 3
            )
            for d in self.payment_reconciliation:
                d.difference = +flt(d.closing_amount, precision) - flt(
                    d.expected_amount, precision
                )
        except Exception as e:
            print(f"[ERROR] Exception in update_payment_reconciliation: {e}")
            raise

    def on_submit(self):
        print(f"[INFO] on_submit called for POSClosingShift: {self.name if hasattr(self, 'name') else ''}")
        try:
            opening_entry = frappe.get_doc("POS Opening Shift", self.pos_opening_shift)
            opening_entry.pos_closing_shift = self.name
            opening_entry.set_status()
            self.delete_draft_invoices()
            opening_entry.save()
        except Exception as e:
            print(f"[ERROR] Exception in on_submit: {e}")
            raise

    def delete_draft_invoices(self):
        print(f"[INFO] delete_draft_invoices called for POSClosingShift: {self.name if hasattr(self, 'name') else ''}")
        try:
            if frappe.get_value("POS Profile", self.pos_profile, "posa_allow_delete"):
                data = frappe.db.sql(
                    """
                    select
                        name
                    from
                        `tabSales Invoice`
                    where
                        docstatus = 0 and posa_is_printed = 0 and posa_pos_opening_shift = %s
                    """,
                    (self.pos_opening_shift),
                    as_dict=1,
                )

                for invoice in data:
                    print(f"[INFO] Deleting draft Sales Invoice: {invoice['name']}")
                    frappe.delete_doc("Sales Invoice", invoice.name, force=1)
        except Exception as e:
            print(f"[ERROR] Exception in delete_draft_invoices: {e}")
            raise

    @frappe.whitelist()
    def get_payment_reconciliation_details(self):
        print(f"[INFO] get_payment_reconciliation_details called for POSClosingShift: {self.name if hasattr(self, 'name') else ''}")
        try:
            currency = frappe.get_cached_value("Company", self.company, "default_currency")
            return frappe.render_template(
                "posawesome/posawesome/doctype/pos_closing_shift/closing_shift_details.html",
                {"data": self, "currency": currency},
            )
        except Exception as e:
            print(f"[ERROR] Exception in get_payment_reconciliation_details: {e}")
            raise


@frappe.whitelist()
def get_cashiers(doctype, txt, searchfield, start, page_len, filters):
    print(f"[INFO] get_cashiers called with doctype={doctype}, txt={txt}, filters={filters}")
    try:
        doctype = "User"
        conditions = []
        cashiers_list = frappe.get_all("POS Profile User", filters=filters, fields=["user as name"])
        fields = ["user"]

        return frappe.db.sql(
            """select {fields} from `tabPOS Profile User`
            where
                docstatus < 2
                and ({key} like %(txt)s)
                and parent = %(pos_profile)s
            order by
                (case when locate(%(_txt)s, user) > 0 then locate(%(_txt)s, user) else 99999 end),
                idx desc,
                user
            limit %(page_len)s offset %(start)s""".format(
                **{
                    "fields": ", ".join(fields),
                    "key": "user",
                    "fcond": "",
                    "mcond": "",
                }
            ),
            {"txt": "%%%s%%" % txt, "_txt": txt.replace("%", ""), "start": start, "page_len": page_len, "pos_profile": filters.get("parent")},
        )
    except Exception as e:
        print(f"[ERROR] Exception in get_cashiers: {e}")
        raise

@frappe.whitelist()
def get_pos_invoices(pos_opening_shift):
    print(f"[INFO] get_pos_invoices called with pos_opening_shift={pos_opening_shift}")
    try:
        submit_printed_invoices(pos_opening_shift)
        data = frappe.db.sql(
            """
        select
            name
        from
            `tabSales Invoice`
        where
            docstatus = 1 and posa_pos_opening_shift = %s
        """,
            (pos_opening_shift),
            as_dict=1,
        )

        data = [frappe.get_doc("Sales Invoice", d.name).as_dict() for d in data]

        return data
    except Exception as e:
        print(f"[ERROR] Exception in get_pos_invoices: {e}")
        raise

@frappe.whitelist()
def get_payments_entries(pos_opening_shift):
    print(f"[INFO] get_payments_entries called with pos_opening_shift={pos_opening_shift}")
    try:
        return frappe.get_all(
            "Payment Entry",
            filters={
                "docstatus": 1,
                "reference_no": pos_opening_shift,
                "payment_type": "Receive",
            },
            fields=[
                "name",
                "mode_of_payment",
                "paid_amount",
                "reference_no",
                "posting_date",
                "party",
            ],
        )
    except Exception as e:
        print(f"[ERROR] Exception in get_payments_entries: {e}")
        raise

@frappe.whitelist()
def make_closing_shift_from_opening(opening_shift):
    opening_shift = json.loads(opening_shift)
    submit_printed_invoices(opening_shift.get("name"))
    closing_shift = frappe.new_doc("POS Closing Shift")
    closing_shift.pos_opening_shift = opening_shift.get("name")
    closing_shift.period_start_date = opening_shift.get("period_start_date")
    closing_shift.period_end_date = frappe.utils.get_datetime()
    closing_shift.pos_profile = opening_shift.get("pos_profile")
    closing_shift.user = opening_shift.get("user")
    closing_shift.company = opening_shift.get("company")
    closing_shift.grand_total = 0
    closing_shift.net_total = 0
    closing_shift.total_quantity = 0

    invoices = get_pos_invoices(opening_shift.get("name"))

    pos_transactions = []
    taxes = []
    payments = []
    pos_payments_table = []
    for detail in opening_shift.get("balance_details"):
        payments.append(
            frappe._dict(
                {
                    "mode_of_payment": detail.get("mode_of_payment"),
                    "opening_amount": detail.get("amount") or 0,
                    "expected_amount": detail.get("amount") or 0,
                }
            )
        )

    for d in invoices:
        pos_transactions.append(
            frappe._dict(
                {
                    "sales_invoice": d.name,
                    "posting_date": d.posting_date,
                    "grand_total": d.grand_total,
                    "customer": d.customer,
                }
            )
        )
        closing_shift.grand_total += flt(d.grand_total)
        closing_shift.net_total += flt(d.net_total)
        closing_shift.total_quantity += flt(d.total_qty)

        for t in d.taxes:
            existing_tax = [
                tx
                for tx in taxes
                if tx.account_head == t.account_head and tx.rate == t.rate
            ]
            if existing_tax:
                existing_tax[0].amount += flt(t.tax_amount)
            else:
                taxes.append(
                    frappe._dict(
                        {
                            "account_head": t.account_head,
                            "rate": t.rate,
                            "amount": t.tax_amount,
                        }
                    )
                )

        for p in d.payments:
            existing_pay = [
                pay for pay in payments if pay.mode_of_payment == p.mode_of_payment
            ]
            if existing_pay:
                cash_mode_of_payment = frappe.get_value(
                    "POS Profile",
                    opening_shift.get("pos_profile"),
                    "posa_cash_mode_of_payment",
                )
                if not cash_mode_of_payment:
                    cash_mode_of_payment = "Cash"
                if existing_pay[0].mode_of_payment == cash_mode_of_payment:
                    amount = p.amount - d.change_amount
                else:
                    amount = p.amount
                existing_pay[0].expected_amount += flt(amount)
            else:
                payments.append(
                    frappe._dict(
                        {
                            "mode_of_payment": p.mode_of_payment,
                            "opening_amount": 0,
                            "expected_amount": p.amount,
                        }
                    )
                )

    pos_payments = get_payments_entries(opening_shift.get("name"))

    for py in pos_payments:
        pos_payments_table.append(
            frappe._dict(
                {
                    "payment_entry": py.name,
                    "mode_of_payment": py.mode_of_payment,
                    "paid_amount": py.paid_amount,
                    "posting_date": py.posting_date,
                    "customer": py.party,
                }
            )
        )
        existing_pay = [
            pay for pay in payments if pay.mode_of_payment == py.mode_of_payment
        ]
        if existing_pay:
            existing_pay[0].expected_amount += flt(py.paid_amount)
        else:
            payments.append(
                frappe._dict(
                    {
                        "mode_of_payment": py.mode_of_payment,
                        "opening_amount": 0,
                        "expected_amount": py.paid_amount,
                    }
                )
            )

    closing_shift.set("pos_transactions", pos_transactions)
    closing_shift.set("payment_reconciliation", payments)
    closing_shift.set("taxes", taxes)
    closing_shift.set("pos_payments", pos_payments_table)

    return closing_shift


@frappe.whitelist()
def submit_closing_shift(closing_shift):
    closing_shift = json.loads(closing_shift)
    closing_shift_doc = frappe.get_doc(closing_shift)
    closing_shift_doc.flags.ignore_permissions = True
    closing_shift_doc.save()
    closing_shift_doc.submit()
    return closing_shift_doc.name


def submit_printed_invoices(pos_opening_shift):
    invoices_list = frappe.get_all(
        "Sales Invoice",
        filters={
            "posa_pos_opening_shift": pos_opening_shift,
            "docstatus": 0,
            "posa_is_printed": 1,
        },
    )
    for invoice in invoices_list:
        invoice_doc = frappe.get_doc("Sales Invoice", invoice.name)
        invoice_doc.submit()
