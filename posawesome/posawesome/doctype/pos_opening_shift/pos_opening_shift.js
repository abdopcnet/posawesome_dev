// Copyright (c) 2020, Youssef Restom and contributors
// For license information, please see license.txt

frappe.ui.form.on('POS Opening Shift', {
	setup(frm) {
		try {
			console.info('[INFO] Running setup for POS Opening Shift');
			if (frm.doc.docstatus == 0) {
				frm.trigger('set_posting_date_read_only');
				frm.set_value('period_start_date', frappe.datetime.now_datetime());
				frm.set_value('user', frappe.session.user);
			}
			frm.set_query("user", function(doc) {
				return {
					query: "posawesome.posawesome.doctype.pos_closing_shift.pos_closing_shift.get_cashiers",
					filters: { 'parent': doc.pos_profile }
				};
			});
			frm.set_query("pos_profile", function(doc) {
				return {
					filters: { 'company': doc.company}
				};
			});
		} catch (error) {
			console.error('[ERROR] setup error:', error);
		}
	},

	refresh(frm) {
		try {
			console.info('[INFO] Refreshing POS Opening Shift');
			// set default posting date / time
			if(frm.doc.docstatus == 0) {
				if(!frm.doc.posting_date) {
					frm.set_value('posting_date', frappe.datetime.nowdate());
				}
				frm.trigger('set_posting_date_read_only');
			}
		} catch (error) {
			console.error('[ERROR] refresh error:', error);
		}
	},

	set_posting_date_read_only(frm) {
		try {
			console.info('[INFO] Setting posting date read only');
			if(frm.doc.docstatus == 0 && frm.doc.set_posting_date) {
				frm.set_df_property('posting_date', 'read_only', 0);
			} else {
				frm.set_df_property('posting_date', 'read_only', 1);
			}
		} catch (error) {
			console.error('[ERROR] set_posting_date_read_only error:', error);
		}
	},

	set_posting_date(frm) {
		try {
			console.info('[INFO] Triggering set_posting_date_read_only');
			frm.trigger('set_posting_date_read_only');
		} catch (error) {
			console.error('[ERROR] set_posting_date error:', error);
		}
	},

	pos_profile: (frm) => {
		try {
			console.info('[INFO] pos_profile triggered');
			if (frm.doc.pos_profile) {
				frappe.db.get_doc("POS Profile", frm.doc.pos_profile)
					.then(({ payments }) => {
						if (payments.length) {
							frm.doc.balance_details = [];
							payments.forEach(({ mode_of_payment }) => {
								frm.add_child("balance_details", { mode_of_payment });
							})
							frm.refresh_field("balance_details");
						}
					})
					.catch(error => {
						console.error('[ERROR] pos_profile get_doc error:', error);
					});
			}
		} catch (error) {
			console.error('[ERROR] pos_profile error:', error);
		}
	}
});