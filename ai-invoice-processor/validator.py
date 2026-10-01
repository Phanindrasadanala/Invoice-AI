def validate_invoice_against_po(
    invoice_data: dict,
    po_data: dict
) -> dict:

    remarks = []

    # --------------------------------------------------
    # 1. PO NUMBER
    # --------------------------------------------------

    invoice_po = invoice_data.get("po_number")
    po_number = po_data.get("po_number")

    if invoice_po != po_number:
        remarks.append(
            f"PO number mismatch: invoice has "
            f"{invoice_po}, but PO has {po_number}."
        )

    # --------------------------------------------------
    # 2. VENDOR
    # --------------------------------------------------

    invoice_vendor = invoice_data.get("vendor_name")
    po_vendor = po_data.get("vendor_name")

    if invoice_vendor != po_vendor:
        remarks.append(
            f"Vendor mismatch: invoice vendor is "
            f"'{invoice_vendor}', while PO vendor is "
            f"'{po_vendor}'."
        )

    # --------------------------------------------------
    # 3. MATERIAL
    # --------------------------------------------------

    invoice_material = invoice_data.get("material")
    po_material = po_data.get("material")

    if invoice_material != po_material:
        remarks.append(
            f"Material mismatch: invoice has "
            f"'{invoice_material}', while PO has "
            f"'{po_material}'."
        )

    # --------------------------------------------------
    # 4. QUANTITY
    # --------------------------------------------------

    invoice_quantity = invoice_data.get("quantity")
    po_quantity = po_data.get("quantity")

    if (
        invoice_quantity is None
        or po_quantity is None
    ):
        remarks.append(
            "Quantity information is missing."
        )

    elif invoice_quantity > po_quantity:
        remarks.append(
            f"Invoice quantity ({invoice_quantity}) "
            f"exceeds approved PO quantity "
            f"({po_quantity})."
        )

    # --------------------------------------------------
    # 5. AMOUNT
    # --------------------------------------------------

    invoice_amount = invoice_data.get("total_amount")
    po_amount = po_data.get("total_amount")

    if (
        invoice_amount is None
        or po_amount is None
    ):
        remarks.append(
            "Amount information is missing."
        )

    elif invoice_amount > po_amount:
        remarks.append(
            f"Invoice amount ({invoice_amount}) "
            f"exceeds approved PO amount "
            f"({po_amount})."
        )

    # --------------------------------------------------
    # FINAL DECISION
    # --------------------------------------------------

    if remarks:
        status = "REVIEW_REQUIRED"
    else:
        status = "PASSED"

    return {
        "status": status,
        "remarks": remarks
    }