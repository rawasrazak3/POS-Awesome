import frappe
from frappe import _

@frappe.whitelist()
def create_petty_cash(date, entry_type, pos_profile, amount, note):
    try:
        doc = frappe.new_doc("Petty Cash")
        doc.date = date
        doc.entry_type = entry_type
        doc.pos_profile = pos_profile
        doc.amount = amount
        doc.note = note

        doc.insert(ignore_permissions=True)
        doc.submit()

        return {
            "status": "success",
            "message": _("Petty Cash entry created and submitted."),
            "name": doc.name
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Petty Cash API Error")
        return {
            "status": "error",
            "message": str(e)
        }
