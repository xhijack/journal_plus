app_name = "journal_plus"
app_title = "Journal Plus"
app_publisher = "PT Sopwer Teknologi Indonesia"
app_description = "Another Journal for ERPNext"
app_email = "ramdani@sopwer.net"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "journal_plus",
# 		"logo": "/assets/journal_plus/logo.png",
# 		"title": "Journal Plus",
# 		"route": "/journal_plus",
# 		"has_permission": "journal_plus.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/journal_plus/css/journal_plus.css"
# app_include_js = "/assets/journal_plus/js/journal_plus.js"

# include js, css files in header of web template
# web_include_css = "/assets/journal_plus/css/journal_plus.css"
# web_include_js = "/assets/journal_plus/js/journal_plus.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "journal_plus/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "journal_plus/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "journal_plus.utils.jinja_methods",
# 	"filters": "journal_plus.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "journal_plus.install.before_install"
# after_install = "journal_plus.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "journal_plus.uninstall.before_uninstall"
# after_uninstall = "journal_plus.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "journal_plus.utils.before_app_install"
# after_app_install = "journal_plus.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "journal_plus.utils.before_app_uninstall"
# after_app_uninstall = "journal_plus.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "journal_plus.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Accounting Dimension": {
		"on_update": "journal_plus.migration.create_accounting_dimensions",
        "validate": "journal_plus.validations.validate_mandatory_dimensions",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"journal_plus.tasks.all"
# 	],
# 	"daily": [
# 		"journal_plus.tasks.daily"
# 	],
# 	"hourly": [
# 		"journal_plus.tasks.hourly"
# 	],
# 	"weekly": [
# 		"journal_plus.tasks.weekly"
# 	],
# 	"monthly": [
# 		"journal_plus.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "journal_plus.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "journal_plus.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "journal_plus.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["journal_plus.utils.before_request"]
# after_request = ["journal_plus.utils.after_request"]

# Job Events
# ----------
# before_job = ["journal_plus.utils.before_job"]
# after_job = ["journal_plus.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"journal_plus.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

