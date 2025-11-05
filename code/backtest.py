#!/usr/bin/env python3
"""
Backtest: CM/SM/ENS train/test with rolling origin.

- CM: Component Model (HOLD ~ W + A + I + SSR)
- SM: Signal Model (HOLD ~ f(t))
- ENS: Ensemble (average of CM and SM)
"""

import numpy as np
import pandas as pd
from typing import Tuple, List, Dict
from sklearn.metrics import roc_auc_score, brier_score_loss


def load_labels(df: pd.DataFrame, delta_days: int = 90, threshold: float = 0.05) -> pd.Series:
    """
    Generate HOLD labels: Δ=90d, x=5% net outflow threshold.
    
    Args:
        df: DataFrame with wallet/transaction data
        delta_days: Time horizon in days
        threshold: Net outflow threshold (e.g., 0.05 = 5%)
    
    Returns:
        Series of binary labels (1=HOLD, 0=not HOLD)
    """
    pass


def train_cm(X_train: pd.DataFrame, y_train: pd.Series):
    """
    Train Component Model: HOLD ~ W + A + I + SSR.
    
    Args:
        X_train: Features DataFrame with columns [W, A, I, SSR]
        y_train: Binary labels
    
    Returns:
        Trained model
    """
    pass


def train_sm(X_train: pd.DataFrame, y_train: pd.Series):
    """
    Train Signal Model: HOLD ~ f(t).
    
    Args:
        X_train: Features DataFrame with column [f]
        y_train: Binary labels
    
    Returns:
        Trained model
    """
    pass


def train_ensemble(cm_model, sm_model):
    """
    Create ensemble model (average of CM and SM predictions).
    
    Args:
        cm_model: Trained Component Model
        sm_model: Trained Signal Model
    
    Returns:
        Ensemble model object
    """
    pass


def rolling_origin_cv(df: pd.DataFrame, n_splits: int = 5) -> List[Tuple]:
    """
    Generate rolling origin cross-validation splits.
    
    Args:
        df: Full dataset
        n_splits: Number of CV splits
    
    Returns:
        List of (train_idx, test_idx) tuples
    """
    pass


def evaluate_model(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Compute evaluation metrics: AUC, Brier score.
    
    Args:
        y_true: True binary labels
        y_pred: Predicted probabilities
    
    Returns:
        Dictionary with metrics: {'auc': ..., 'brier': ...}
    """
    pass


def compare_models(cm_metrics: Dict, sm_metrics: Dict) -> Dict[str, float]:
    """
    Compare CM vs SM using Diebold–Mariano and AICc.
    
    Args:
        cm_metrics: Component Model metrics
        sm_metrics: Signal Model metrics
    
    Returns:
        Dictionary with comparison statistics
    """
    pass


def backtest_rolling_origin(df: pd.DataFrame, n_splits: int = 5) -> Dict:
    """
    Run full backtest with rolling origin CV.
    
    Args:
        df: Full dataset with features and labels
        n_splits: Number of CV splits
    
    Returns:
        Dictionary with results: metrics per model, comparisons
    """
    pass

