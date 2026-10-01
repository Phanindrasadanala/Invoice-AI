from pathlib import Path
import shutil


def create_passed_folders(
    invoice_folder: str,
    po_folder: str
):
    invoice_folder_path = Path(invoice_folder)
    po_folder_path = Path(po_folder)

    invoices_passed = (
        invoice_folder_path.parent / "invoices_passed"
    )

    purchase_orders_passed = (
        po_folder_path.parent / "purchase_orders_passed"
    )

    invoices_passed.mkdir(
        parents=True,
        exist_ok=True
    )

    purchase_orders_passed.mkdir(
        parents=True,
        exist_ok=True
    )

    return invoices_passed, purchase_orders_passed


def move_passed_files(
    invoice_file: Path,
    po_file: Path,
    invoice_folder: str,
    po_folder: str
):
    invoices_passed, purchase_orders_passed = (
        create_passed_folders(
            invoice_folder,
            po_folder
        )
    )

    invoice_destination = (
        invoices_passed / invoice_file.name
    )

    po_destination = (
        purchase_orders_passed / po_file.name
    )

    shutil.move(
        str(invoice_file),
        str(invoice_destination)
    )

    shutil.move(
        str(po_file),
        str(po_destination)
    )

    return {
        "invoice": str(invoice_destination),
        "po": str(po_destination)
    }