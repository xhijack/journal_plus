# Copyright (c) 2025, PT Sopwer Teknologi Indonesia
# See license.txt

import frappe
import unittest
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate
from decimal import Decimal


class TestExpenseEntry(FrappeTestCase):
	"""
	Unit test untuk Expense Entry:
	- submit -> GL entries dibuat dan seimbang
	- cancel -> reversal entries dibuat (ada entri is_cancelled)
	- delete -> jika setting aktif, GL entries dihapus
	"""

	def setUp(self):
		# Use existing default company
		self.company = frappe.defaults.get_user_default("Company") or frappe.get_default("company")
		if not self.company:
			# nothing to test against — skip
			self.skipTest("No default company configured on this site. Skipping ExpenseEntry tests.")

		# Try to find existing ledger accounts in this company:
		asset_accounts = frappe.get_all(
			"Account",
			filters={"company": self.company, "root_type": "Asset", "is_group": 0},
			pluck="name",
			limit_page_length=1,
		)
		expense_accounts = frappe.get_all(
			"Account",
			filters={"company": self.company, "root_type": "Expense", "is_group": 0},
			pluck="name",
			limit_page_length=1,
		)

		# If either account type missing, skip tests with instructive message.
		if not asset_accounts or not expense_accounts:
			msg = (
				"Site does not have required ledger accounts for testing.\n"
				"Need at least one Asset (ledger) account and one Expense (ledger) account "
				"in company `{company}`.\n"
				"Found Asset accounts: {asset}, Expense accounts: {expense}.\n"
				"Please create chart of accounts or run tests on a site with COA."
			).format(company=self.company, asset=asset_accounts, expense=expense_accounts)
			self.skipTest(msg)

		self.cash_account = asset_accounts[0]
		self.expense_account = expense_accounts[0]

	def tearDown(self):
		# keep the DB clean for other tests
		frappe.db.rollback()

	def _make_expense_entry(self, amount=100000):
		"""
		Create (but do not submit) an Expense Entry doc with a single detail line.
		"""
		doc = frappe.get_doc({
			"doctype": "Expense Entry",
			"company": self.company,
			"posting_date": nowdate(),
			"remarks": "Testing Expense Entry",
			"account_paid_from": self.cash_account,
			"details": [
				{
					"expense_label": None,
					"expense_account": self.expense_account,
					"amount": amount,
					"remarks": "Biaya perjalanan test"
				}
			]
		})
		doc.insert(ignore_permissions=True)
		return doc

	def _get_gl_entries(self, voucher_type, voucher_no):
		"""
		Helper to retrieve GL Entry rows for a voucher.
		"""
		return frappe.get_all(
			"GL Entry",
			filters={"voucher_type": voucher_type, "voucher_no": voucher_no},
			fields=["account", "debit", "credit", "is_cancelled"]
		)

	def test_expense_entry_submission_creates_gl_entries(self):
		expense = self._make_expense_entry(50000)
		expense.submit()

		gl_entries = self._get_gl_entries(expense.doctype, expense.name)
		self.assertTrue(gl_entries, "GL Entries not found after submit")

		# Sum debit and credit (as Decimal)
		total_debit = sum(Decimal(str(e.get("debit") or 0)) for e in gl_entries)
		total_credit = sum(Decimal(str(e.get("credit") or 0)) for e in gl_entries)
		self.assertEqual(total_debit, total_credit, "GL is not balanced after submit")

		# Check accounts used
		accounts = {e.get("account") for e in gl_entries}
		self.assertIn(self.expense_account, accounts)
		self.assertIn(self.cash_account, accounts)

	def test_cancel_creates_reversal_entries(self):
		expense = self._make_expense_entry(120000)
		expense.submit()
		expense.cancel()

		gl_entries = self._get_gl_entries(expense.doctype, expense.name)
		self.assertTrue(gl_entries, "No GL Entry found for Expense Entry after cancel")

		# There should be at least one entry marked cancelled (reversal)
		self.assertTrue(any(e.get("is_cancelled") for e in gl_entries), "No cancelled GL entry found (reversal missing)")

		# And total debits should still match total credits across all GL rows for the voucher
		total_debit = sum(Decimal(str(e.get("debit") or 0)) for e in gl_entries)
		total_credit = sum(Decimal(str(e.get("credit") or 0)) for e in gl_entries)
		self.assertEqual(total_debit, total_credit, "GL not balanced after cancel")

	def test_delete_removes_gl_entries_if_setting_enabled(self):
		# Enable Accounts Setting for deleting linked ledger entries
		frappe.db.set_single_value("Accounts Settings", "delete_linked_ledger_entries", 1)

		expense = self._make_expense_entry(75000)
		expense.submit()
		expense.cancel()
		name = expense.name
		expense.delete()

		gl_entries = self._get_gl_entries("Expense Entry", name)
		self.assertFalse(gl_entries, "GL Entries not deleted after document deletion with setting enabled")
