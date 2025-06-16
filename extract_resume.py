import fitz  # PyMuPDF
def extract_text_from_pdf(stream=None, file_path=None):
    """
    Extracts text content from a PDF, either from a file path or an in-memory stream.

    Args:
        stream (bytes, optional): The byte stream of the PDF file.
        file_path (str, optional): The file path to the PDF.

    Returns:
        str: The extracted text content, or an empty string if an error occurs.
    """
    try:
        # Check if a byte stream is provided
        if stream:
            # Open the PDF from the in-memory stream
            doc = fitz.open(stream=stream, filetype="pdf")
        # Otherwise, check if a file path is provided
        elif file_path:
            doc = fitz.open(file_path)
        # If neither is provided, return empty
        else:
            return ""

        text = "".join(page.get_text() for page in doc)
        doc.close()
        return text
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return ""