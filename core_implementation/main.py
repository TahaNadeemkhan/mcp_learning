import base64
from pydoc import doc
from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("DocumentMCP", stateless_http=True)

docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

# TODO: Write a tool to read a doc
@mcp.tool(name = "read_doc", description="Read a document by its ID")
async def read_doc(
        doc_id: str = Field("Id of the document to read"),
        ) -> str:
    """Read a document by its ID."""
    if not doc_id:
        raise ValueError(f"No document for ID: {doc_id} provided.")
    return docs[doc_id]

@mcp.resource("docs://documents", mime_type="application/json")
def list_docs() -> list[str]:
    return list(docs.keys())

@mcp.resource("docs://documents/{doc_id}", mime_type="application/json")
def read_doc(doc_id: str):
    if doc_id in docs:
        return {"name": doc_id, "content": docs[doc_id]}
    else:
        raise mcp.ResourceNotFound(f"Document '{doc_id}' not found.")

@mcp.resource("binary://logo", mime_type="image/png")
def get_logo():
    try:
        with open("logo.png", "rb") as f:
            data = f.read()
        encoded = base64.b64encode(data).decode("utf-8")
        return {"file name": "logo.png", "data": encoded}
    except:
        raise mcp.ResourceNotFound("logo file not found.")
    
@mcp.prompt(name="custom prompt", title="My prompt", description="Prompt for the guidance of the user")
def get_prompt(user_name: str):
    return f"Hello {user_name}"


mcp_server = mcp.streamable_http_app()
