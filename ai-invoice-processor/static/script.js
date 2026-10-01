// ==========================================
// AI AUTOMATED INVOICE PROCESSOR
// FRONTEND JAVASCRIPT
// ==========================================


// ------------------------------------------
// DOM ELEMENTS
// ------------------------------------------

const invoiceFolderInput =
    document.getElementById("invoice-folder");

const poFolderInput =
    document.getElementById("po-folder");

const invoiceFolderName =
    document.getElementById("invoice-folder-name");

const poFolderName =
    document.getElementById("po-folder-name");

const invoiceCount =
    document.getElementById("invoice-count");

const poCount =
    document.getElementById("po-count");

const processButton =
    document.getElementById("process-button");

const buttonText =
    document.getElementById("button-text");

const buttonSpinner =
    document.getElementById("button-spinner");

const progressContainer =
    document.getElementById("progress-container");

const progressText =
    document.getElementById("progress-text");

const progressPercentage =
    document.getElementById("progress-percentage");

const progressFill =
    document.getElementById("progress-fill");

const summarySection =
    document.getElementById("summary-section");

const resultsSection =
    document.getElementById("results-section");

const resultsBody =
    document.getElementById("results-body");

const totalCount =
    document.getElementById("total-count");

const passedCount =
    document.getElementById("passed-count");

const reviewCount =
    document.getElementById("review-count");

const errorMessage =
    document.getElementById("error-message");


// ------------------------------------------
// SELECTED FILES
// ------------------------------------------

let invoiceFiles = [];

let poFiles = [];


// ------------------------------------------
// INVOICE FOLDER SELECTED
// ------------------------------------------

invoiceFolderInput.addEventListener(
    "change",
    function () {

        invoiceFiles =
            Array.from(this.files)
                .filter(file =>
                    file.name
                        .toLowerCase()
                        .endsWith(".pdf")
                );


        if (invoiceFiles.length > 0) {

            const firstFile =
                this.files[0];

            const folderPath =
                firstFile.webkitRelativePath;

            const folderName =
                folderPath.split("/")[0];


            invoiceFolderName.textContent =
                folderName;

            invoiceCount.textContent =
                `${invoiceFiles.length} PDF file${invoiceFiles.length !== 1 ? "s" : ""}`;

        } else {

            invoiceFolderName.textContent =
                "No PDF files found";

            invoiceCount.textContent =
                "0 PDF files";
        }


        updateProcessButton();
    }
);


// ------------------------------------------
// PO FOLDER SELECTED
// ------------------------------------------

poFolderInput.addEventListener(
    "change",
    function () {

        poFiles =
            Array.from(this.files)
                .filter(file =>
                    file.name
                        .toLowerCase()
                        .endsWith(".pdf")
                );


        if (poFiles.length > 0) {

            const firstFile =
                this.files[0];

            const folderPath =
                firstFile.webkitRelativePath;

            const folderName =
                folderPath.split("/")[0];


            poFolderName.textContent =
                folderName;

            poCount.textContent =
                `${poFiles.length} PDF file${poFiles.length !== 1 ? "s" : ""}`;

        } else {

            poFolderName.textContent =
                "No PDF files found";

            poCount.textContent =
                "0 PDF files";
        }


        updateProcessButton();
    }
);


// ------------------------------------------
// ENABLE / DISABLE PROCESS BUTTON
// ------------------------------------------

function updateProcessButton() {

    const hasInvoices =
        invoiceFiles.length > 0;

    const hasPOs =
        poFiles.length > 0;


    processButton.disabled =
        !(hasInvoices && hasPOs);
}


// ------------------------------------------
// PROCESS BUTTON
// ------------------------------------------

processButton.addEventListener(
    "click",
    async function () {

        if (
            invoiceFiles.length === 0 ||
            poFiles.length === 0
        ) {

            showError(
                "Please select both an invoice folder and a purchase order folder."
            );

            return;
        }


        hideError();

        setProcessingState(true);

        showProgress();

        hideResults();


        try {

            const formData =
                new FormData();


            // ----------------------------------
            // ADD INVOICE FILES
            // ----------------------------------

            invoiceFiles.forEach(
                file => {

                    formData.append(
                        "invoice_files",
                        file,
                        file.name
                    );

                }
            );


            // ----------------------------------
            // ADD PO FILES
            // ----------------------------------

            poFiles.forEach(
                file => {

                    formData.append(
                        "po_files",
                        file,
                        file.name
                    );

                }
            );


            updateProgress(
                10,
                "Uploading invoice and PO files..."
            );


            // ----------------------------------
            // SEND TO FASTAPI
            // ----------------------------------

            const response =
                await fetch(
                    "/process",
                    {
                        method: "POST",

                        body: formData
                    }
                );


            updateProgress(
                90,
                "Processing invoice validation..."
            );


            // ----------------------------------
            // HANDLE HTTP ERROR
            // ----------------------------------

            if (!response.ok) {

                let errorText =
                    "Unable to process invoices.";

                try {

                    const errorData =
                        await response.json();

                    if (errorData.detail) {

                        errorText =
                            errorData.detail;
                    }

                } catch (error) {

                    // Ignore JSON parsing error
                }


                throw new Error(errorText);
            }


            // ----------------------------------
            // READ RESPONSE
            // ----------------------------------

            const data =
                await response.json();


            updateProgress(
                100,
                "Processing completed."
            );


            // ----------------------------------
            // DISPLAY RESULTS
            // ----------------------------------

            displayResults(data);


        } catch (error) {

            console.error(
                "Processing error:",
                error
            );


            showError(
                error.message ||
                "An unexpected error occurred while processing the invoices."
            );


            hideProgress();

        } finally {

            setProcessingState(false);
        }

    }
);


