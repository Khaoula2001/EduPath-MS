# src/transformers/data_cleaner.py
"""
Data Cleaner Module - Enhanced
===============================
Comprehensive data cleaning pipeline with quality checks
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DataCleaner:
    """Cleans and validates data with comprehensive quality checks"""

    def __init__(self):
        self.cleaning_report = {}

    def clean_student_info(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Clean student_info table:
        - Remove duplicates
        - Handle missing values
        - Standardize categorical values
        - Validate data types
        """
        logger.info(f"🧹 Cleaning student_info: {len(df)} rows")

        original_count = len(df)
        report = {'original_rows': original_count}

        # 1. Standardize column names
        df = df.copy()
        df.columns = [c.strip().lower() for c in df.columns]

        # 2. Remove exact duplicates
        df_before_dedup = len(df)
        df = df.drop_duplicates()
        report['duplicates_removed'] = df_before_dedup - len(df)

        # 3. Remove duplicates based on key columns
        key_cols = ['id_student', 'code_module', 'code_presentation']
        if all(c in df.columns for c in key_cols):
            df = df.drop_duplicates(subset=key_cols, keep='first')

        # 4. Convert data types
        if 'id_student' in df.columns:
            df['id_student'] = pd.to_numeric(df['id_student'], errors='coerce').astype('Int64')

        if 'num_of_prev_attempts' in df.columns:
            df['num_of_prev_attempts'] = pd.to_numeric(df['num_of_prev_attempts'], errors='coerce').fillna(0).astype(int)

        if 'studied_credits' in df.columns:
            df['studied_credits'] = pd.to_numeric(df['studied_credits'], errors='coerce').fillna(0).astype(int)

        # 5. Handle categorical missing values
        categorical_cols = ['gender', 'region', 'highest_education', 'imd_band',
                            'age_band', 'disability', 'final_result']

        report['missing_before'] = {}
        report['missing_after'] = {}

        for col in categorical_cols:
            if col in df.columns:
                report['missing_before'][col] = int(df[col].isna().sum())
                df[col] = df[col].fillna('Unknown')
                report['missing_after'][col] = int(df[col].isna().sum())

        # 6. Standardize categorical values
        if 'gender' in df.columns:
            df['gender'] = df['gender'].str.strip().str.capitalize()

        if 'disability' in df.columns:
            df['disability'] = df['disability'].replace({'Y': 'Yes', 'N': 'No'})

        # 7. Remove rows with critical missing values
        critical_cols = ['id_student', 'code_module', 'code_presentation']
        before_drop = len(df)
        df = df.dropna(subset=[c for c in critical_cols if c in df.columns])
        report['critical_missing_removed'] = before_drop - len(df)

        report['final_rows'] = len(df)
        report['cleaning_rate'] = (original_count - len(df)) / original_count if original_count > 0 else 0

        logger.info(f"✅ Cleaned student_info: {len(df)} rows remaining "
                    f"(removed {original_count - len(df)})")

        return df, report

    def clean_student_vle(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Clean student_vle table"""
        logger.info(f"🧹 Cleaning student_vle: {len(df)} rows")

        original_count = len(df)
        report = {'original_rows': original_count}

        df = df.copy()
        df.columns = [c.strip().lower() for c in df.columns]

        # Remove duplicates
        key_cols = ['id_student', 'id_site', 'date']
        if all(c in df.columns for c in key_cols):
            before = len(df)
            df = df.drop_duplicates(subset=key_cols, keep='first')
            report['duplicates_removed'] = before - len(df)

        # Convert types
        if 'id_student' in df.columns:
            df['id_student'] = pd.to_numeric(df['id_student'], errors='coerce').astype('Int64')

        if 'sum_click' in df.columns:
            df['sum_click'] = pd.to_numeric(df['sum_click'], errors='coerce').fillna(0).astype(int)
            # Remove negative clicks
            before = len(df)
            df = df[df['sum_click'] >= 0]
            report['negative_clicks_removed'] = before - len(df)

        if 'date' in df.columns:
            df['date'] = pd.to_numeric(df['date'], errors='coerce').fillna(-1).astype(int)

        # Remove outliers (clicks > 99th percentile)
        if 'sum_click' in df.columns:
            threshold = df['sum_click'].quantile(0.99)
            before = len(df)
            df = df[df['sum_click'] <= threshold]
            report['outliers_removed'] = before - len(df)
            report['outlier_threshold'] = float(threshold)

        report['final_rows'] = len(df)

        logger.info(f"✅ Cleaned student_vle: {len(df)} rows remaining")

        return df, report

    def clean_student_assessment(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Clean student_assessment table"""
        logger.info(f"🧹 Cleaning student_assessment: {len(df)} rows")

        original_count = len(df)
        report = {'original_rows': original_count}

        df = df.copy()
        df.columns = [c.strip().lower() for c in df.columns]

        # Remove duplicates
        key_cols = ['id_assessment', 'id_student']
        if all(c in df.columns for c in key_cols):
            before = len(df)
            df = df.drop_duplicates(subset=key_cols, keep='last')  # Keep latest submission
            report['duplicates_removed'] = before - len(df)

        # Convert types
        if 'id_student' in df.columns:
            df['id_student'] = pd.to_numeric(df['id_student'], errors='coerce').astype('Int64')

        if 'score' in df.columns:
            df['score'] = pd.to_numeric(df['score'], errors='coerce')
            # Valid score range: 0-100
            before = len(df)
            df = df[(df['score'] >= 0) & (df['score'] <= 100)]
            report['invalid_scores_removed'] = before - len(df)

        if 'date_submitted' in df.columns:
            df['date_submitted'] = pd.to_numeric(df['date_submitted'], errors='coerce')

        if 'is_banked' in df.columns:
            df['is_banked'] = pd.to_numeric(df['is_banked'], errors='coerce').fillna(0).astype(int)

        report['final_rows'] = len(df)

        logger.info(f"✅ Cleaned student_assessment: {len(df)} rows remaining")

        return df, report

    def clean_assessments(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Clean assessments table"""
        logger.info(f"🧹 Cleaning assessments: {len(df)} rows")

        df = df.copy()
        df.columns = [c.strip().lower() for c in df.columns]

        # Remove duplicates
        if 'id_assessment' in df.columns:
            before = len(df)
            df = df.drop_duplicates(subset=['id_assessment'], keep='first')
            removed = before - len(df)

        # Convert types
        if 'date' in df.columns:
            df['date'] = pd.to_numeric(df['date'], errors='coerce')

        if 'weight' in df.columns:
            df['weight'] = pd.to_numeric(df['weight'], errors='coerce').fillna(0.0)

        logger.info(f"✅ Cleaned assessments: {len(df)} rows")

        return df, {'original_rows': len(df) + removed if 'removed' in locals() else len(df),
                    'final_rows': len(df)}

    def clean_all(self, raw_data: Dict[str, pd.DataFrame]) -> Tuple[Dict[str, pd.DataFrame], Dict]:
        """
        Clean all tables and generate comprehensive report
        """
        logger.info("=" * 60)
        logger.info("🚀 Starting Data Cleaning Pipeline")
        logger.info("=" * 60)

        cleaned_data = {}
        cleaning_reports = {}

        # Clean student_info
        if 'student_info' in raw_data and not raw_data['student_info'].empty:
            cleaned_data['student_info'], cleaning_reports['student_info'] = \
                self.clean_student_info(raw_data['student_info'])

        # Clean student_vle
        if 'student_vle' in raw_data and not raw_data['student_vle'].empty:
            cleaned_data['student_vle'], cleaning_reports['student_vle'] = \
                self.clean_student_vle(raw_data['student_vle'])

        # Clean student_assessment
        if 'student_assessment' in raw_data and not raw_data['student_assessment'].empty:
            cleaned_data['student_assessment'], cleaning_reports['student_assessment'] = \
                self.clean_student_assessment(raw_data['student_assessment'])

        # Clean assessments
        if 'assessments' in raw_data and not raw_data['assessments'].empty:
            cleaned_data['assessments'], cleaning_reports['assessments'] = \
                self.clean_assessments(raw_data['assessments'])

        # Copy other tables as-is
        for key in ['student_registration', 'vle', 'courses']:
            if key in raw_data and not raw_data[key].empty:
                cleaned_data[key] = raw_data[key].copy()
                cleaned_data[key].columns = [c.strip().lower() for c in cleaned_data[key].columns]

        # Generate summary
        summary = self.generate_cleaning_summary(cleaning_reports)

        logger.info("=" * 60)
        logger.info("✅ Data Cleaning Pipeline Complete")
        logger.info("=" * 60)

        return cleaned_data, {'tables': cleaning_reports, 'summary': summary}

    def generate_cleaning_summary(self, reports: Dict[str, Dict]) -> Dict:
        """Generate summary statistics from cleaning reports"""
        total_original = sum(r.get('original_rows', 0) for r in reports.values())
        total_final = sum(r.get('final_rows', 0) for r in reports.values())
        total_removed = total_original - total_final

        summary = {
            'total_original_rows': total_original,
            'total_final_rows': total_final,
            'total_removed_rows': total_removed,
            'overall_cleaning_rate': total_removed / total_original if total_original > 0 else 0,
            'tables_cleaned': len(reports)
        }

        logger.info(f"\n📊 Cleaning Summary:")
        logger.info(f"  Original rows: {total_original:,}")
        logger.info(f"  Final rows: {total_final:,}")
        logger.info(f"  Removed: {total_removed:,} ({summary['overall_cleaning_rate']:.2%})")

        return summary