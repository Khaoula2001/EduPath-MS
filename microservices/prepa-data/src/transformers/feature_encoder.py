# src/transformers/feature_encoder.py
"""
Feature Encoder Module
=====================
Handles encoding of categorical features and target variables
"""

import pandas as pd
import numpy as np
import json
import logging
from typing import Dict, Any, List, Tuple
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class FeatureEncoder:
    """Encodes features using various encoding strategies"""

    def __init__(self, config_path: str = "/opt/prepadata/config/preprocessing_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.encoding_mappings = {}
        self.scaling_params = {}

    def _load_config(self) -> Dict[str, Any]:
        """Load encoding configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            return config.get('preprocessing_config', {})
        except Exception as e:
            logger.warning(f"Could not load config: {e}")
            return {}

    def encode_target(self, df: pd.DataFrame, target_col: str = 'final_result') -> Tuple[pd.DataFrame, Dict[str, int]]:
        """
        Encode the target variable

        Args:
            df: DataFrame with target column
            target_col: Name of target column

        Returns:
            Tuple of (encoded DataFrame, mapping dictionary)
        """
        if target_col not in df.columns:
            logger.warning(f"Target column '{target_col}' not found in DataFrame")
            return df, {}

        # Use mapping from config or default mapping
        target_mapping = self.config.get('encoding', {}).get('target_mapping', {
            'Pass': 0,
            'Fail': 1,
            'Withdrawn': 2,
            'Distinction': 3
        })

        # Create encoded column
        encoded_col = f"{target_col}_encoded"
        df[encoded_col] = df[target_col].map(target_mapping)

        # Fill unknown values with -1
        unknown_mask = df[encoded_col].isna()
        if unknown_mask.any():
            df.loc[unknown_mask, encoded_col] = -1
            logger.info(f"Filled {unknown_mask.sum()} unknown target values with -1")

        # Convert to integer
        df[encoded_col] = df[encoded_col].astype(int)

        # Log distribution
        distribution = df[encoded_col].value_counts().sort_index()
        logger.info(f"Target distribution: {dict(distribution)}")

        # Save mapping
        self.encoding_mappings[target_col] = target_mapping

        return df, target_mapping

    def encode_categorical_features(self, df: pd.DataFrame,
                                    categorical_cols: List[str] = None,
                                    method: str = 'label') -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Encode categorical features

        Args:
            df: DataFrame with categorical columns
            categorical_cols: List of categorical column names
            method: Encoding method ('label', 'onehot', 'ordinal')

        Returns:
            Tuple of (encoded DataFrame, encoding information)
        """
        if df.empty:
            return df, {}

        # Use columns from config if not specified
        if categorical_cols is None:
            categorical_cols = self.config.get('encoding', {}).get('categorical_features', [])

        # Filter columns that exist in DataFrame
        categorical_cols = [col for col in categorical_cols if col in df.columns]

        if not categorical_cols:
            logger.warning("No categorical columns found to encode")
            return df, {}

        logger.info(f"Encoding {len(categorical_cols)} categorical columns: {categorical_cols}")

        df_encoded = df.copy()
        encoding_info = {
            'method': method,
            'columns_encoded': [],
            'mappings': {}
        }

        for col in categorical_cols:
            if method == 'label':
                encoded_df, mapping = self._label_encode(df_encoded, col)
                df_encoded = encoded_df
                encoding_info['mappings'][col] = mapping
                encoding_info['columns_encoded'].append(f"{col}_encoded")

            elif method == 'onehot':
                encoded_df = self._onehot_encode(df_encoded, col)
                df_encoded = encoded_df
                # Get the new column names
                new_cols = [c for c in encoded_df.columns if c.startswith(f"{col}_")]
                encoding_info['columns_encoded'].extend(new_cols)

            elif method == 'ordinal':
                encoded_df, mapping = self._ordinal_encode(df_encoded, col)
                df_encoded = encoded_df
                encoding_info['mappings'][col] = mapping
                encoding_info['columns_encoded'].append(f"{col}_encoded")

        logger.info(f"Created {len(encoding_info['columns_encoded'])} encoded features")

        return df_encoded, encoding_info

    def _label_encode(self, df: pd.DataFrame, col: str) -> Tuple[pd.DataFrame, Dict[str, int]]:
        """Label encode a categorical column"""
        encoder = LabelEncoder()

        # Fill NA with 'Unknown' before encoding
        df_filled = df[col].fillna('Unknown')

        # Fit and transform
        encoded_values = encoder.fit_transform(df_filled)

        # Add encoded column
        df[f"{col}_encoded"] = encoded_values

        # Create mapping dictionary
        mapping = dict(zip(encoder.classes_, encoder.transform(encoder.classes_)))

        logger.debug(f"Label encoded '{col}': {len(mapping)} categories")

        return df, mapping

    def _onehot_encode(self, df: pd.DataFrame, col: str) -> pd.DataFrame:
        """One-hot encode a categorical column"""
        # Fill NA with 'Unknown'
        df_filled = df[col].fillna('Unknown')

        # Create dummies
        dummies = pd.get_dummies(df_filled, prefix=col, dtype=int)

        # Drop original column and add dummies
        df = df.drop(columns=[col])
        df = pd.concat([df, dummies], axis=1)

        logger.debug(f"One-hot encoded '{col}': created {len(dummies.columns)} columns")

        return df

    def _ordinal_encode(self, df: pd.DataFrame, col: str) -> Tuple[pd.DataFrame, Dict[str, int]]:
        """
        Ordinal encode with custom ordering for known categories
        """
        # Define order for specific columns
        order_mappings = {
            'age_band': ['0-35', '35-55', '55+'],
            'highest_education': ['No Formal quals', 'Lower Than A Level',
                                  'A Level or Equivalent', 'HE Qualification',
                                  'Post Graduate Qualification'],
            'imd_band': ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%',
                         '50-60%', '60-70%', '70-80%', '80-90%', '90-100%']
        }

        if col in order_mappings:
            categories = order_mappings[col]
            mapping = {cat: idx for idx, cat in enumerate(categories)}

            # Fill NA with median category
            df_filled = df[col].fillna(categories[len(categories)//2])

            # Map values
            df[f"{col}_encoded"] = df_filled.map(mapping)

            # Fill any remaining NaN (for unknown categories)
            df[f"{col}_encoded"] = df[f"{col}_encoded"].fillna(-1).astype(int)

            logger.debug(f"Ordinal encoded '{col}': {len(categories)} ordered categories")

        else:
            # Fallback to label encoding
            return self._label_encode(df, col)

        return df, mapping

    def normalize_features(self, df: pd.DataFrame,
                           numeric_cols: List[str] = None,
                           method: str = 'minmax') -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Normalize numeric features

        Args:
            df: DataFrame with numeric columns
            numeric_cols: List of numeric column names
            method: Normalization method ('minmax', 'standard', 'robust')

        Returns:
            Tuple of (normalized DataFrame, scaling parameters)
        """
        if df.empty:
            return df, {}

        # Use columns from config if not specified
        if numeric_cols is None:
            numeric_cols = self.config.get('normalization', {}).get('numeric_features_to_normalize', [])

        # Filter columns that exist and are numeric
        numeric_cols = [col for col in numeric_cols
                        if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]

        if not numeric_cols:
            logger.warning("No numeric columns found to normalize")
            return df, {}

        logger.info(f"Normalizing {len(numeric_cols)} numeric columns: {numeric_cols}")

        df_normalized = df.copy()
        scaling_info = {
            'method': method,
            'columns_normalized': [],
            'parameters': {}
        }

        for col in numeric_cols:
            if method == 'minmax':
                scaler = MinMaxScaler()
                suffix = '_normalized'
            elif method == 'standard':
                scaler = StandardScaler()
                suffix = '_standardized'
            elif method == 'robust':
                from sklearn.preprocessing import RobustScaler
                scaler = RobustScaler()
                suffix = '_robust'
            else:
                logger.warning(f"Unknown method '{method}', using MinMax")
                scaler = MinMaxScaler()
                suffix = '_normalized'

            # Reshape for scaler
            col_data = df[[col]].values

            # Fit and transform
            scaled_data = scaler.fit_transform(col_data)

            # Add scaled column
            df_normalized[f"{col}{suffix}"] = scaled_data

            # Save scaler parameters
            if hasattr(scaler, 'scale_'):
                scaling_info['parameters'][col] = {
                    'mean': float(scaler.mean_[0]) if hasattr(scaler, 'mean_') else None,
                    'scale': float(scaler.scale_[0]) if hasattr(scaler, 'scale_') else None,
                    'min': float(scaler.data_min_[0]) if hasattr(scaler, 'data_min_') else None,
                    'max': float(scaler.data_max_[0]) if hasattr(scaler, 'data_max_') else None
                }

            scaling_info['columns_normalized'].append(f"{col}{suffix}")

        logger.info(f"Created {len(scaling_info['columns_normalized'])} normalized features")

        # Save scaling parameters
        self.scaling_params = scaling_info['parameters']

        return df_normalized, scaling_info

    def separate_features_target(self, df: pd.DataFrame,
                                 target_col: str = 'final_result_encoded',
                                 exclude_cols: List[str] = None) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Separate features and target

        Args:
            df: DataFrame with features and target
            target_col: Name of target column
            exclude_cols: Columns to exclude from features

        Returns:
            Tuple of (features DataFrame, target Series)
        """
        if df.empty:
            return pd.DataFrame(), pd.Series()

        # Default columns to exclude
        if exclude_cols is None:
            exclude_cols = ['id_student', 'code_module', 'code_presentation', 'final_result']

        # Get feature columns
        feature_cols = [col for col in df.columns
                        if col not in exclude_cols + [target_col]]

        # Features
        X = df[feature_cols].copy()

        # Target
        if target_col in df.columns:
            y = df[target_col].copy()
        else:
            y = pd.Series(dtype=int)

        logger.info(f"Separated {X.shape[1]} features and {len(y)} target samples")

        return X, y

    def save_encoding_config(self, output_path: str = "/opt/prepadata/config/encoding_config.json"):
        """Save encoding configuration and mappings"""
        config_to_save = {
            'encoding_mappings': self.encoding_mappings,
            'scaling_parameters': self.scaling_params,
            'saved_at': pd.Timestamp.now().isoformat()
        }

        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(config_to_save, f, indent=2, default=str)

        logger.info(f"Encoding configuration saved to {output_path}")

        return config_to_save

    def load_encoding_config(self, config_path: str = "/opt/prepadata/config/encoding_config.json"):
        """Load previously saved encoding configuration"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)

            self.encoding_mappings = config.get('encoding_mappings', {})
            self.scaling_params = config.get('scaling_parameters', {})

            logger.info(f"Loaded encoding configuration from {config_path}")

            return config
        except Exception as e:
            logger.warning(f"Could not load encoding config: {e}")
            return {}