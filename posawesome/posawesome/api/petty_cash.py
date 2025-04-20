import frappe
from frappe import _
from frappe.utils import flt

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

@frappe.whitelist()
def get_petty_cash(pos_opening_shift):
    petty_cash_entries = frappe.get_all(
        "Petty Cash",
        filters={"docstatus": 1, "posa_pos_opening_shift": pos_opening_shift},
        fields=["name", "entry_type", "note", "amount"],
    )

    petty_cash_in = []
    petty_cash_out = []
    total_payin = 0
    total_payout = 0

    for entry in petty_cash_entries:
        if entry.entry_type == "Pay In":
            petty_cash_in.append({
                "name": entry.name,
                "note": entry.note,
                "amount": entry.amount
            })
            total_payin += flt(entry.amount)
        elif entry.entry_type == "Pay Out":
            petty_cash_out.append({
                "name": entry.name,
                "note": entry.note,
                "amount": entry.amount
            })
            total_payout += flt(entry.amount)

    return {
        "petty_cash_in": petty_cash_in,
        "petty_cash_out": petty_cash_out,
        "custom_total_payin": total_payin,
        "custom_total_payout": total_payout,
        "custom_closing_amount": total_payin - total_payout
    }
