# Bloc N° 5 : Industrialisation d'un algorithme d'apprentissage automatique et automatisation des processus de décision.

[Video explain - Bloc 5](xxxxx)

[Link to ML flow server](https://mlfga.herokuapp.com/)

[link to API documentation](https://apiga.herokuapp.com/docs)

[Link to dashboard]( https://strga.herokuapp.com/)


# GetAround Project
GetAround allows to rent cars from any person for a few hours or a few days.

## Context and goals of this study:
1. The Data Science team is working on pricing optimization and expects from us that we suggest optimum prices for car owners using Machine Learning.
1. To mitigate frictions with late returns at checkout, GetAround decided to implement a minimum delay between two rentals. The Product Manager needs to decide the optimum threshold (in minutes) and scope (checking via mobile or connect). We prepared a dashboard to help him making this decision.

# Pricing optimization – Machine learning - / predict endpoint
1.	ML flow tracking

The related files are stored in <b>1-ml_flow_tracking<b>, the files containing credentials have been removed.

- An ML flow server has been set up to store models and their artifacts.

URL to ML flow tracking : https://mlfga.herokuapp.com/

In the experiment rental_price, the loaded model is a linear regression.

- Here are the main commands to deploy:



2.	API - / predict endpoint
The related files are stored in <b>2-API<b>, the files containing credentials have been removed.

- An API has been built to allow to get predictions on the model loaded.

URL to resquest API : https://apiga.herokuapp.com/predict

This URL can be used through a python coding, per file attached request_predict_API.ipynb

This end point accepts POST method with JSON input data and returns predictions. We assume inputs will be always well formated. Here below the features, expected format and default value : 

![alt text](https://github.com/[username]/[reponame]/blob/[branch]/image.jpg?raw=true)




- The documentation of the API is available at https://apiga.herokuapp.com/docs

- Here are the main commands to deploy:

# Dashboarding
The related files are stored in <b>3-streamlit<b>


- This dashboard is a supporting tool to make the right trade off between mitigating impact of delays and not hurting the revenue of cars owners. It focuses on threshold (in minutes) and scope (checking via mobile or connect).

Here is the dashboard app : https://strga.herokuapp.com/

- Main conclusions :
    More than 80% of the rents are done through mobile.
    •	Implementing a minimum threshold between 2 rents would concern 9% of the number of rents in average (6% for mobile scope and 19% for connect scope).
    Talking about number of cars, putting the threshold to 90 minutes would impact ~40% of the cars rented, while putting it to 480 minutes would impact over 70% of the cars rented. The threshold needs thus to be defined carefully to fix issues in the consecutive rents without killing opportunities of consecutive rents.
    •	Late check-outs concern about half of the cars with consecutive rents (mobile about 60% and connect about 40%). Third quartile is 86 minutes.
    In term of impact for next driver, the analysis focuses on time delta with previous rent minus delay: negative means friction with next driver. Most of the issues are below 120 minutes. Most of late check-outs come from mobile with bigger and more frequent negative values.
    •	Applying a threshold means fixing issues but also missing opportunities of consecutive rents as the car would not be available during a given time for another rent.
    To balance both effects the threshold needs to be set as low as possible and on a limited scope.
    As mobile generates more issues, best would be to set the threshold on mobile only.
    The threshold pops between 30 minutes (solving 87 problematic cases out of 126) and 60 minutes (solving 102 problematic cases out of 126).

