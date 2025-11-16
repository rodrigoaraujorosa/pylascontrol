# tests/test_pylascontrol.py

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pylascontrol.pylascontrol import (
    load_budget_excel,
    plot_chart_by_type,
    MONTHS_MAP,
    LABELS_TO_IGNORE
)


class TestConstants:
    """Test module constants"""
    
    def test_months_map_has_all_months(self):
        """Test that MONTHS_MAP contains all 12 months"""
        assert len(MONTHS_MAP) == 12
        assert all(1 <= month <= 12 for month in MONTHS_MAP.values())
    
    def test_labels_to_ignore_not_empty(self):
        """Test that LABELS_TO_IGNORE is not empty"""
        assert len(LABELS_TO_IGNORE) > 0
        assert "Total" in LABELS_TO_IGNORE


class TestLoadBudgetExcel:
    """Test load_budget_excel function"""
    
    @pytest.fixture
    def mock_excel_data(self):
        """Create mock Excel data"""
        data = {
            "Unnamed: 0": ["", "RECEITA", "Salário", "DESPESAS", "Cotidiano", "Alimentação", "Total"],
            "JAN": ["JAN", np.nan, 5000.0, np.nan, np.nan, 800.0, 5800.0],
            "FEV": ["FEV", np.nan, 5000.0, np.nan, np.nan, 850.0, 5850.0],
            "MAR": ["MAR", np.nan, 5200.0, np.nan, np.nan, 900.0, 6100.0],
        }
        return pd.DataFrame(data)
    
    @patch('pylascontrol.pylascontrol.pd.read_excel')
    def test_load_budget_excel_structure(self, mock_read_excel, mock_excel_data):
        """Test that load_budget_excel returns correct DataFrame structure"""
        mock_read_excel.return_value = mock_excel_data
        
        df = load_budget_excel("fake_path.xlsx", year=2025)
        
        # Check columns
        expected_columns = ['ano', 'mes', 'tipo', 'grupo', 'categoria', 'valor']
        assert list(df.columns) == expected_columns
    
    @patch('pylascontrol.pylascontrol.pd.read_excel')
    def test_load_budget_excel_filters_labels(self, mock_read_excel, mock_excel_data):
        """Test that ignored labels are filtered out"""
        mock_read_excel.return_value = mock_excel_data
        
        df = load_budget_excel("fake_path.xlsx", year=2025)
        
        # "Total" should be filtered out
        assert "Total" not in df['categoria'].values
    
    @patch('pylascontrol.pylascontrol.pd.read_excel')
    def test_load_budget_excel_year_parameter(self, mock_read_excel, mock_excel_data):
        """Test that year parameter is correctly assigned"""
        mock_read_excel.return_value = mock_excel_data
        
        df = load_budget_excel("fake_path.xlsx", year=2024)
        
        # All records should have year 2024
        assert all(df['ano'] == 2024)
    
    @patch('pylascontrol.pylascontrol.pd.read_excel')
    def test_load_budget_excel_tipo_classification(self, mock_read_excel, mock_excel_data):
        """Test that tipo is correctly classified"""
        mock_read_excel.return_value = mock_excel_data
        
        df = load_budget_excel("fake_path.xlsx", year=2025)
        
        # Salário should be receita
        salario_rows = df[df['categoria'] == 'Salário']
        assert all(salario_rows['tipo'] == 'receita')
        
        # Alimentação should be despesa
        alimentacao_rows = df[df['categoria'] == 'Alimentação']
        assert all(alimentacao_rows['tipo'] == 'despesa')
    
    @patch('pylascontrol.pylascontrol.pd.read_excel')
    def test_load_budget_excel_ignores_zero_values(self, mock_read_excel):
        """Test that zero values are ignored"""
        data = {
            "Unnamed: 0": ["", "RECEITA", "Salário"],
            "JAN": ["JAN", np.nan, 0.0],
            "FEV": ["FEV", np.nan, 5000.0],
        }
        mock_read_excel.return_value = pd.DataFrame(data)
        
        df = load_budget_excel("fake_path.xlsx", year=2025)
        
        # Only FEV should have a record
        assert len(df) == 1
        assert df.iloc[0]['mes'] == 2


