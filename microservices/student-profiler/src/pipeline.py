from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


@dataclass(slots=True)
class ProfilingArtifacts:
    pipeline: Pipeline
    pca: PCA
    kmeans: KMeans


@dataclass(slots=True)
class ProfilingConfig:
    features: dict
    pca: dict
    kmeans: dict


class StudentProfilerPipeline:
    def __init__(self, config: ProfilingConfig) -> None:
        self.config = config
        self.numeric_cols = config.features["include"]
        self.categorical_cols = config.features.get("categorical", [])
        self.pipeline = self._build_preprocessing_pipeline()
        self.pca = PCA(**config.pca)
        self.kmeans = KMeans(**config.kmeans)

    def _build_preprocessing_pipeline(self) -> ColumnTransformer:
        numeric_pipeline = Pipeline(
            steps=[
                (
                    "imputer",
                    SimpleImputer(strategy=self.config.features.get("imputation_strategy", "median")),
                ),
                ("scaler", StandardScaler()),
            ]
        )
        categorical_pipeline = Pipeline(
            steps=[
                (
                    "imputer",
                    SimpleImputer(strategy=self.config.features.get("categorical_imputation", "most_frequent")),
                ),
                ("encoder", OneHotEncoder(handle_unknown="ignore")),
            ]
        )
        return ColumnTransformer(
            transformers=[
                ("num", numeric_pipeline, self.numeric_cols),
                ("cat", categorical_pipeline, self.categorical_cols),
            ]
        )

    def fit(self, df: pd.DataFrame) -> ProfilingArtifacts:
        all_cols = self.numeric_cols + self.categorical_cols
        features = df[all_cols]
        transformed = self.pipeline.fit_transform(features)
        reduced = self.pca.fit_transform(transformed)
        self.kmeans.fit(reduced)
        return ProfilingArtifacts(self.pipeline, self.pca, self.kmeans)

    def assign_clusters(self, df: pd.DataFrame) -> np.ndarray:
        all_cols = self.numeric_cols + self.categorical_cols
        transformed = self.pipeline.transform(df[all_cols])
        reduced = self.pca.transform(transformed)
        return self.kmeans.predict(reduced)

    def save(self, path: str) -> None:
        joblib.dump({
            "pipeline": self.pipeline,
            "pca": self.pca,
            "kmeans": self.kmeans,
        }, path)

    @classmethod
    def load(cls, path: str) -> ProfilingArtifacts:
        data = joblib.load(path)
        return ProfilingArtifacts(**data)
