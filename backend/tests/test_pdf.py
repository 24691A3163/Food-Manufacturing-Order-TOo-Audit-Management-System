from backend.app.services.benchmark_service import BenchmarkService
from backend.app.services.pdf_service import PDFService
from backend.app.models.invoice import Invoice

def test_pdf_invoice_generation(db_session):
    res = BenchmarkService.run_benchmark(db_session)
    invoice = db_session.query(Invoice).first()
    assert invoice is not None
    
    pdf_bytes = PDFService.generate_invoice_pdf(invoice)
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 2000
    assert pdf_bytes.startswith(b"%PDF-")

