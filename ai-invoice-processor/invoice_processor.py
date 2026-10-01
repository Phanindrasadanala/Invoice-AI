from pathlib import Path

from pdf_reader import extract_text_from_pdf
from llm import extract_invoice_data, extract_po_data
from policy import check_invoice_policy
from validator import validate_invoice_against_po
from file_manager import move_passed_files


def find_po_file(po_folder: str, po_number: str):
    """
    Find the PO PDF corresponding to the PO number
    extracted from the invoice.
    """

    po_folder_path = Path(po_folder)

    for file in po_folder_path.glob("*.pdf"):
        if po_number.lower() in file.stem.lower():
            return file

    return None


def process_invoice(
    invoice_file: Path,
    po_folder: str,
    invoice_folder: str
):
    """
    Process one invoice completely.

    Workflow:

    1. Read invoice
    2. Extract invoice information
    3. Check company policy
    4. Get PO number
    5. Find matching PO
    6. Read PO
    7. Extract PO information
    8. Compare invoice with PO
    9. If passed, move invoice + PO
    10. Return final result
    """

    print("\n" + "=" * 60)
    print(f"PROCESSING: {invoice_file.name}")
    print("=" * 60)

    # --------------------------------------------------
    # 1. READ INVOICE
    # --------------------------------------------------

    print("[1] Reading invoice...")

    invoice_text = extract_text_from_pdf(
        str(invoice_file)
    )

    print("[1] Invoice read successfully.")

    # --------------------------------------------------
    # 2. EXTRACT INVOICE INFORMATION
    # --------------------------------------------------

    print("[2] Extracting invoice information...")

    invoice_data = extract_invoice_data(
        invoice_text
    )

    invoice_dict = invoice_data.model_dump()

    print("[2] Invoice information extracted.")
    print(invoice_dict)

    # --------------------------------------------------
    # 3. CHECK COMPANY POLICY
    # --------------------------------------------------

    print("[3] Checking company policy...")

    policy_result = check_invoice_policy(
        invoice_dict
    )

    print(
        f"[3] Policy result: "
        f"{policy_result['status']}"
    )

    # --------------------------------------------------
    # 4. STOP IF POLICY FAILED
    # --------------------------------------------------

    if policy_result["status"] == "REVIEW_REQUIRED":

        print("[3] Invoice requires review.")
        print("[3] Reason:")

        for remark in policy_result["remarks"]:
            print(f"    - {remark}")

        return {
            "invoice": invoice_file.name,
            "po": None,
            "invoice_data": invoice_dict,
            "po_data": None,
            "status": "REVIEW_REQUIRED",
            "remarks": policy_result["remarks"],
            "moved_files": None
        }

    # --------------------------------------------------
    # 5. GET PO NUMBER
    # --------------------------------------------------

    print("[4] Getting PO number...")

    po_number = invoice_data.po_number

    if not po_number:

        print("[4] PO number not found.")

        return {
            "invoice": invoice_file.name,
            "po": None,
            "invoice_data": invoice_dict,
            "po_data": None,
            "status": "REVIEW_REQUIRED",
            "remarks": [
                "Invoice does not contain a valid PO number."
            ],
            "moved_files": None
        }

    print(f"[4] PO number: {po_number}")

    # --------------------------------------------------
    # 6. FIND MATCHING PO
    # --------------------------------------------------

    print("[5] Searching for matching PO...")

    po_file = find_po_file(
        po_folder,
        po_number
    )

    if not po_file:

        print(
            f"[5] PO file not found for {po_number}."
        )

        return {
            "invoice": invoice_file.name,
            "po": None,
            "invoice_data": invoice_dict,
            "po_data": None,
            "status": "REVIEW_REQUIRED",
            "remarks": [
                f"PO file not found for {po_number}."
            ],
            "moved_files": None
        }

    print(f"[5] Matching PO found: {po_file.name}")

    # --------------------------------------------------
    # 7. READ PO
    # --------------------------------------------------

    print("[6] Reading PO...")

    po_text = extract_text_from_pdf(
        str(po_file)
    )

    print("[6] PO read successfully.")

    # --------------------------------------------------
    # 8. EXTRACT PO INFORMATION
    # --------------------------------------------------

    print("[7] Extracting PO information...")

    po_data = extract_po_data(
        po_text
    )

    po_dict = po_data.model_dump()

    print("[7] PO information extracted.")
    print(po_dict)

    # --------------------------------------------------
    # 9. COMPARE INVOICE WITH PO
    # --------------------------------------------------

    print("[8] Comparing invoice with PO...")

    validation_result = validate_invoice_against_po(
        invoice_dict,
        po_dict
    )

    print(
        f"[8] Validation result: "
        f"{validation_result['status']}"
    )

    # --------------------------------------------------
    # 10. SHOW REMARKS
    # --------------------------------------------------

    if validation_result["remarks"]:

        print("[8] Remarks:")

        for remark in validation_result["remarks"]:
            print(f"    - {remark}")

    # --------------------------------------------------
    # 11. MOVE FILES ONLY IF PASSED
    # --------------------------------------------------

    if validation_result["status"] == "PASSED":

        print("[9] Invoice passed validation.")
        print("[9] Moving invoice and PO...")

        moved_files = move_passed_files(
            invoice_file=invoice_file,
            po_file=po_file,
            invoice_folder=invoice_folder,
            po_folder=po_folder
        )

        print("[9] Invoice and PO moved successfully.")

    else:

        print(
            "[9] Invoice requires review. "
            "Files will remain in original folders."
        )

        moved_files = None

    # --------------------------------------------------
    # 12. FINAL RESULT
    # --------------------------------------------------

    return {
        "invoice": invoice_file.name,
        "po": po_file.name,
        "invoice_data": invoice_dict,
        "po_data": po_dict,
        "status": validation_result["status"],
        "remarks": validation_result["remarks"],
        "moved_files": moved_files
    }


def process_all_invoices(
    invoice_folder: str,
    po_folder: str
):
    """
    Process every invoice in the invoice folder
    one by one.
    """

    invoice_folder_path = Path(invoice_folder)

    invoice_files = sorted(
        invoice_folder_path.glob("*.pdf")
    )

    print("\n" + "=" * 60)
    print("AI AUTOMATED INVOICE PROCESSOR")
    print("=" * 60)

    print(
        f"Invoice folder: {invoice_folder}"
    )

    print(
        f"PO folder: {po_folder}"
    )

    print(
        f"Found {len(invoice_files)} invoice(s)."
    )

    results = []

    # Process invoices one by one
    for invoice_file in invoice_files:

        result = process_invoice(
            invoice_file=invoice_file,
            po_folder=po_folder,
            invoice_folder=invoice_folder
        )

        results.append(result)

    # --------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------

    passed = sum(
        1
        for result in results
        if result["status"] == "PASSED"
    )

    review_required = sum(
        1
        for result in results
        if result["status"] == "REVIEW_REQUIRED"
    )

    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)

    print(f"Total invoices: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Review required: {review_required}")

    print("\nRESULTS:")

    for result in results:

        print(
            f"\n{result['invoice']} "
            f"→ {result['status']}"
        )

        if result["remarks"]:

            for remark in result["remarks"]:
                print(f"   Remark: {remark}")

    return results