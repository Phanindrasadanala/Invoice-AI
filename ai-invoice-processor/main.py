from pathlib import Path
import shutil
import tempfile

from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles

from invoice_processor import process_all_invoices


app = FastAPI(
    title="AI Automated Invoice Processor"
)


# ============================================================
# FRONTEND
# ============================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


@app.get("/")
def home():
    from fastapi.responses import FileResponse

    return FileResponse("static/index.html")


# ============================================================
# PROCESS INVOICES
# ============================================================

@app.post("/process")
async def process_invoices(
    invoice_files: list[UploadFile] = File(...),
    po_files: list[UploadFile] = File(...)
):

    # --------------------------------------------------------
    # Create temporary processing directories
    # --------------------------------------------------------

    temp_directory = Path(
        tempfile.mkdtemp(
            prefix="invoice_processor_"
        )
    )

    invoice_folder = (
        temp_directory / "invoices"
    )

    po_folder = (
        temp_directory / "purchase_orders"
    )

    invoice_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    po_folder.mkdir(
        parents=True,
        exist_ok=True
    )


    try:

        # ----------------------------------------------------
        # Save uploaded invoice files
        # ----------------------------------------------------

        for invoice in invoice_files:

            if not invoice.filename:
                continue

            if not invoice.filename.lower().endswith(".pdf"):
                continue

            destination = (
                invoice_folder /
                Path(invoice.filename).name
            )

            with open(destination, "wb") as buffer:

                shutil.copyfileobj(
                    invoice.file,
                    buffer
                )


        # ----------------------------------------------------
        # Save uploaded PO files
        # ----------------------------------------------------

        for po in po_files:

            if not po.filename:
                continue

            if not po.filename.lower().endswith(".pdf"):
                continue

            destination = (
                po_folder /
                Path(po.filename).name
            )

            with open(destination, "wb") as buffer:

                shutil.copyfileobj(
                    po.file,
                    buffer
                )


        # ----------------------------------------------------
        # Process invoices using existing processor
        # ----------------------------------------------------

        results = process_all_invoices(
            invoice_folder=str(invoice_folder),
            po_folder=str(po_folder)
        )


        # ----------------------------------------------------
        # Calculate summary
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # Return response to frontend
        # ----------------------------------------------------

        return {
            "total_processed": len(results),
            "passed": passed,
            "review_required": review_required,
            "results": results
        }


    finally:

        # ----------------------------------------------------
        # Clean up temporary files
        # ----------------------------------------------------

        shutil.rmtree(
            temp_directory,
            ignore_errors=True
        )