# journal_plus/journal_plus/doctype/expense_entry/expense_entry.py

import frappe
from frappe.model.document import Document
from decimal import Decimal, ROUND_HALF_UP
from frappe import _

from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.accounts_controller import AccountsController  # path sesuai versi kamu

def _to_decimal(val):
    """
    Convert a value to Decimal safely.
    """
    try:
        return Decimal(str(val or 0))
    except Exception:
        return Decimal("0.0")

def _float_safe(d: Decimal) -> float:
    """
    Quantize decimal to 2 places (for currency) and return float.
    """
    return float(d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


class ExpenseEntry(AccountsController):
    """
    Custom Expense Entry inheriting AccountsController to reuse core accounting logic
    (cancel, trash deletions, link checks) + our custom GL posting logic.
    """

    def validate(self):
        """
        Validate custom fields: compute total and qty from details.
        Then call parent validate (if exists) for further checks.
        """
        total = Decimal("0.0")
        qty = 0

        for idx, row in enumerate(getattr(self, "details", []) or [], start=1):
            amt_dec = _to_decimal(row.get("amount"))
            if amt_dec < 0:
                frappe.throw(_(
                    "Amount must be non-negative for row {0} (account: {1})"
                ).format(idx, row.get("expense_account", "")))
            total += amt_dec
            qty += 1

        # Set fields
        try:
            self.total = float(total)
        except Exception:
            self.total = total
        self.qty = qty

        # Call parent validate if available
        try:
            super(ExpenseEntry, self).validate()
        except AttributeError:
            pass

    def before_cancel(self):
        """
        Prepare for cancellation: define ignore linked doctypes so GL entries
        do not block cancel. Then call parent logic if any.
        """
        self.ignore_linked_doctypes = ("GL Entry", "Stock Ledger Entry")

        try:
            super(ExpenseEntry, self).before_cancel()
        except AttributeError:
            pass

    def on_submit(self):
        """
        When submitted: post GL entries (custom logic) and mark posted_to_gl.
        Then call parent on_submit if exists.
        """
        if not frappe.has_permission(self.doctype, ptype="write", doc=self):
            frappe.throw(_("You don’t have permission to post this document"))

        gl_map = self._build_gl_map_for_expense()
        gl_map_dicts = [frappe._dict(e) for e in gl_map]

        # Post GL entries. Use merge_entries=False to prevent internal aggregation.
        make_gl_entries(gl_map_dicts, cancel=False, adv_adj=False, merge_entries=False)

        # Mark as posted
        if self.meta.has_field("posted_to_gl"):
            self.db_set("posted_to_gl", 1)

        try:
            super(ExpenseEntry, self).on_submit()
        except AttributeError:
            pass

    def on_cancel(self):
        """
        When cancelled: reverse GL entries (post reversal), optionally set status,
        then call parent on_cancel logic.
        """
        gl_map = self._build_gl_map_for_expense()
        gl_map_dicts = [frappe._dict(e) for e in gl_map]

        make_gl_entries(gl_map_dicts, cancel=True, adv_adj=False, merge_entries=False)

        # Optionally update status field if available
        if self.meta.has_field("status"):
            self.db_set("status", "Cancelled")

        try:
            super(ExpenseEntry, self).on_cancel()
        except AttributeError:
            pass

    def _build_gl_map_for_expense(self):
        """
        Build the list of dict maps for GL posting based on detail lines.
        Debit per detail, one credit combining total.
        """
        details = getattr(self, "details", []) or []
        if not details:
            frappe.throw(_("No detail lines found"))

        credit_account = self.account_paid_from
        if not credit_account:
            frappe.throw(_("Account Paid From is required"))

        # Company fallback logic
        company = self.company or frappe.get_cached_value(
            "Global Defaults", None, "default_company"
        )
        if not company:
            frappe.throw(_("Company is required"))

        # Currency and exchange rate
        currency = (
            self.currency
            or frappe.get_cached_value("Company", company, "default_currency")
            or getattr(self, "company_currency", None)
            or "IDR"
        )
        exchange_rate = getattr(self, "exchange_rate", 1.0)

        posting_date = (
            getattr(self, "posting_date", None)
            or getattr(self, "required_date", None)
            or frappe.utils.nowdate()
        )

        gl_entries = []
        total_debit = Decimal("0.0")

        for idx, row in enumerate(details, start=1):
            acct = row.get("expense_account")
            if not acct:
                frappe.throw(_("Expense Account is required for row {0}").format(idx))

            amt_dec = _to_decimal(row.get("amount"))
            if amt_dec <= 0:
                frappe.throw(_("Amount must be positive for row {0}").format(idx))

            total_debit += amt_dec
            amt = _float_safe(amt_dec)

            # Use unique marker in 'against' or 'remarks' to avoid merging
            marker = row.get("name") or str(idx)
            remarks = row.get("remarks") or self.remarks or _("Expense")
            remarks_with_marker = f"{remarks} [{marker}]"

            gl_entries.append({
                "posting_date": posting_date,
                "account": acct,
                "party_type": row.get("party_type"),
                "party": row.get("party"),
                "against": f"{credit_account}|{marker}",
                "debit": amt,
                "credit": 0.0,
                "debit_in_account_currency": amt,
                "credit_in_account_currency": 0.0,
                "account_currency": currency,
                "exchange_rate": exchange_rate,
                "company": company,
                "voucher_type": self.doctype,
                "voucher_no": self.name,
                "remarks": remarks_with_marker,
                "cost_center": row.get("cost_center") or self.cost_center,
                "project": row.get("project") or self.project,
                "is_opening": getattr(self, "is_opening", 0)
            })

        # Single credit entry
        total_credit_amt = _float_safe(total_debit)
        # Combine detail expense accounts for the 'against' field
        against_list = ", ".join([row.get("expense_account", "") for row in details])

        gl_entries.append({
            "posting_date": posting_date,
            "account": credit_account,
            "party_type": None,
            "party": None,
            "against": against_list,
            "debit": 0.0,
            "credit": total_credit_amt,
            "debit_in_account_currency": 0.0,
            "credit_in_account_currency": total_credit_amt,
            "account_currency": currency,
            "exchange_rate": exchange_rate,
            "company": company,
            "voucher_type": self.doctype,
            "voucher_no": self.name,
            "remarks": self.remarks or _("Payment/Clearing"),
            "cost_center": self.cost_center,
            "project": self.project,
            "is_opening": getattr(self, "is_opening", 0)
        })

        # Validate balance
        total_debit_dec = sum(_to_decimal(e.get("debit", 0)) for e in gl_entries)
        total_credit_dec = sum(_to_decimal(e.get("credit", 0)) for e in gl_entries)

        if total_debit_dec != total_credit_dec:
            diff = (total_debit_dec - total_credit_dec).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            rounding_account = (
                getattr(self, "rounding_account", None)
                or frappe.get_cached_value("Company", company, "rounding_account")
            )
            if rounding_account:
                # Create adjustment entry
                if diff > 0:
                    adj = {
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
                    }
                else:
                    adj = {
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
                    }
                gl_entries.append(adj)

                # recalc
                total_debit_dec = sum(_to_decimal(e.get("debit", 0)) for e in gl_entries)
                total_credit_dec = sum(_to_decimal(e.get("credit", 0)) for e in gl_entries)

        if total_debit_dec != total_credit_dec:
            frappe.throw(_(
                "GL entries are not balanced: debit {0} != credit {1}"
            ).format(total_debit_dec, total_credit_dec))

        return gl_entries
