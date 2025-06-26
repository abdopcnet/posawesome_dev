// Copyright (c) 2020, Youssef Restom and contributors
// For license information, please see license.txt

frappe.ui.form.on('POS Closing Shift', {
	onload: function (frm) {
		console.info('[INFO] onload called');
		frm.set_query("pos_profile", function (doc) {
			return {
				filters: { 'user': doc.user }
			};
		});

		frm.set_query("user", function (doc) {
			return {
				query: "posawesome.posawesome.doctype.pos_closing_shift.pos_closing_shift.get_cashiers",
				filters: { 'parent': doc.pos_profile }
			};
		});

		frm.set_query("pos_opening_shift", function (doc) {
			return { filters: { 'status': 'Open', 'docstatus': 1 } };
		});

		if (frm.doc.docstatus === 0) frm.set_value("period_end_date", frappe.datetime.now_datetime());
		if (frm.doc.docstatus === 1) set_html_data(frm);
	},

	pos_opening_shift (frm) {
		console.info('[INFO] pos_opening_shift triggered');
		if (frm.doc.pos_opening_shift && frm.doc.user) {
			reset_values(frm);
			frappe.run_serially([
				() => frm.trigger("set_opening_amounts"),
				() => frm.trigger("get_pos_invoices"),
				() => frm.trigger("get_pos_payments")
			]);
		}
	},

	set_opening_amounts (frm) {
		console.info('[INFO] set_opening_amounts called');
		frappe.db.get_doc("POS Opening Shift", frm.doc.pos_opening_shift)
			.then(({ balance_details }) => {
				balance_details.forEach(detail => {
					frm.add_child("payment_reconciliation", {
						mode_of_payment: detail.mode_of_payment,
						opening_amount: detail.amount || 0,
						expected_amount: detail.amount || 0
					});
				});
			})
			.catch(e => {
				console.error('[ERROR] Exception in set_opening_amounts:', e);
			});
	},

	get_pos_invoices (frm) {
		console.info('[INFO] get_pos_invoices called');
		frappe.call({
			method: 'posawesome.posawesome.doctype.pos_closing_shift.pos_closing_shift.get_pos_invoices',
			args: {
				pos_opening_shift: frm.doc.pos_opening_shift,
			},
			callback: (r) => {
				let pos_docs = r.message;
				set_form_data(pos_docs, frm);
				refresh_fields(frm);
				set_html_data(frm);
			},
			error: function(err) {
				console.error('[ERROR] Exception in get_pos_invoices:', err);
			}
		});
	},

	get_pos_payments (frm) {
		console.info('[INFO] get_pos_payments called');
		frappe.call({
			method: 'posawesome.posawesome.doctype.pos_closing_shift.pos_closing_shift.get_payments_entries',
			args: {
				pos_opening_shift: frm.doc.pos_opening_shift,
			},
			callback: (r) => {
				let pos_payments = r.message;
				set_form_payments_data(pos_payments, frm);
				refresh_fields(frm);
				set_html_data(frm);
			},
			error: function(err) {
				console.error('[ERROR] Exception in get_pos_payments:', err);
			}
		});
	}
});

frappe.ui.form.on('POS Closing Shift Detail', {
	closing_amount: (frm, cdt, cdn) => {
		console.info('[INFO] closing_amount changed');
		const row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "difference", flt(row.expected_amount - row.closing_amount));
	}
});

function set_form_data (data, frm) {
	console.info('[INFO] set_form_data called');
	try {
		data.forEach(d => {
			add_to_pos_transaction(d, frm);
			frm.doc.grand_total += flt(d.grand_total);
			frm.doc.net_total += flt(d.net_total);
			frm.doc.total_quantity += flt(d.total_qty);
			add_to_payments(d, frm);
			add_to_taxes(d, frm);
		});
	} catch (e) {
		console.error('[ERROR] Exception in set_form_data:', e);
	}
}

function set_form_payments_data (data, frm) {
	console.info('[INFO] set_form_payments_data called');
	try {
		data.forEach(d => {
			add_to_pos_payments(d, frm);
			add_pos_payment_to_payments(d, frm);
		});
	} catch (e) {
		console.error('[ERROR] Exception in set_form_payments_data:', e);
	}
}

function add_to_pos_transaction (d, frm) {
	console.info('[INFO] add_to_pos_transaction called');
	frm.add_child("pos_transactions", {
		sales_invoice: d.name,
		posting_date: d.posting_date,
		grand_total: d.grand_total,
		customer: d.customer
	});
}

