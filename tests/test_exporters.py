import os

import pandas as pd
import pytest
from clinipub.exporters import JournalHTMLExporter, JournalDocxExporter


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


def test_docx_exporter_empty_dataframe_error():
    with pytest.raises(ValueError, match="The input DataFrame cannot be empty."):
        JournalDocxExporter(pd.DataFrame(), journal="nejm")


def test_docx_exporter_file_generation(tmp_path):
    df = pd.DataFrame({"Arm A": ["12 (10%)", "45.2 (4.1)"], "Arm B": ["15 (12%)", "42.1 (3.9)"]})
    df.index = ["Adverse Events", "Mean Age"]
    
    output_file = tmp_path / "test_table1.docx"
    exporter = JournalDocxExporter(df, journal="nejm")
    exporter.save(str(output_file))
    
    assert os.path.exists(output_file)
    assert os.path.getsize(output_file) > 0
