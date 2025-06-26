## -*- coding: utf-8 -*-
# Copyright (c) 2020, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import comma_or, nowdate, getdate
from frappe import _
from frappe.model.document import Document

class OverAllowanceError(frappe.ValidationError): pass


def validate_status(status, options):
    try:
        print(f"[INFO] Validating status: {status} against options: {options}")
        if status not in options:
            print(f"[ERROR] Status '{status}' is not in options: {options}")
            frappe.throw(_("Status must be one of {0}").format(comma_or(options)))
    except Exception as e:
        print(f"[ERROR] Exception in validate_status: {e}")
        raise

status_map = {
	"POS Opening Shift": [
		["Draft", None],
		["Open", "eval:self.docstatus == 1 and not self.pos_closing_shift"],
		["Closed", "eval:self.docstatus == 1 and self.pos_closing_shift"],
		["Cancelled", "eval:self.docstatus == 2"],
	]
}

class StatusUpdater(Document):

    def set_status(self, update=False, status=None, update_modified=True):
        print(f"[INFO] set_status called with update={update}, status={status}, update_modified={update_modified}")
        try:
            if self.is_new():
                print(f"[INFO] Document is new. Checking for amended_from.")
                if self.get('amended_from'):
                    self.status = 'Draft'
                    print(f"[INFO] Status set to Draft due to amended_from.")
                return

            if self.doctype in status_map:
                _status = self.status
                if status and update:
                    print(f"[INFO] Updating status in DB to: {status}")
                    self.db_set("status", status)

                sl = status_map[self.doctype][:]
                sl.reverse()
                for s in sl:
                    if not s[1]:
                        self.status = s[0]
                        print(f"[INFO] Status set to: {s[0]}")
                        break
                    elif s[1].startswith("eval:"):
                        try:
                            result = frappe.safe_eval(s[1][5:], None, { "self": self.as_dict(), "getdate": getdate,
                                    "nowdate": nowdate, "get_value": frappe.db.get_value })
                            print(f"[INFO] Evaluated {s[1]} to {result}")
                            if result:
                                self.status = s[0]
                                print(f"[INFO] Status set to: {s[0]}")
                                break
                        except Exception as e:
                            print(f"[ERROR] Exception in safe_eval: {e}")
                            raise
                    elif getattr(self, s[1])():
                        self.status = s[0]
                        print(f"[INFO] Status set to: {s[0]}")
                        break

                if self.status != _status and self.status not in ("Cancelled", "Partially Ordered",
                                                                    "Ordered", "Issued", "Transferred"):
                    print(f"[INFO] Adding comment for status: {self.status}")
                    self.add_comment("Label", _(self.status))

                if update:
                    print(f"[INFO] Updating status in DB to: {self.status}")
                    self.db_set('status', self.status, update_modified = update_modified)
        except Exception as e:
            print(f"[ERROR] Exception in set_status: {e}")
            raise
