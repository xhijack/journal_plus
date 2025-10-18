// Copyright (c) 2025, PT Sopwer Teknologi Indonesia and contributors
// For license information, please see license.txt

frappe.ui.form.on("Expense Entry", {
	refresh(frm) {
        if (frm.doc.docstatus === 1) {
                    frm.add_custom_button("View Ledger", function() {
                        // buka report General Ledger dengan filter voucher_no & voucher_type
                        frappe.set_route("query-report", "General Ledger", {
                            "voucher_no": frm.doc.name,
                            "voucher_type": frm.doc.doctype,
                            "company": frm.doc.company
                        });
                    }, "View");
                }
	},
    setup(frm) {
        frm.set_query("expense_account", 'details', () => {
			return {
				filters: [
					["Account", "root_type", "=", "Expense"],
                    ["Account", "is_group", "=", "0"],
                    ["Account", "company", "=", frm.doc.company]
				]
			}
		});
    },
    mode_of_payment(frm){
        erpnext.accounts.pos.get_payment_mode_account(frm, frm.doc.mode_of_payment, function(account){
			// let payment_account_field = frm.doc.payment_type == "Receive" ? "paid_to" : "paid_from";
			frm.set_value('account_paid_from', account);
		})
    },
});

frappe.ui.form.on("Expense Entry Detail", {
    expense_label(frm, cdt, cdn){
        const row = locals[cdt][cdn];
        // console.log(row);
        const company = frm.doc.company;
        frappe.db.get_doc('Expense Label', row.expense_label).then(doc => {
            const accountRow = doc.accounts.find(a => a.company === company);
            console.log(accountRow);
            if (accountRow && accountRow.account) {
                frappe.model.set_value(cdt, cdn, 'expense_account', accountRow.account);
            } else {
                alert('No expense account found for this company in the selected Expense Label.');
            }
        }).catch(() => {
            frappe.model.set_value(cdt, cdn, 'expense_account', '');
        });
    }
});
