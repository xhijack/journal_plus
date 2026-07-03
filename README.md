# 🧾 Journal Plus
### Simplify your accounting workflow in ERPNext

**Journal Plus** is a smart extension app for **ERPNext** that makes journal transactions easy for non-accountants.  
No more manual debit/credit entries — just record your expenses, incomes, or fund transfers, and Journal Plus will handle the ledger posting automatically.  

---

## ✨ Key Features

### 💸 Expense Entry
- Record expenses without worrying about debits and credits.  
- Automatically creates General Ledger entries on submit.  
- Supports multiple expense lines with different accounts and remarks.  
- Fully integrated with ERPNext’s accounting structure.  
- Cancel and deletion behavior follow ERPNext accounting best practices.  

### 🧩 Accounting Dimensions
- Seamless integration with ERPNext **Accounting Dimensions**.  
- Add contextual metadata (like Branch, Cost Center, or Department) to every entry line.  
- Dimension-based reporting for financial analysis and budget control.
- Automatically create custom field based on accounting dimensions  


### 💰 Income Entry *(coming soon)*
- Simplify revenue recording for non-finance users.  
- Automatically maps income to the correct accounts.  
- Supports multiple income sources in a single transaction.  

### 🔁 Fund Transfer *(coming soon)*
- Easily transfer funds between bank or cash accounts.  
- Auto-posts both debit and credit sides with validation logic.  
- Perfect for inter-department or inter-branch transactions.  


---

## ⚙️ Technical Highlights
- Built with **Frappe Framework v15+** and fully compatible with **ERPNext v15+**.  
- Inherits `AccountsController` for accurate accounting behavior (submit, cancel, delete).  
- Uses ERPNext’s native `make_gl_entries()` for consistent ledger posting.  
- Includes automated test cases for GL balance, reversals, and deletion logic.  
- Modular and extensible design — easy to add new transaction types (Income, Fund Transfer, etc).  

---

## 🧠 Why Journal Plus?
ERPNext’s default *Journal Entry* is powerful — but built for accountants.  
**Journal Plus** simplifies accounting workflows so that:
- **Admins or non-finance users** can record expenses or fund transfers confidently.  
- All ledger integrity and accounting rules are enforced automatically.  
- It saves time and reduces the learning curve for teams outside finance.  

---

## 🧑‍💻 Installation

```bash
# From your bench directory
bench get-app https://github.com/xhijack/journal_plus.git
bench --site your-site-name install-app journal_plus
bench migrate
```
---
## Contribution
From PT Sopwer Teknologi Indonesia