function add_to_pos_payments (d, frm) {
	console.info('[INFO] add_to_pos_payments called');
	frm.add_child("pos_payments", {
		payment_entry: d.name,
		posting_date: d.posting_date,
		paid_amount: d.paid_amount,
		customer: d.party,
		mode_of_payment: d.mode_of_payment
	});
}

function add_to_payments (d, frm) {
	console.info('[INFO] add_to_payments called');
	try {
		d.payments.forEach(p => {
			const payment = frm.doc.payment_reconciliation.find(pay => pay.mode_of_payment === p.mode_of_payment);
			if (payment) {
				let amount = p.amount;
				let cash_mode_of_payment = get_value("POS Profile", frm.doc.pos_profile, 'posa_cash_mode_of_payment');
				if (!cash_mode_of_payment) {
					cash_mode_of_payment = 'Cash';
				}
				if (payment.mode_of_payment == cash_mode_of_payment) {
					amount = p.amount - d.change_amount;
				}
				payment.expected_amount += flt(amount);
			} else {
				frm.add_child("payment_reconciliation", {
					mode_of_payment: p.mode_of_payment,
					opening_amount: 0,
					expected_amount: p.amount || 0
				});
			}
		});
	} catch (e) {
		console.error('[ERROR] Exception in add_to_payments:', e);
	}
}

function add_pos_payment_to_payments (p, frm) {
	console.info('[INFO] add_pos_payment_to_payments called');
	try {
		const payment = frm.doc.payment_reconciliation.find(pay => pay.mode_of_payment === p.mode_of_payment);
		if (payment) {
			let amount = p.paid_amount;
			payment.expected_amount += flt(amount);
		} else {
			frm.add_child("payment_reconciliation", {
				mode_of_payment: p.mode_of_payment,
				opening_amount: 0,
				expected_amount: p.amount || 0
			});
		}
	} catch (e) {
		console.error('[ERROR] Exception in add_pos_payment_to_payments:', e);
	}
};


function add_to_taxes (d, frm) {
	console.info('[INFO] add_to_taxes called');
	try {
		d.taxes.forEach(t => {
			const tax = frm.doc.taxes.find(tx => tx.account_head === t.account_head && tx.rate === t.rate);
			if (tax) {
				tax.amount += flt(t.tax_amount);
			} else {
				frm.add_child("taxes", {
					account_head: t.account_head,
					rate: t.rate,
					amount: t.tax_amount
				});
			}
		});
	} catch (e) {
		console.error('[ERROR] Exception in add_to_taxes:', e);
	}
}

function reset_values (frm) {
	console.info('[INFO] reset_values called');
	frm.set_value("pos_transactions", []);
	frm.set_value("payment_reconciliation", []);
	frm.set_value("pos_payments", []);
	frm.set_value("taxes", []);
	frm.set_value("grand_total", 0);
	frm.set_value("net_total", 0);
	frm.set_value("total_quantity", 0);
}

function refresh_fields (frm) {
	console.info('[INFO] refresh_fields called');
	frm.refresh_field("pos_transactions");
	frm.refresh_field("payment_reconciliation");
	frm.refresh_field("pos_payments");
	frm.refresh_field("taxes");
	frm.refresh_field("grand_total");
	frm.refresh_field("net_total");
	frm.refresh_field("total_quantity");
}

function set_html_data (frm) {
	console.info('[INFO] set_html_data called');
	frappe.call({
		method: "get_payment_reconciliation_details",
		doc: frm.doc,
		callback: (r) => {
			frm.get_field("payment_reconciliation_details").$wrapper.html(r.message);
		},
		error: function(err) {
			console.error('[ERROR] Exception in set_html_data:', err);
		}
	});
}

const get_value = (doctype, name, field) => {
	console.info(`[INFO] get_value called for doctype: ${doctype}, name: ${name}, field: ${field}`);
	let value;
	frappe.call({
		method: 'frappe.client.get_value',
		args: {
			'doctype': doctype,
			'filters': { 'name': name },
			'fieldname': field
		},
		async: false,
		callback: function (r) {
			if (!r.exc) {
				value = r.message[field];
			}
		},
		error: function(err) {
			console.error('[ERROR] Exception in get_value:', err);
		}
	});
	return value;
};