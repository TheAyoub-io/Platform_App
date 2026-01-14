
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

# Custom Transformer for creating new features
class FeatureCreator(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X_ = X.copy()
        # Ensure columns are numeric and handle potential errors
        X_['Duree'] = pd.to_numeric(X_['Duree'], errors='coerce').fillna(0)
        X_['Cout_de_la_Vie'] = pd.to_numeric(X_['Cout_de_la_Vie'], errors='coerce').fillna(1)
        X_['budget'] = pd.to_numeric(X_['budget'], errors='coerce').fillna(0)

        # Create budget-related features
        X_['Budget_per_day'] = X_['budget'] / (X_['Duree'] + 1e-6)
        X_['Budget_Ajuste'] = X_['Budget_per_day'] / (X_['Cout_de_la_Vie'] + 1e-6)

        # Create interaction feature
        X_['Interet_Continent'] = X_['Interet'].astype(str) + '_' + X_['continent'].astype(str)
        return X_