class TestPlotChartByType:
    """Test plot_chart_by_type function"""
    
    @pytest.fixture
    def sample_df(self):
        """Create sample DataFrame for plotting"""
        data = {
            'ano': [2025] * 6,
            'mes': [1, 1, 2, 2, 3, 3],
            'tipo': ['receita', 'despesa', 'receita', 'despesa', 'receita', 'despesa'],
            'valor': [5000, 3000, 5200, 3500, 5100, 3200]
        }
        return pd.DataFrame(data)
    
    @patch('pylascontrol.pylascontrol.plt.show')
    def test_plot_line_chart(self, mock_show, sample_df):
        """Test line chart plotting"""
        plot_chart_by_type(sample_df, year=2025, type="line")
        mock_show.assert_called_once()
    
    @patch('pylascontrol.pylascontrol.plt.show')
    def test_plot_bar_chart(self, mock_show, sample_df):
        """Test bar chart plotting"""
        plot_chart_by_type(sample_df, year=2025, type="bar")
        mock_show.assert_called_once()
    
    @patch('pylascontrol.pylascontrol.plt.show')
    def test_plot_saldo_chart(self, mock_show, sample_df):
        """Test saldo chart plotting"""
        plot_chart_by_type(sample_df, year=2025, type="saldo")
        mock_show.assert_called_once()
    
    def test_plot_invalid_type(self, sample_df):
        """Test that invalid chart type raises ValueError"""
        with pytest.raises(ValueError, match="chart_type inválido"):
            plot_chart_by_type(sample_df, year=2025, type="invalid")
    
    @patch('pylascontrol.pylascontrol.plt.show')
    def test_plot_filters_by_year(self, mock_show, sample_df):
        """Test that plotting filters by year correctly"""
        # Add data for different year
        extra_data = pd.DataFrame({
            'ano': [2024, 2024],
            'mes': [1, 1],
            'tipo': ['receita', 'despesa'],
            'valor': [4000, 2500]
        })
        combined_df = pd.concat([sample_df, extra_data], ignore_index=True)
        
        # Should only plot 2025 data
        plot_chart_by_type(combined_df, year=2025, type="line")
        mock_show.assert_called_once()
    
    @patch('pylascontrol.pylascontrol.plt.show')
    def test_plot_handles_missing_receita(self, mock_show):
        """Test that plotting handles missing receita data"""
        df = pd.DataFrame({
            'ano': [2025, 2025],
            'mes': [1, 2],
            'tipo': ['despesa', 'despesa'],
            'valor': [3000, 3500]
        })
        
        plot_chart_by_type(df, year=2025, type="line")
        mock_show.assert_called_once()
    
    @patch('pylascontrol.pylascontrol.plt.show')
    def test_plot_handles_missing_despesa(self, mock_show):
        """Test that plotting handles missing despesa data"""
        df = pd.DataFrame({
            'ano': [2025, 2025],
            'mes': [1, 2],
            'tipo': ['receita', 'receita'],
            'valor': [5000, 5200]
        })
        
        plot_chart_by_type(df, year=2025, type="bar")
        mock_show.assert_called_once()


class TestIntegration:
    """Integration tests"""
    
    @patch('pylascontrol.pylascontrol.pd.read_excel')
    @patch('pylascontrol.pylascontrol.plt.show')
    def test_full_workflow(self, mock_show, mock_read_excel):
        """Test complete workflow from loading to plotting"""
        # Create realistic mock data
        data = {
            "Unnamed: 0": ["", "RECEITA", "Salário", "DESPESAS", "Cotidiano", "Alimentação"],
            "JAN": ["JAN", np.nan, 5000.0, np.nan, np.nan, 800.0],
            "FEV": ["FEV", np.nan, 5200.0, np.nan, np.nan, 850.0],
        }
        mock_read_excel.return_value = pd.DataFrame(data)
        
        # Load data
        df = load_budget_excel("fake_path.xlsx", year=2025)
        
        # Verify data loaded correctly
        assert len(df) > 0
        assert 'ano' in df.columns
        
        # Plot each chart type
        for chart_type in ["line", "bar", "saldo"]:
            plot_chart_by_type(df, year=2025, type=chart_type)
        
        # Should have called plt.show() three times
        assert mock_show.call_count == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
