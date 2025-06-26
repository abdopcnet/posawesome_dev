// Copyright (c) 2021, Youssef Restom and contributors
// For license information, please see license.txt

frappe.ui.form.on('POS Coupon', {
	setup: function (frm) {
		console.info('[INFO] setup called');
		frm.set_query("pos_offer", function () {
			return {
				filters: {
					"company": frm.doc.company,
					"coupon_based": 1,
					"disable": 0,
				}
			};
		});
	},
	coupon_name: function (frm) {
		console.info('[INFO] coupon_name changed');
		if (frm.doc.__islocal === 1) {
			frm.trigger("make_coupon_code");
		}
	},
	coupon_type: function (frm) {
		console.info('[INFO] coupon_type changed');
		if (frm.doc.__islocal === 1) {
			frm.trigger("make_coupon_code");
		}
	},
	make_coupon_code: function (frm) {
		console.info('[INFO] make_coupon_code called');
		try {
			var coupon_name = frm.doc.coupon_name;
			var coupon_code;
			if (frm.doc.coupon_type == 'Gift Card') {
				coupon_code = Math.random().toString(12).substring(2, 12).toUpperCase();
			}
			else if (frm.doc.coupon_type == 'Promotional') {
				coupon_name = coupon_name.replace(/\s/g, '');
				coupon_code = coupon_name.toUpperCase().slice(0, 8);
			}
			frm.doc.coupon_code = coupon_code;
			frm.refresh_field('coupon_code');
			console.info('[INFO] coupon_code generated:', coupon_code);
		} catch (e) {
			console.error('[ERROR] Exception in make_coupon_code:', e);
		}
	},
	refresh: function (frm) {
		console.info('[INFO] refresh called');
		if (frm.doc.pricing_rule) {
			frm.add_custom_button(__("Add/Edit Coupon Conditions"), function () {
				console.info('[INFO] Add/Edit Coupon Conditions button clicked');
				frappe.set_route("Form", "POS Offer", frm.doc.pos_offer);
			});
		}
	}
});