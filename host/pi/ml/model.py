from __future__ import annotations
from dataclasses import dataclass
from typing import List
import joblib  # type: ignore
from sklearn.linear_model import LogisticRegression  # type: ignore


@dataclass
class TherapyModel:
    """Thin wrapper over scikit-learn LogisticRegression."""
    clf: LogisticRegression

    @classmethod
    def new(cls) -> "TherapyModel":
        clf = LogisticRegression(
            random_state=42,
            max_iter=500,
            n_jobs=None,
        )
        return cls(clf=clf)

    def fit(self, X: List[List[float]], y: List[int]) -> None:
        self.clf.fit(X, y)

    def predict_proba(self, X: List[List[float]]) -> List[float]:
        # Return probability for class "1" (improve/succeed)
        probs = self.clf.predict_proba(X)[:, 1]
        return probs.tolist()

    def save(self, path: str) -> None:
        joblib.dump(self.clf, path)

    @classmethod
    def load(cls, path: str) -> "TherapyModel":
        clf = joblib.load(path)
        return cls(clf=clf)
