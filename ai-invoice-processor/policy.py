from pydantic import BaseModel, Field

from llm import llm


COMPANY_POLICY = """
You are validating a vendor invoice against the company's mandatory
invoice-processing policies.

Company policies:

1. The invoice must contain a valid PO number.
2. The invoice must contain a vendor name.
3. The invoice must contain the required invoice information.
4. Duplicate invoices must not be processed.
5. Any mandatory policy violation must require human review.
6. If all mandatory invoice-level requirements are satisfied,
   the invoice can proceed to Purchase Order validation.

Important:
At this stage, ONLY validate the invoice against the company policies.

Do NOT compare the invoice with the Purchase Order yet.
Purchase Order comparison will happen separately.
"""


class PolicyResult(BaseModel):
    status: str = Field(
        description="Either PASSED or REVIEW_REQUIRED"
    )

    remarks: list[str] = Field(
        default_factory=list,
        description="Reasons for any policy violations"
    )


structured_policy_llm = llm.with_structured_output(
    PolicyResult
)


def check_invoice_policy(invoice_data: dict) -> dict:

    prompt = f"""
{COMPANY_POLICY}

Invoice information:

{invoice_data}

Determine whether this invoice satisfies the company
invoice-processing policies.

Return:

- PASSED if all invoice-level mandatory policies are satisfied.
- REVIEW_REQUIRED if any mandatory policy is violated.

If PASSED, remarks must be an empty list.

If REVIEW_REQUIRED, provide clear and specific remarks
for every policy violation.
"""

    result = structured_policy_llm.invoke(prompt)

    return result.model_dump()