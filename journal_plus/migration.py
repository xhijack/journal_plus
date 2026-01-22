import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe import _


def create_accounting_dimensions(doc, method):
    """
        Create accounting Dimension fields in Expense Entry and Expense Entry Detail
    """

    if doc.disabled:
        return

    dimension_fieldname = frappe.scrub(doc.name)
    dimension_doctype = doc.document_type

    if not dimension_doctype:
        return

    is_required = frappe.db.exists(
        "Accounting Dimension Default",
        {
            "parent": doc.name,
            "mandatory_for_pl": 1,
        }
    )

    custom_fields = {}

    if not frappe.db.exists(
        "Custom Field",
        {"dt": "Expense Entry", "fieldname": dimension_fieldname},
    ):
        custom_fields.setdefault("Expense Entry", []).append(
            {
                "fieldname": dimension_fieldname,
                "label": doc.label,
                "fieldtype": "Link",
                "options": dimension_doctype,
                "insert_after": "project",
                "reqd": 1 if is_required else 0,
                "ignore_user_permissions": 1,
            }
        )
    if not frappe.db.exists(
        "Custom Field",
        {"dt": "Expense Entry Detail", "fieldname": dimension_fieldname},
    ):
        custom_fields.setdefault("Expense Entry Detail", []).append(
            {
                "fieldname": dimension_fieldname,
                "label": dimension_fieldname,
                "fieldtype": "Link",
                "options": dimension_doctype,
                "insert_after": "cost_center",
                "reqd": 1 if is_required else 0,
                "ignore_user_permissions": 1,
            }
        )

    if custom_fields:
        create_custom_fields(custom_fields, update=True)
        frappe.clear_cache()

        frappe.msgprint(
            _("Accounting Dimension <b>{0}</b> synced to Expense Entry").format(
                doc.label
            )
        )