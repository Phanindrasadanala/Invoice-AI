import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field


load_dotenv()


class InvoiceData(BaseModel):
    invoice_number: str | None = Field(default=None)
    invoice_date: str | None = Field(default=None)
    po_number: str | None = Field(default=None)
    vendor_name: str | None = Field(default=None)
    material: str | None = Field(default=None)
    quantity: float | None = Field(default=None)
    unit_price: float | None = Field(default=None)
    total_amount: float | None = Field(default=None)


llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

structured_llm = llm.with_structured_output(InvoiceData)


def extract_invoice_data(invoice_text: str) -> InvoiceData:

    prompt = f"""
You are an invoice document extraction system.

Read the invoice text below and extract the requested information.

Do not invent information.
If a field is not present, return null.

Extract:
- Invoice number
- Invoice date
- PO number
- Vendor name
- Material
- Quantity
- Unit price
- Total invoice amount

Invoice text:

{invoice_text}
"""

    return structured_llm.invoke(prompt)

class POData(BaseModel):
    po_number: str | None = Field(default=None)
    po_date: str | None = Field(default=None)
    vendor_name: str | None = Field(default=None)
    material: str | None = Field(default=None)
    quantity: float | None = Field(default=None)
    unit_price: float | None = Field(default=None)
    total_amount: float | None = Field(default=None)


structured_po_llm = llm.with_structured_output(POData)


def extract_po_data(po_text: str) -> POData:

    prompt = f"""
You are a Purchase Order document extraction system.

Read the Purchase Order text below and extract the requested
information.

Do not invent information.
If a field is not present, return null.

Extract:

- PO number
- PO date
- Vendor name
- Material
- Approved quantity
- Unit price
- Approved total amount

Purchase Order text:

{po_text}
"""

    return structured_po_llm.invoke(prompt)