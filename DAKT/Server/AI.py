import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
import joblib

def load_and_prepare_data(filepath):
    df = pd.read_csv(filepath)
    y = df['Label'].apply(mapping_target)
    X = df.drop(columns=['Label'], axis=1)
    numericals = df.select_dtypes(include='number').columns.tolist()
    stan = StandardScaler()
    X[numericals] = stan.fit_transform(X[numericals])

    joblib.dump(stan, 'scaler.pkl')
    return train_test_split(X, y, test_size=0.2, random_state=42, shuffle=True)


# Mapping to 1 or 0
def mapping_target(x):
    """
        Arg:
        if clause: (bool)

        Return:
        Binary classes:
            Safe: 0
            Signs of water pollution: 1
            Pollution: 2
    """
    if x == 'Safe':
        return 0
    elif x == 'Signs of Water Pollution':
        return 1
    else:
        return 2


def RandomForest_Training(X_train, X_test, y_train, y_test):
    rdf = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42).fit(X_train, y_train)
    y_train_pred = rdf.predict(X_train)
    y_test_pred = rdf.predict(X_test)
    return y_train_pred, y_test_pred, rdf

def SVC_Training(X_train, X_test, y_train, y_test):
    model = SVC(kernel='linear', random_state=42)
    model.fit(X_train, y_train)
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    return y_train_pred, y_test_pred, model






