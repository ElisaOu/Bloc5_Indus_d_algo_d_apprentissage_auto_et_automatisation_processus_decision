# import librairies
import os
import pandas as pd
pd.options.mode.chained_assignment = None
from secrets import randbits # to avoid an error when running code on randbit

import time
import mlflow

from mlflow.models.signature import infer_signature
from sklearn.model_selection import train_test_split 
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.metrics import  mean_squared_error, mean_absolute_percentage_error, r2_score
from sklearn.linear_model import LinearRegression
#import joblib


if __name__ == "__main__":
    ### MLFLOW Experiment setup
    experiment_name="rental _price"
    mlflow.set_experiment(experiment_name)
    experiment = mlflow.get_experiment_by_name(experiment_name)

    client = mlflow.tracking.MlflowClient()
    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])

    run = client.create_run(experiment.experiment_id)

    print("training model...")
    
    # Time execution
    start_time = time.time()

    # Call mlflow autolog
    mlflow.sklearn.autolog(log_models=False) # We won't log models right away

    #import dataset
    df = pd.read_csv("get_around_pricing_project.csv", index_col =0)

    # X, y split 
    target_name = "rental_price_per_day"

    Y = df.loc[:,target_name]
    X = df.drop(target_name, axis = 1)

    # Train/test split
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=0)

    print(df.columns)

    # Preprocessing
    categorical_features = X_train.select_dtypes("object").columns # Select all the columns containing strings
    categorical_transformer = OneHotEncoder(drop='first', handle_unknown='error', sparse=False)

    numerical_feature_mask = ~X_train.columns.isin(X_train.select_dtypes("object").columns) # Select all the columns containing anything else than strings
    numerical_features = X_train.columns[numerical_feature_mask]
    numerical_transformer = StandardScaler()

    feature_preprocessor = ColumnTransformer(
        transformers=[
            ("categorical_transformer", categorical_transformer, categorical_features),
            ("numerical_transformer", numerical_transformer, numerical_features)
        ]
    )
    print("processing done")

    model = Pipeline(steps=[("features_preprocessing", feature_preprocessor),
                    ("reg", LinearRegression())
                    ])


    # Log experiment to MLFlow
    with mlflow.start_run() as run: 
        model.fit(X_train, Y_train)
        predictions = model.predict(X_train)

        # Log model seperately to have more flexibility on setup 
        mlflow.sklearn.log_model(sk_model=model, 
            artifact_path="pricing_getaround", 
            registered_model_name = "lin_reg",
            signature=infer_signature(X_train, predictions)
            )

    # If you want to persist model locally
    #joblib.dump(model, "model.joblib")

    print("...Done!")
    print(f"---Total training time: {time.time()-start_time}")