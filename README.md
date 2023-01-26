# Bloc N° 5 : Industrialisation d'un algorithme d'apprentissage automatique et automatisation des processus de décision.

[Video explain - Bloc 5](https://share.vidyard.com/watch/5Yq2uo1daUuTbL6fYDszVu?)

[Link to ML flow server](https://mlfga.herokuapp.com/)

[link to API documentation](https://apiga.herokuapp.com/docs)

[Link to dashboard](https://strga.herokuapp.com/)


# GetAround Project
GetAround allows to rent cars from any person for a few hours or a few days.

## Context and goals of this study:

1. The Data Science team is working on pricing optimization and expects from us that we suggest optimum prices for car owners using Machine Learning.
1. To mitigate frictions with late returns at checkout, GetAround decided to implement a minimum delay between two rentals. The Product Manager needs to decide the optimum threshold (in minutes) and scope (checking via mobile or connect). We prepared a dashboard to help him making this decision.

# 1. Pricing optimization – Machine learning - / predict endpoint

## ML flow tracking

The related files are stored in **1-ml_flow_tracking**, credentials have been removed.

- An **ML flow server** has been set up to store models and their artifacts.

URL to ML flow tracking : https://mlfga.herokuapp.com/

In the experiment called rental_price, the loaded model is a linear regression.

- Here are the main commands used to deploy:

#### ML Flow tracking setup :

-files : Dockerfile + requirements.txt + run.sh 

-terminal command : docker build . -t mlf-getaround

-terminal command : source run.sh

-check of the app in local by typing localhost:4000 on internet explorer

-if ok, deploy to heroku with terminal commands :

heroku login

heroku container:login

heroku create mlfga

heroku container:push web -a mlfga

heroku container:release web -a mlfga

-In the heroku app, feed config variables (S3 bucket + AWS credentials)

-Put URI add-ons in heroku ressources with heroku postgres

#### Feed with a model :

-Add a file app.py to set experiments on the ML flow tracking app and the source of data used

-terminal command : docker build . -t mlf-getaround

-run the image with source run.sh

## API - / predict endpoint

The related files are stored in **2-API**, the credentials have been removed.

- An **API** has been built to allow to get predictions on the model loaded.

Root URL of the API : https://apiga.herokuapp.com/

URL to request API : https://apiga.herokuapp.com/predict

This end point accepts POST method with JSON input data and returns predictions. We assume inputs will be always well formated. 

Here below the features, expected format and default value : 

![Features of the API](https://github.com/ElisaOu/Bloc5_Indus_d_algo_d_apprentissage_auto_et_automatisation_processus_decision/blob/main/API_features.JPG)

- The code for requesting the API is available in file attached : request_predict_API.ipynb

- The **documentation of the API** is available at https://apiga.herokuapp.com/docs

- Here are the main commands to deploy :

#### API :

-files : Dockerfile + app.py + requirements.txt + run.sh 

-terminal command : docker build . -t api-getaround

-Add a secrets.sh containing credentials (credentials have been removed here)

-terminal command : source secrets.sh

-terminal command : source run.sh

-check of the app in local by typing localhost:4000 on internet explorer

-if ok, deploy to heroku with terminal commands

heroku login

heroku container:login

heroku create apiga

heroku container:push web -a apiga

heroku container:release web -a apiga

-In the heroku app, feed config variables, same as in run.sh


# 2. Dashboarding

The related files are stored in **3-streamlit**

- This dashboard is a supporting tool to make the right trade off between mitigating impact of delays and not hurting the revenue of cars owners. 

It focuses on threshold (in minutes) and scope (checking via mobile or connect).

Here is the dashboard app : https://strga.herokuapp.com/

- Main conclusions from the dashboard:

More than 80% of the rents are done through mobile.

-Implementing a minimum threshold between 2 rents would concern 9% of the number of rents in average (6% for mobile scope and 19% for connect scope).
Talking about number of cars, putting the threshold to 90 minutes would impact ~40% of the cars rented, while putting it to 480 minutes would impact over 70% of the cars rented. 

The threshold needs thus to be defined carefully to fix issues in the consecutive rents without killing opportunities of consecutive rents.

-Late check-outs concern about half of the cars with consecutive rents (mobile about 60% and connect about 40%). 

Third quartile is 86 minutes.

In term of impact for next driver, most of the issues are below 120 minutes. 

Most of late check-outs come from mobile with longer and more frequent delays.

-Applying a threshold means fixing issues but also missing opportunities of consecutive rents as the car would not be available during a given time for another rent.

To balance both effects the threshold needs to be set as low as possible and on a limited scope.

As mobile generates more issues, best would be to set the threshold on mobile only.

The threshold pops between 30 minutes (solving 87 problematic cases out of 126) and 60 minutes solving 102 problematic cases out of 126).

- Here are the main commands to deploy :

-files : Dockerfile + app.py + config.toml 

-terminal command : docker build . -t strga

-terminal command : docker run -it -e PORT=80 -p 4000:80

-check of the app in local by typing localhost:4000 on internet explorer

-deploy to heroku with terminal commands

heroku login

heroku container:login

heroku create apiga

heroku container:push web -a strga

heroku container:release web -a strga

# Conclusion

Here are the tools delivered for this project:

- The **complete code** stored in a github repo

- An **ML flow tracking server** to store machine learning models

- A **documented online API**

- An **online dashboard**.
 
Happy reading !
