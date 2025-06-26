# -*- coding: utf-8 -*-
# Copyright (c) 2020, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint
from frappe.model.document import Document
from posawesome.posawesome.api.status_updater import StatusUpdater
import sys


class POSOpeningShift(StatusUpdater):
	def validate(self):
		print(f"[INFO] validate called for POSOpeningShift: {self.name if hasattr(self, 'name') else ''}", file=sys.stdout)
		try:
			self.validate_pos_profile_and_cashier()
			self.set_status()
		except Exception as e:
			print(f"[ERROR] Exception in validate: {e}", file=sys.stderr)
			raise

	def validate_pos_profile_and_cashier(self):
		print(f"[INFO] validate_pos_profile_and_cashier called for POSOpeningShift: {self.name if hasattr(self, 'name') else ''}", file=sys.stdout)
		try:
			if self.company != frappe.db.get_value("POS Profile", self.pos_profile, "company"):
				print(f"[ERROR] POS Profile {self.pos_profile} does not belong to company {self.company}", file=sys.stderr)
				frappe.throw(_("POS Profile {} does not belongs to company {}".format(self.pos_profile, self.company)))

			if not cint(frappe.db.get_value("User", self.user, "enabled")):
				print(f"[ERROR] User {self.user} has been disabled.", file=sys.stderr)
				frappe.throw(_("User {} has been disabled. Please select valid user/cashier".format(self.user)))
		except Exception as e:
			print(f"[ERROR] Exception in validate_pos_profile_and_cashier: {e}", file=sys.stderr)
			raise

	def on_submit(self):
		print(f"[INFO] on_submit called for POSOpeningShift: {self.name if hasattr(self, 'name') else ''}", file=sys.stdout)
		try:
			self.set_status(update=True)
		except Exception as e:
			print(f"[ERROR] Exception in on_submit: {e}", file=sys.stderr)
			raise
