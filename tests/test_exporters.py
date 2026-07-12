import pandas as pd
import pytest
from clinipub.exporters import JournalHTMLExporter


def test_exporter_empty_dataframe_error():
    with pytest.raises(ValueError, match="The input DataFrame cannot be empty."):
        JournalHTMLExporter(pd.DataFrame(), journal="nejm")


def test_exporter_invalid_journal_style():
    df = pd.DataFrame({"age": [55, 62]})
    with pytest.raises(ValueError, match="Unsupported journal style"):
        JournalHTMLExporter(df, journal="nature")


def test_exporter_css_injection_matching():
    df = pd.DataFrame({"age": [55, 62]})
    
    # Verify NEJM traditional serif injection
    nejm_exporter = JournalHTMLExporter(df, journal="nejm")
    nejm_html = nejm_exporter.export()
    assert "Times New Roman" in nejm_html
    
    # Verify JAMA modern sans-serif injection
    jama_exporter = JournalHTMLExporter(df, journal="jama")
    jama_html = jama_exporter.export()
    assert "Arial" in jama_html
