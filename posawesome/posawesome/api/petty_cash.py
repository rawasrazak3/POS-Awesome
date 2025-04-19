import frappe
from frappe import _

@frappe.whitelist()
def create_petty_cash(date, entry_type, pos_profile, amount, note, posa_pos_opening_shift):
    try:
        doc = frappe.new_doc("Petty Cash")
        doc.date = date
        doc.entry_type = entry_type
        doc.pos_profile = pos_profile
        doc.amount = amount
        doc.note = note
        doc.posa_pos_opening_shift = posa_pos_opening_shift
        # doc.opening_amount = opening_amount
        # doc.closing_amount = closing_amount

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
