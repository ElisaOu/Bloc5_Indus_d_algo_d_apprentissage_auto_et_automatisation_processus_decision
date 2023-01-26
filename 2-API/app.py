# Importing libraries
import mlflow 
import uvicorn
import json
import pandas as pd 
from pydantic import BaseModel
from typing import Literal, List, Union
from fastapi import FastAPI, File, UploadFile

# 2 suivants chez inspi K
import boto3
import pickle


# suivant chez inspi K mais pas sur corrigé)
mlflow.set_tracking_uri("https://mlfga.herokuapp.com/") 


description = """
Here is our application of machine learning! It predicts the rental price for cars and helps you fixing the right price!
Check out documentation below 👇 for more information on each endpoint. 
"""

tags_metadata = [
    {
        "name": "Introduction Endpoint",
        "description": "Simple endpoint to try out!",
    },

    {
        "name": "Machine Learning Endpoint",
        "description": "Rental cars right pricing"
    }
]


app = FastAPI(
    title= "🚗 Estimate the right price and rent your car!",
    description=description,
    version="0.1",
    contact={
        "name": "Elisa Ouillé",
        "url": "https://www.linkedin.com/in/elisaouille/",
    },
    openapi_tags=tags_metadata
)


class PredictionFeatures(BaseModel):
    model_key: str = 'Lamborghini'
    mileage: int = 40000
    engine_power: int = 225
    fuel: str = 'petrol'
    paint_color: str = 'grey'
    car_type: str = 'sedan'
    private_parking_available: bool = True
    has_gps: bool = True
    has_air_conditioning: bool = True
    automatic_car: bool = False
    has_getaround_connect: bool = True
    has_speed_regulator: bool = True
    winter_tires: bool = True
    # if empty, replacing by most common data (or mean) from our model prediction dataset


@app.get("/", tags=["Introduction Endpoint"])
async def index():

    message = 'This is the API default endpoint. To get more information about the API, go to "/docs".'
    return message



@app.post("/predict", tags=["Machine Learning Endpoint"])
async def predict(features: PredictionFeatures):
    """
    Estimation of rental price for cars.
    """
    # Read data 
    df = pd.DataFrame(dict(features), index=[0])

    # Log model from mlflow 
    logged_model = 'runs:/22442f6913df4a0fa3b2c9d44c0e6570/pricing_getaround'

    # Load model as a PyFuncModel.
    loaded_model = mlflow.pyfunc.load_model(logged_model)

    # If you want to load model persisted locally
    #loaded_model = joblib.load('salary_predictor/model.joblib')

    prediction = loaded_model.predict(df)

    # Format response
    response = {"prediction": prediction.tolist()[0]}
    return response


if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000) # Here you define your web server to run the `app` variable 
                                    # (which contains FastAPI instance), with a specific host IP (0.0.0.0) and port (4000)