# Copyright (c) 2026, PT Sopwer Teknologi Indonesia and contributors
# For license information, please see license.txt

"""Bank Reconciliation Tool integration untuk Expense Entry.

Expense Entry memposting GL-nya sendiri (credit ke `account_paid_from` = akun bank/kas)
tanpa lewat Journal Entry. Modul ini menyuntikkan query pencocokan lewat hook
`get_matching_queries` agar Expense Entry muncul sebagai kandidat voucher saat
mencocokkan Bank Transaction. Lihat journal_plus/hooks.py.
"""

import frappe
from frappe.query_builder.custom import ConstantColumn

from erpnext.accounts.utils import get_account_currency


def get_matching_queries(
	bank_account,
	company,
	transaction,
	document_types,
	exact_match,
	account_from_to,
	from_date=None,
	to_date=None,
	filter_by_reference_date=None,
	from_reference_date=None,
	to_reference_date=None,
	common_filters=None,
):
	"""Kembalikan list query (frappe.qb) kandidat Expense Entry untuk Bank Reconciliation Tool.

	Signature mengikuti pemanggil erpnext: bank_reconciliation_tool.get_queries().
	"""
	# Hanya jalan kalau user mencentang checkbox "Expense Entry" (frappe.scrub -> "expense_entry").
	if not document_types or "expense_entry" not in document_types:
		return []

	# Expense Entry selalu uang keluar (credit akun bank) -> cuma cocok untuk withdrawal.
	if not (transaction.withdrawal and transaction.withdrawal > 0.0):
		return []

	currency = get_account_currency(bank_account)

	ee = frappe.qb.DocType("Expense Entry")

	amount_equality = ee.total == common_filters.amount
	amount_rank = frappe.qb.terms.Case().when(amount_equality, 1).else_(0)
	amount_condition = amount_equality if exact_match else ee.total > 0.0

	ref_condition = ee.payment_reference == common_filters.reference_no
	ref_rank = frappe.qb.terms.Case().when(ref_condition, 1).else_(0)

	query = (
		frappe.qb.from_(ee)
		.select(
			(ref_rank + amount_rank + 1).as_("rank"),
			ConstantColumn("Expense Entry").as_("doctype"),
			ee.name,
			ee.total.as_("paid_amount"),
			ee.payment_reference.as_("reference_no"),
			ee.posting_date.as_("reference_date"),
			ee.payment_to.as_("party"),
			ConstantColumn("").as_("party_type"),
			ee.posting_date,
			ee.currency,
		)
		.where(ee.docstatus == 1)
		.where(ee.clearance_date.isnull())
		.where(ee.account_paid_from == common_filters.bank_account)
		.where(ee.currency == currency)
		.where(amount_condition)
	)

	if from_date and to_date:
		query = query.where(ee.posting_date[from_date:to_date])

	return [query]
