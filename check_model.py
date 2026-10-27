import joblib
model = joblib.load('models/phish_model.pkl')
print(f"Features: {model.n_features_in_}")
print(f"Type: {type(model).__name__}")
if hasattr(model, 'feature_names_in_'):
    print("Features:", list(model.feature_names_in_))
else:
    print("No feature names")
print(f"Classes: {list(model.classes_)}")
