# src/transformers/data_validator.py
"""
Data Validator Module
=====================
Comprehensive data quality validation and checks
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Tuple
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DataValidator:
    """Validates data quality with comprehensive checks"""

    def __init__(self, config_path: str = "/opt/prepadata/config/preprocessing_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.validation_results = {}

    def _load_config(self) -> Dict[str, Any]:
        """Load validation configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            return config.get('preprocessing_config', {})
        except Exception as e:
            logger.warning(f"Could not load config: {e}")
            return {}

    def validate_dataset(self, df: pd.DataFrame, table_name: str,
                         key_columns: List[str] = None) -> Dict[str, Any]:
        """
        Perform comprehensive validation on a dataset

        Args:
            df: DataFrame to validate
            table_name: Name of the table
            key_columns: Primary key columns for uniqueness check

        Returns:
            Dictionary with validation results
        """
        if df.empty:
            return {
                'status': 'EMPTY',
                'issues': ['Dataset is empty'],
                'checks_passed': 0,
                'checks_failed': 0
            }

        results = {
            'table_name': table_name,
            'row_count': len(df),
            'column_count': len(df.columns),
            'checks_passed': 0,
            'checks_failed': 0,
            'issues': [],
            'warnings': [],
            'details': {}
        }

        # 1. Check for duplicates
        duplicate_report = self.check_duplicates(df, key_columns)
        results['details']['duplicates'] = duplicate_report

        if duplicate_report['duplicate_count'] > 0:
            results['issues'].append(f"Found {duplicate_report['duplicate_count']} duplicate rows")
            results['checks_failed'] += 1
        else:
            results['checks_passed'] += 1

        # 2. Check missing values
        missing_report = self.check_missing_values(df)
        results['details']['missing_values'] = missing_report

        if missing_report['total_missing'] > 0:
            results['warnings'].append(f"Found {missing_report['total_missing']} missing values")
            # This is a warning, not an issue
            results['checks_passed'] += 1
        else:
            results['checks_passed'] += 1

        # 3. Check data types
        type_report = self.check_data_types(df, table_name)
        results['details']['data_types'] = type_report

        if type_report['type_mismatches'] > 0:
            results['issues'].append(f"Found {type_report['type_mismatches']} data type mismatches")
            results['checks_failed'] += 1
        else:
            results['checks_passed'] += 1

        # 4. Check value ranges
        range_report = self.check_value_ranges(df, table_name)
        results['details']['value_ranges'] = range_report

        if range_report['out_of_range'] > 0:
            results['issues'].append(f"Found {range_report['out_of_range']} out-of-range values")
            results['checks_failed'] += 1
        else:
            results['checks_passed'] += 1

        # 5. Check referential integrity (for related tables)
        if key_columns and 'id_' in ' '.join(df.columns):
            ref_report = self.check_referential_integrity(df, table_name)
            results['details']['referential_integrity'] = ref_report

            if ref_report['integrity_violations'] > 0:
                results['issues'].append(f"Found {ref_report['integrity_violations']} referential integrity violations")
                results['checks_failed'] += 1
            else:
                results['checks_passed'] += 1

        # 6. Check for outliers
        outlier_report = self.check_outliers(df, table_name)
        results['details']['outliers'] = outlier_report

        if outlier_report['outlier_count'] > 0:
            results['warnings'].append(f"Found {outlier_report['outlier_count']} potential outliers")
            results['checks_passed'] += 1  # Warnings don't fail the check

        # Overall status
        if len(results['issues']) == 0:
            results['status'] = 'PASS'
        elif len(results['issues']) <= 2:
            results['status'] = 'WARNING'
        else:
            results['status'] = 'FAIL'

        self.validation_results[table_name] = results
        return results

    def check_duplicates(self, df: pd.DataFrame, key_columns: List[str] = None) -> Dict[str, Any]:
        """Check for duplicate rows"""
        report = {
            'duplicate_count': 0,
            'duplicate_percentage': 0.0,
            'key_columns_used': key_columns
        }

        if df.empty:
            return report

        if key_columns and all(col in df.columns for col in key_columns):
            # Check duplicates on key columns
            duplicate_mask = df.duplicated(subset=key_columns, keep=False)
        else:
            # Check all columns
            duplicate_mask = df.duplicated(keep=False)

        report['duplicate_count'] = int(duplicate_mask.sum())
        report['duplicate_percentage'] = (report['duplicate_count'] / len(df)) * 100

        if report['duplicate_count'] > 0:
            report['duplicate_examples'] = df[duplicate_mask].head(5).to_dict('records')

        return report

    def check_missing_values(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check for missing values"""
        report = {
            'total_missing': 0,
            'missing_by_column': {},
            'columns_with_missing': []
        }

        if df.empty:
            return report

        for column in df.columns:
            missing_count = df[column].isna().sum()
            if missing_count > 0:
                report['missing_by_column'][column] = {
                    'count': int(missing_count),
                    'percentage': (missing_count / len(df)) * 100
                }
                report['columns_with_missing'].append(column)

        report['total_missing'] = int(df.isna().sum().sum())
        report['missing_percentage'] = (report['total_missing'] / (len(df) * len(df.columns))) * 100

        return report

    def check_data_types(self, df: pd.DataFrame, table_name: str) -> Dict[str, Any]:
        """Check if data types match expected schema"""
        report = {
            'type_mismatches': 0,
            'mismatches': []
        }

        if df.empty or 'data_types' not in self.config:
            return report

        expected_types = self.config.get('data_types', {}).get(table_name, {})

        for column, expected_type in expected_types.items():
            if column in df.columns:
                actual_type = str(df[column].dtype)
                expected_type_str = str(expected_type)

                # Simple type matching (can be enhanced)
                if not self._type_matches(actual_type, expected_type_str):
                    report['type_mismatches'] += 1
                    report['mismatches'].append({
                        'column': column,
                        'expected': expected_type_str,
                        'actual': actual_type
                    })

        return report

    def _type_matches(self, actual: str, expected: str) -> bool:
        """Check if actual dtype matches expected"""
        type_mapping = {
            'int64': ['int64', 'Int64', 'int32', 'Int32', 'int'],
            'float64': ['float64', 'Float64', 'float32', 'float'],
            'object': ['object', 'string', 'str'],
            'category': ['category']
        }

        for base_type, aliases in type_mapping.items():
            if expected == base_type and actual in aliases:
                return True

        return actual == expected

    def check_value_ranges(self, df: pd.DataFrame, table_name: str) -> Dict[str, Any]:
        """Check if values are within expected ranges"""
        report = {
            'out_of_range': 0,
            'range_violations': []
        }

        if df.empty:
            return report

        # Check for specific columns based on table
        if table_name == 'student_assessment' and 'score' in df.columns:
            # Score should be between 0-100
            invalid_scores = df[(df['score'] < 0) | (df['score'] > 100)]
            if len(invalid_scores) > 0:
                report['out_of_range'] += len(invalid_scores)
                report['range_violations'].append({
                    'column': 'score',
                    'expected_range': '0-100',
                    'invalid_count': len(invalid_scores),
                    'invalid_values': invalid_scores['score'].unique().tolist()[:5]
                })

        if 'sum_click' in df.columns:
            # Clicks should be non-negative
            negative_clicks = df[df['sum_click'] < 0]
            if len(negative_clicks) > 0:
                report['out_of_range'] += len(negative_clicks)
                report['range_violations'].append({
                    'column': 'sum_click',
                    'expected_range': '>= 0',
                    'invalid_count': len(negative_clicks)
                })

        return report

    def check_referential_integrity(self, df: pd.DataFrame, table_name: str) -> Dict[str, Any]:
        """Check referential integrity for foreign keys"""
        report = {
            'integrity_violations': 0,
            'violations': []
        }

        # This would require checking against reference tables
        # For now, return empty report
        return report

    def check_outliers(self, df: pd.DataFrame, table_name: str) -> Dict[str, Any]:
        """Check for statistical outliers"""
        report = {
            'outlier_count': 0,
            'outliers_by_column': {}
        }

        if df.empty:
            return report

        # Check numeric columns for outliers using IQR method
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        for column in numeric_cols:
            if column in ['id_student', 'id_assessment', 'id_site']:
                continue  # Skip ID columns

            col_data = df[column].dropna()
            if len(col_data) < 10:
                continue

            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
            outlier_count = len(outliers)

            if outlier_count > 0:
                report['outlier_count'] += outlier_count
                report['outliers_by_column'][column] = {
                    'count': outlier_count,
                    'percentage': (outlier_count / len(df)) * 100,
                    'lower_bound': float(lower_bound),
                    'upper_bound': float(upper_bound)
                }

        return report

    def get_validation_summary(self, validation_reports: Dict[str, Dict]) -> pd.DataFrame:
        """Create summary DataFrame from validation reports"""
        summary_data = []

        for table_name, report in validation_reports.items():
            summary_data.append({
                'Table': table_name,
                'Rows': report.get('row_count', 0),
                'Columns': report.get('column_count', 0),
                'Status': report.get('status', 'UNKNOWN'),
                'Checks Passed': report.get('checks_passed', 0),
                'Checks Failed': report.get('checks_failed', 0),
                'Issues': len(report.get('issues', [])),
                'Warnings': len(report.get('warnings', []))
            })

        return pd.DataFrame(summary_data)

    def save_validation_report(self, output_path: str = "/opt/prepadata/reports/validation_report.json"):
        """Save validation results to JSON file"""
        import json
        import os

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(self.validation_results, f, indent=2, default=str)

        logger.info(f"Validation report saved to {output_path}")