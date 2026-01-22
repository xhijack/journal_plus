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
    cost_center(frm){
        if (!frm.doc.cost_center) return;
        (frm.doc.details || []).forEach(row => {
            if (!row.cost_center) {
                frappe.model.set_value(row.doctype, row.name, 'cost_center', frm.doc.cost_center);
            }
        });
    },
    project(frm){
        if (!frm.doc.project) return;
        (frm.doc.details || []).forEach(row => {
            if (!row.project) {
                frappe.model.set_value(row.doctype, row.name, 'project', frm.doc.project);
            }
        });
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
        frm.set_query("cost_center", 'details', () => {
			return {
				filters: [
                    ["Cost Center", "company", "=", frm.doc.company]
				]
			}
		});
        frm.set_query("project", 'details', () => {
			return {
				filters: [
                    ["Project", "company", "=", frm.doc.company]
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
    },
    details_add(frm, cdt, cdn){
        const row = locals[cdt][cdn];
        if (frm.doc.cost_center && !row.cost_center) {
            frappe.model.set_value(cdt, cdn, 'cost_center', frm.doc.cost_center);
        }
        if (frm.doc.project && !row.project) {
            frappe.model.set_value(cdt, cdn, 'project', frm.doc.project);
        }
    }
});
