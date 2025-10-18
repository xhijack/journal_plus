# journal_plus/journal_plus/doctype/expense_entry/expense_entry.py

import frappe
from frappe.model.document import Document
from decimal import Decimal, ROUND_HALF_UP
from frappe import _
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.accounts_controller import AccountsController

def _to_decimal(val):
    try:
        return Decimal(str(val or 0))
    except Exception:
        return Decimal("0.0")

def _float_safe(d: Decimal) -> float:
    return float(d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


class ExpenseEntry(AccountsController):
    """Expense Entry inheriting AccountsController so it gets standard accounting behavior
       (cancel, trash/delete GL, linked doc checks) + our custom logic."""

    def validate(self):
        total = Decimal("0.0")
        qty = 0
        for idx, row in enumerate(getattr(self, "details", []) or [], start=1):
            amt = _to_decimal(getattr(row, "amount", 0))
            if amt < 0:
                frappe.throw(_("Amount must be non-negative for row {0} (account: {1})").format(idx, getattr(row, "expense_account", "")))
            total += amt
            qty += 1
        try:
            self.total = float(total)
        except Exception:
            self.total = total
        self.qty = qty

        # Optionally call parent validate for AccountingController logic
        try:
            super(ExpenseEntry, self).validate()
        except AttributeError:
            pass

    def before_cancel(self):
        # Set ignore linked doctypes so GL Entry doesn't stop cancel
        self.ignore_linked_doctypes = ("GL Entry", "Stock Ledger Entry")

        # Call parent behavior
        try:
            super(ExpenseEntry, self).before_cancel()
        except AttributeError:
            pass

    def on_submit(self):
        if not frappe.has_permission(self.doctype, ptype="write", doc=self):
            frappe.throw(_("You don’t have permission to post this document"))

        gl_map = self._build_gl_map_for_expense()
        gl_map_dicts = [frappe._dict(e) for e in gl_map]
        make_gl_entries(gl_map_dicts, cancel=False, adv_adj=False, merge_entries=False)

        if hasattr(self, "db_set"):
            try:
                self.db_set("posted_to_gl", 1)
            except:
                pass

        # call parent on_submit if needed
        try:
            super(ExpenseEntry, self).on_submit()
        except AttributeError:
            pass

    def on_cancel(self):
        # Reverse GL entries
        gl_map = self._build_gl_map_for_expense()
        gl_map_dicts = [frappe._dict(e) for e in gl_map]
        make_gl_entries(gl_map_dicts, cancel=True, adv_adj=False, merge_entries=False)

        # Set document status (only if field exists)
        if self.meta.has_field("status"):
            self.db_set("status", "Cancelled")

        # Call parent on_cancel if exists
        try:
            super(ExpenseEntry, self).on_cancel()
        except AttributeError:
            pass

    def _build_gl_map_for_expense(self):
        if not getattr(self, "details", None):
            frappe.throw(_("No detail lines found"))

        credit_account = getattr(self, "account_paid_from", None)
        if not credit_account:
            frappe.throw(_("Account Paid From is required"))

        company = getattr(self, "company", None) or frappe.get_cached_value("Global Defaults", None, "default_company")
        if not company:
            frappe.throw(_("Company is required"))

        currency = getattr(self, "currency", None) or frappe.get_cached_value("Company", company, "default_currency") or getattr(self, "company_currency", None) or "IDR"
        exchange_rate = getattr(self, "exchange_rate", None) or 1.0
        posting_date = getattr(self, "posting_date", None) or getattr(self, "required_date", None) or frappe.utils.nowdate()

        gl_entries = []
        total_debit = Decimal("0.0")

        for idx, row in enumerate(getattr(self, "details", []) or [], start=1):
            acct = getattr(row, "expense_account", None)
            if not acct:
                frappe.throw(_("Expense Account is required for row {0}").format(idx))

            amt_dec = _to_decimal(getattr(row, "amount", 0))
            if amt_dec <= 0:
                frappe.throw(_("Amount must be positive for row {0}").format(idx))

            total_debit += amt_dec
            amt = _float_safe(amt_dec)

            gl_entries.append({
                "posting_date": posting_date,
                "account": acct,
                "party_type": getattr(row, "party_type", None),
                "party": getattr(row, "party", None),
                "against": credit_account,
                "debit": amt,
                "credit": 0.0,
                "debit_in_account_currency": amt,
                "credit_in_account_currency": 0.0,
                "account_currency": currency,
                "exchange_rate": exchange_rate,
                "company": company,
                "voucher_type": self.doctype,
                "voucher_no": self.name,
                "remarks": getattr(row, "remarks", None) or getattr(self, "remarks", None) or _("Expense"),
                "cost_center": getattr(row, "cost_center", None) or getattr(self, "cost_center", None),
                "project": getattr(row, "project", None) or getattr(self, "project", None),
                "is_opening": getattr(self, "is_opening", 0)
            })

        gl_entries.append({
            "posting_date": posting_date,
            "account": credit_account,
            "party_type": None,
            "party": None,
            "against": ", ".join([ getattr(r, "expense_account", "") for r in (getattr(self, "details", []) or []) ]),
            "debit": 0.0,
            "credit": _float_safe(total_debit),
            "debit_in_account_currency": 0.0,
            "credit_in_account_currency": _float_safe(total_debit),
            "account_currency": currency,
            "exchange_rate": exchange_rate,
            "company": company,
            "voucher_type": self.doctype,
            "voucher_no": self.name,
            "remarks": getattr(self, "remarks", None) or _("Payment/Clearing"),
            "cost_center": getattr(self, "cost_center", None),
            "project": getattr(self, "project", None),
            "is_opening": getattr(self, "is_opening", 0)
        })

        total_debit_dec = sum([_to_decimal(e.get("debit") or 0) for e in gl_entries])
        total_credit_dec = sum([_to_decimal(e.get("credit") or 0) for e in gl_entries])
        if total_debit_dec != total_credit_dec:
            diff = (total_debit_dec - total_credit_dec).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            rounding_account = getattr(self, "rounding_account", None) or frappe.get_cached_value("Company", company, "rounding_account")
            if rounding_account:
                if diff > 0:
                    gl_entries.append({
                        "posting_date": posting_date,
                        "account": rounding_account,
                        "debit": 0.0,
                        "credit": _float_safe(diff),
                        "debit_in_account_currency": 0.0,
                        "credit_in_account_currency": _float_safe(diff),
                        "account_currency": currency,
                        "exchange_rate": exchange_rate,
                        "company": company,
                        "voucher_type": self.doctype,
                        "voucher_no": self.name,
                        "remarks": _("Rounding adjustment"),
                    })
                else:
                    gl_entries.append({
                        "posting_date": posting_date,
                        "account": rounding_account,
                        "debit": _float_safe(-diff),
                        "credit": 0.0,
                        "debit_in_account_currency": _float_safe(-diff),
                        "credit_in_account_currency": 0.0,
                        "account_currency": currency,
                        "exchange_rate": exchange_rate,
                        "company": company,
                        "voucher_type": self.doctype,
                        "voucher_no": self.name,
                        "remarks": _("Rounding adjustment"),
                    })
                total_debit_dec = sum([_to_decimal(e.get("debit") or 0) for e in gl_entries])
                total_credit_dec = sum([_to_decimal(e.get("credit") or 0) for e in gl_entries])

        if total_debit_dec != total_credit_dec:
            frappe.throw(_("GL entries are not balanced: debit {0} != credit {1}").format(total_debit_dec, total_credit_dec))

        return gl_entries
