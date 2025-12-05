# src/transformers/normalizer.py
import pandas as pd
import numpy as np
import json
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Normalizer:
    """Normalizes data using mapping configuration"""

    def __init__(self, mapping_path: str = "/opt/prepadata/config/mapping.json"):
        self.mapping_path = mapping_path
        self.mapping = self.load_mapping()

    def load_mapping(self) -> Dict[str, Any]:
        """Load mapping configuration from JSON file"""
        try:
            with open(self.mapping_path, 'r', encoding='utf-8') as f:
                mapping = json.load(f)
            logger.info("Loaded mapping.json (%s features)", len(mapping))
            return mapping
        except FileNotFoundError:
            logger.warning(f"Mapping file not found: {self.mapping_path}")
            return {}
        except Exception as e:
            logger.error(f"Failed to load mapping: {e}")
            return {}

    def normalize(self, source_df: pd.DataFrame, source_type: str = 'oulad') -> pd.DataFrame:
        """
        Apply mapping to normalize data from source format to unified schema

        Args:
            source_df: Source DataFrame (OULAD or Moodle format)
            source_type: 'oulad' or 'moodle'

        Returns:
            Normalized DataFrame with unified schema
        """
        if source_df.empty:
            logger.warning("Empty DataFrame provided for normalization")
            return pd.DataFrame()

        if not self.mapping:
            logger.warning("No mapping available, returning original DataFrame")
            return source_df

        return self.apply_mapping_to_rowwise(source_df, self.mapping, source_type)

    def apply_mapping_to_rowwise(self, source_df: pd.DataFrame,
                                 mapping: Dict[str, Any],
                                 source_type: str) -> pd.DataFrame:
        """
        Simple mapping engine: for direct column mapping, copy column.
        For aggregate/filter types mapping, these typically are handled in aggregator.
        This function handles rowwise transforms (demographics, credits, etc).
        """
        out = pd.DataFrame(index=source_df.index)

        for feature, rules in mapping.items():
            rule = rules.get(source_type)
            transform = rules.get('transform')

            if isinstance(rule, str):
                if rule in source_df.columns:
                    out[feature] = source_df[rule]
                else:
                    out[feature] = np.nan
            else:
                # not rowwise
                out[feature] = np.nan

            # apply small transforms inline
            if transform == "to_int":
                out[feature] = pd.to_numeric(out[feature], errors='coerce').fillna(0).astype(int)
            elif transform == "map_age_band_or_compute":
                out[feature] = out[feature].fillna('Unknown')

        logger.info("apply_mapping_to_rowwise produced %s columns", out.shape[1])
        return out


# Legacy functions for backward compatibility
def load_mapping(path: str) -> Dict[str, Any]:
    """Legacy function - use Normalizer class instead"""
    with open(path, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    logger.info("Loaded mapping.json (%s features)", len(mapping))
    return mapping


def apply_mapping_to_rowwise(source_df: pd.DataFrame,
                             mapping: Dict[str, Any],
                             source_type: str) -> pd.DataFrame:
    """Legacy function - use Normalizer class instead"""
    out = pd.DataFrame(index=source_df.index)
    for feature, rules in mapping.items():
        rule = rules.get(source_type)
        transform = rules.get('transform')
        if isinstance(rule, str):
            if rule in source_df.columns:
                out[feature] = source_df[rule]
            else:
                out[feature] = np.nan
        else:
            out[feature] = np.nan

        if transform == "to_int":
            out[feature] = pd.to_numeric(out[feature], errors='coerce').fillna(0).astype(int)
        elif transform == "map_age_band_or_compute":
            out[feature] = out[feature].fillna('Unknown')

    logger.info("apply_mapping_to_rowwise produced %s columns", out.shape[1])
    return out