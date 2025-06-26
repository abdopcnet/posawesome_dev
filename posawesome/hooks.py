# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "posawesome"
app_title = "POS Awesome"
app_publisher = "future-support"
app_description = "posawesome"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "abdopcnet@gmail.com"
app_license = "GPLv3"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/posawesome/css/posawesome.css"
# app_include_js = "/assets/posawesome/js/posawesome.js"
app_include_js = [
    "/assets/posawesome/node_modules/vue/dist/vue.global.prod.js",
    "/assets/posawesome/node_modules/vuetify/dist/vuetify.js",
    "posawesome.bundle.js",
]

# /assets/posawesome/node_modules/vue/dist/vue.global.prod.js
# include js, css files in header of web template
# web_include_css = "/assets/posawesome/css/posawesome.css"
# web_include_js = "/assets/posawesome/js/posawesome.js"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "POS Profile": "posawesome/api/pos_profile.js",
    "Sales Invoice": "posawesome/api/invoice.js",
    "Company": "posawesome/api/company.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "posawesome.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "posawesome.install.before_install"
# after_install = "posawesome.install.after_install"
# before_uninstall = "posawesome.uninstall.before_uninstall"
after_uninstall = "posawesome.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "posawesome.notifications.get_notification_config"

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

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Sales Invoice": {
        "validate": "posawesome.posawesome.api.invoice.validate",
        "before_submit": "posawesome.posawesome.api.invoice.before_submit",
        "before_cancel": "posawesome.posawesome.api.invoice.before_cancel",
    },
    "Customer": {
        "validate": "posawesome.posawesome.api.customer.validate",
        "after_insert": "posawesome.posawesome.api.customer.after_insert",
    },
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"posawesome.tasks.all"
# 	],
# 	"daily": [
# 		"posawesome.tasks.daily"
# 	],
# 	"hourly": [
# 		"posawesome.tasks.hourly"
# 	],
# 	"weekly": [
# 		"posawesome.tasks.weekly"
# 	]
# 	"monthly": [
# 		"posawesome.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "posawesome.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "posawesome.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "posawesome.task.get_dashboard_data"
# }

# override_doctype_class = {
# "doctype": "method",
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

fixtures = [
    {"doctype": "Custom Field", "filters": [["module", "=", "POSAwesome"]]},
    {"doctype": "Property Setter", "filters": [["module", "=", "POSAwesome"]]},
]
