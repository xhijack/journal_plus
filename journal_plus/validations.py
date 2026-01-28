from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
    get_accounting_dimensions,
)

import frappe

def validate_mandatory_dimensions():
    dimensions = get_accounting_dimensions()
    for dim in dimensions:
        mandatory = frappe.db.get_value(
            "Accounting Dimension Default",
            {"parent": dim, "mandatory_for_pl": 1},
            "name",
        )
        if mandatory and not getattr(dim, None):
            frappe.throw(_("{0} is mandatory for Profit and Loss").format(frappe.bold(dim)))