// ------------------------------------------
// DISPLAY RESULTS
// ------------------------------------------

function displayResults(data) {

    summarySection.classList.remove("hidden");

    resultsSection.classList.remove("hidden");


    // ----------------------------------
    // SUMMARY
    // ----------------------------------

    totalCount.textContent =
        data.total_processed ?? 0;

    passedCount.textContent =
        data.passed ?? 0;

    reviewCount.textContent =
        data.review_required ?? 0;


    // ----------------------------------
    // CLEAR OLD RESULTS
    // ----------------------------------

    resultsBody.innerHTML = "";


    const results =
        data.results || [];


    // ----------------------------------
    // NO RESULTS
    // ----------------------------------

    if (results.length === 0) {

        const row =
            document.createElement("tr");

        row.innerHTML = `
            <td colspan="5" style="text-align:center;">
                No invoices were processed.
            </td>
        `;

        resultsBody.appendChild(row);

        return;
    }


    // ----------------------------------
    // ADD EACH RESULT
    // ----------------------------------

    results.forEach(
        (result, index) => {

            const row =
                document.createElement("tr");


            // Invoice
            const invoiceCell =
                document.createElement("td");

            invoiceCell.textContent =
                result.invoice || "-";


            // PO
            const poCell =
                document.createElement("td");

            poCell.textContent =
                result.po || "-";


            // Status
            const statusCell =
                document.createElement("td");

            const statusBadge =
                document.createElement("span");


            if (
                result.status === "PASSED"
            ) {

                statusBadge.className =
                    "status status-passed";

                statusBadge.textContent =
                    "PASSED";

            } else {

                statusBadge.className =
                    "status status-review";

                statusBadge.textContent =
                    "REVIEW REQUIRED";
            }


            statusCell.appendChild(
                statusBadge
            );


            // Remarks
            const remarksCell =
                document.createElement("td");

            remarksCell.className =
                "remarks";


            const remarks =
                result.remarks || [];


            if (
                remarks.length === 0
            ) {

                const noRemarks =
                    document.createElement("span");

                noRemarks.className =
                    "no-remarks";

                noRemarks.textContent =
                    "—";

                remarksCell.appendChild(
                    noRemarks
                );

            } else {

                remarksCell.innerHTML =
                    remarks
                        .map(
                            remark =>
                                `<div>• ${escapeHtml(remark)}</div>`
                        )
                        .join("");
            }


            // Number
            const numberCell =
                document.createElement("td");

            numberCell.textContent =
                index + 1;


            // Add cells
            row.appendChild(
                numberCell
            );

            row.appendChild(
                invoiceCell
            );

            row.appendChild(
                poCell
            );

            row.appendChild(
                statusCell
            );

            row.appendChild(
                remarksCell
            );


            resultsBody.appendChild(
                row
            );

        }
    );


    // ----------------------------------
    // SCROLL TO RESULTS
    // ----------------------------------

    resultsSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


// ------------------------------------------
// ESCAPE HTML
// ------------------------------------------

function escapeHtml(value) {

    const div =
        document.createElement("div");

    div.textContent =
        value;

    return div.innerHTML;
}


// ------------------------------------------
// PROCESSING STATE
// ------------------------------------------

function setProcessingState(
    processing
) {

    if (processing) {

        processButton.disabled =
            true;

        buttonText.textContent =
            "Processing...";

        buttonSpinner.classList.remove(
            "hidden"
        );

        invoiceFolderInput.disabled =
            true;

        poFolderInput.disabled =
            true;

    } else {

        buttonText.textContent =
            "Process Invoices";

        buttonSpinner.classList.add(
            "hidden"
        );

        invoiceFolderInput.disabled =
            false;

        poFolderInput.disabled =
            false;


        updateProcessButton();
    }
}


// ------------------------------------------
// PROGRESS
// ------------------------------------------

function showProgress() {

    progressContainer.classList.remove(
        "hidden"
    );

    updateProgress(
        0,
        "Preparing..."
    );
}


function hideProgress() {

    progressContainer.classList.add(
        "hidden"
    );
}


function updateProgress(
    percentage,
    message
) {

    progressFill.style.width =
        `${percentage}%`;

    progressPercentage.textContent =
        `${percentage}%`;

    progressText.textContent =
        message;
}


// ------------------------------------------
// ERROR
// ------------------------------------------

function showError(
    message
) {

    errorMessage.textContent =
        message;

    errorMessage.classList.remove(
        "hidden"
    );


    errorMessage.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });
}


function hideError() {

    errorMessage.classList.add(
        "hidden"
    );

    errorMessage.textContent =
        "";
}


// ------------------------------------------
// HIDE RESULTS
// ------------------------------------------

function hideResults() {

    summarySection.classList.add(
        "hidden"
    );

    resultsSection.classList.add(
        "hidden"
    );

    resultsBody.innerHTML =
        "";
}