import streamlit as st
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pip
pip.main(["install", "openpyxl"])


### Config
st.set_page_config(
    page_title="Get Around Dashboard",
    page_icon="🚗",
    layout="wide"
)

DATA_URL = ('https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_delay_analysis.xlsx')

### App
st.title("Get Around Dashboard 🚗")

st.markdown("""
Get Around allows to rent cars from any person for a few hours or a few days.

Any user is expected to bring back the car on time, but it happens that drivers are late for the check-out. This can generate high friction for the next driver if the car was supposed to be rented again on the same day.
In order to mitigate those issues we are requested to help defining a threshold defining a minimum delay between two rentals. 

The goal of this dashboard is to help understanding what is the optimum threshold (in minutes) and scope (checking type via mobile or connect).
""")
st.markdown("---")

# load data
df = pd.read_excel('https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_delay_analysis.xlsx', engine="openpyxl") 

# Replacing NaN by 0 for "delay_at_checkout_in_minutes" and "previous_ended_rental_id"
df["delay_at_checkout_in_minutes"] = df["delay_at_checkout_in_minutes"].fillna(0)
df["previous_ended_rental_id"] = df["previous_ended_rental_id"].fillna(0)
# Replacing NaN by very long value for "time_delta_with_previous_rental_in_minutes" to keep the raws and identify there is no next rent registered
df["time_delta_with_previous_rental_in_minutes"] = df["time_delta_with_previous_rental_in_minutes"].fillna(5000)  

# adding a column delay (1/0, keeping in mind no delay can be in advance), prev_rental (1/0) and rental (1/0 where 0 means canceled)
df['delay'] = df['delay_at_checkout_in_minutes'].apply(lambda x: 1 if x >0 else 0)
df["prev_rent"] = df["previous_ended_rental_id"].apply(lambda x: 1 if x >0 else 0)
df["rental"] = df["state"].apply(lambda x: 1 if x == "ended" else 0)  

# When there are 2 consecutive rents, let's put back the checking type and delay of the previous rent
df_info_to_add = df[["rental_id", "checkin_type", "delay_at_checkout_in_minutes"]] #generating a second df to gather back the info about previous rent
df_def = pd.merge(df, df_info_to_add, left_on="previous_ended_rental_id", right_on = "rental_id", how = "outer")

# Replacing NaN by 0 or very long time, per same logic as above
df_def["rental_id_y"] = df_def["rental_id_y"].fillna(0)
df_def["checkin_type_y"] = df_def["checkin_type_y"].fillna(0)
df_def["delay_at_checkout_in_minutes_y"] = df_def["delay_at_checkout_in_minutes_y"].fillna(5000)
df_def = df_def.sort_values(by = "time_delta_with_previous_rental_in_minutes")
df_def = df_def[df_def["state"] == "ended"] #remove canceled rents


# show raw data
@st.cache(allow_output_mutation=True)
def load_data(nrows):
    return df_def

st.subheader ("View the raw data here ⬇︎")

data_load_state = st.text('Loading data...')
data = load_data(None)
data_load_state.text("") # change text from "Loading data..." to "" once the the load_data function has run

## Run the below code if the check is checked ✅
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)    


# CHARTS

## Split mobile/connect
st.subheader("Split Mobile/ Connect (nb of rents)")
perc_mobile = df_def[df_def["checkin_type_x"] == "mobile"].shape[0]/df_def.shape[0]*100
perc_connect = df_def[df_def["checkin_type_x"] == "connect"].shape[0]/df_def.shape[0]*100

col1, col2 = st.columns((1,5))
with col1:
    st.metric("% Mobile", np.round(perc_mobile, 1))
with col2:
    st.metric("% Connect", np.round(perc_connect, 1))

## Share of revenue potentially impacted by the feature
st.subheader("Share of revenue potentially impacted by the feature 💲")

### Create 3 columns
col1, col2, col3 = st.columns(3)

with col1: #Share of revenue having consecutive rents
    
    df_mobile = df_def[df_def["checkin_type_x"] == "mobile"]
    df_connect = df_def[df_def["checkin_type_x"] == "connect"]

    tot = round(df_def[df_def["previous_ended_rental_id"] > 1].shape[0]/df_def.shape[0] * 100 , 2)
    mobile = round( df_mobile[df_mobile["previous_ended_rental_id"] > 1].shape[0] / df_mobile.shape[0] * 100 ,2)
    connect = round( df_connect[df_connect["previous_ended_rental_id"] > 1].shape[0] / df_connect.shape[0] * 100 ,2)

    x_data = [connect, mobile, tot]
    y_data = ["connect", "mobile", "Complete scope"]

    fig1 = px.bar(df_def, x=x_data, y=y_data,  orientation='h', title = "Share of revenue with consecutive rents (percent nb of rents)", text_auto = True, labels={"x": "% of revenue", "y":"scope"})
    st.plotly_chart(fig1, use_container_width=True)

with col2: #Nb cars impacted by the feature

    nb_car_impacted = pd.DataFrame(df_def.groupby("time_delta_with_previous_rental_in_minutes")["time_delta_with_previous_rental_in_minutes"].count())
    nb_car_impacted = nb_car_impacted.rename(columns = {"time_delta_with_previous_rental_in_minutes" : "cars_count"})
    nb_car_impacted.reset_index(inplace = True)
    nb_car_impacted["cumulated_cars_count"] = nb_car_impacted["cars_count"].cumsum()
    nb_car_impacted = nb_car_impacted[nb_car_impacted["time_delta_with_previous_rental_in_minutes"]< 5000]

    fig2 = px.area(
    x = nb_car_impacted["time_delta_with_previous_rental_in_minutes"],
    y = nb_car_impacted["cumulated_cars_count"],
    labels = dict(x="Minutes between 2 rents", y= "Number of cars impacted"),
    title ="Nb of rentals impacted according to threshold - Complete scope"
    )
    st.plotly_chart(fig2, use_container_width=True)

with col3: #Nb cars impacted by the feature splitting mobile / connect
    nb_car_impacted_mob = pd.DataFrame(df_mobile.groupby("time_delta_with_previous_rental_in_minutes")["time_delta_with_previous_rental_in_minutes"].count())
    nb_car_impacted_mob = nb_car_impacted_mob.rename(columns = {"time_delta_with_previous_rental_in_minutes" : "cars_count"})
    nb_car_impacted_mob.reset_index(inplace = True)
    nb_car_impacted_mob["cumulated_cars_count"] = nb_car_impacted_mob["cars_count"].cumsum()
    nb_car_impacted_mob = nb_car_impacted_mob[nb_car_impacted_mob["time_delta_with_previous_rental_in_minutes"]< 5000]

    nb_car_impacted_conn = pd.DataFrame(df_connect.groupby("time_delta_with_previous_rental_in_minutes")["time_delta_with_previous_rental_in_minutes"].count())
    nb_car_impacted_conn = nb_car_impacted_conn.rename(columns = {"time_delta_with_previous_rental_in_minutes" : "cars_count"})
    nb_car_impacted_conn.reset_index(inplace = True)
    nb_car_impacted_conn["cumulated_cars_count"] = nb_car_impacted_conn["cars_count"].cumsum()
    nb_car_impacted_conn = nb_car_impacted_conn[nb_car_impacted_conn["time_delta_with_previous_rental_in_minutes"]< 5000]

    x = nb_car_impacted["time_delta_with_previous_rental_in_minutes"]
    y1 = nb_car_impacted_mob["cumulated_cars_count"]
    y2 = nb_car_impacted_conn["cumulated_cars_count"]

    fig3 = px.scatter(x =x, y = y1, color = px.Constant("mobile"), labels = dict(x="Minutes between 2 rents", y= "Number of cars impacted", color = "Scope"),
                title ="Nb of rentals impacted according to threshold - Mobile/Connect")
    fig3.add_scatter(x =x, y = y2, name = "Connect")

    st.plotly_chart(fig3, use_container_width=True)


## Late check-outs
st.subheader("Late check-outs ⌚")

### Create 3 columns - Analysis of late check-outs on total scope
col1, col2, col3 = st.columns((1,0.5,2))

with col1: #share of late check_out, total scope
    # rentals having delay from previous rent:
    delay_prev = df_def[(df_def["delay_at_checkout_in_minutes_y"] > 0) & (df_def["delay_at_checkout_in_minutes_y"] < 5000)].shape[0]
    # rentals NOT having delay from previous rent:
    no_delay_prev = df_def[df_def["previous_ended_rental_id"] > 0].shape[0]-delay_prev  

    fig4 = px.pie(df_def, values = [delay_prev, no_delay_prev], title = "Delay in check-out - Complete scope", hole = 0.5, names = ["Delay", "No delay"])
    st.plotly_chart(fig4, use_container_width=True)

with col2: #Distribution of delays
    # keeping only rents that had delay in previous rent
    delay_to_keep = (df_def["delay_at_checkout_in_minutes_y"] > 0) & (df_def["delay_at_checkout_in_minutes_y"] < 1000)
    has_prev_rent = df_def["prev_rent"] == 1
    mask = (delay_to_keep) & (has_prev_rent)
    df_delay = df_def[mask]
    df_delay = df_delay.copy()

    fig = px.violin(df_delay,
        y = df_delay["delay_at_checkout_in_minutes_y"],
        title ="Distribution (Major outliers removed)")
    st.plotly_chart(fig, use_container_width=True)
    
with col3:# impact on next driver, total scope
    # Impact = "time_delta_with_previous_rental_in_minutes" - "delay_at_checkout_in_minutes_y". Negative means friction with next driver. The more negative, the more impact
    df_delay["impact"] = df_delay["time_delta_with_previous_rental_in_minutes"] -  df_delay["delay_at_checkout_in_minutes_y"]
    df_delay = df_delay.reset_index(drop = True)    

    fig5 = px.violin(df_delay,
        x = df_delay["time_delta_with_previous_rental_in_minutes"],
        y = df_delay["impact"],
        title = "Impact on the next driver  = time delta with prev rent - delay (minutes) - Complete scope")
    st.plotly_chart(fig5, use_container_width=True)

### Create 2 columns - Analysis of late check-outs by scope
col1, col2 = st.columns((1,2))

with col1: #share of late check_out - select mobile or connect
    scope = st.selectbox("Select a scope", df_def["checkin_type_x"].sort_values().unique())
    df_def_scope = df_def[df_def["checkin_type_x"]==scope]

    delay_prev_scope = df_def_scope[(df_def_scope["delay_at_checkout_in_minutes_y"] > 0) & (df_def_scope["delay_at_checkout_in_minutes_y"] < 5000)].shape[0]
    no_delay_prev_scope = df_def_scope[df_def_scope["previous_ended_rental_id"] > 0].shape[0]-delay_prev_scope 

    fig6 = px.pie(df_def_scope, values = [delay_prev_scope, no_delay_prev_scope], title = "Delay in check-out - Mobile/ Connect", hole = 0.5, names = ["Delay", "No delay"])
    fig6.update_traces(textinfo='value')
    st.plotly_chart(fig6, use_container_width=True)

with col2: # impact on next driver, same filter applied as chart just above mobile or connect, same format as impact on next driver for total scope
    delay_to_keep_scope = (df_def_scope["delay_at_checkout_in_minutes_y"] > 0) & (df_def_scope["delay_at_checkout_in_minutes_y"] < 1000)
    has_prev_rent_scope = df_def_scope["prev_rent"] == 1
    mask = (delay_to_keep_scope) & (has_prev_rent_scope)
    df_delay_scope = df_def_scope[mask]
    df_delay_scope = df_delay_scope.copy()

    df_delay_scope["impact"] = df_delay_scope["time_delta_with_previous_rental_in_minutes"] -  df_delay_scope["delay_at_checkout_in_minutes_y"]
    df_delay_scope = df_delay_scope.reset_index(drop = True)    

    fig7 = px.violin(df_delay,
        x = df_delay_scope["time_delta_with_previous_rental_in_minutes"],
        y = df_delay_scope["impact"],
        title = "Impact on the next driver  = time delta with prev rent - delay (minutes) - Mobile/ Connect")
    st.plotly_chart(fig7, use_container_width=True)

## Number of problematic cases solved
st.subheader("Number of problematic cases solved ✔︎")
### Create 2 columns: 1 on total scope, 1 on scope selected per above
col1, col2 = st.columns(2)

with col1: # total scope
    # problematic scope are where impact(defined above) is negative
    problematic = df_delay[df_delay["impact"] < 0]

    # group by time "time_delta_with_previous_rental_in_minutes", count cumulated cases
    nb_cases_solved = pd.DataFrame(problematic.groupby("time_delta_with_previous_rental_in_minutes")["time_delta_with_previous_rental_in_minutes"].count())
    nb_cases_solved = nb_cases_solved.rename(columns = {"time_delta_with_previous_rental_in_minutes" : "cases_counts"})
    nb_cases_solved.reset_index(inplace = True)
    nb_cases_solved["cumulated_cases_count"] = nb_cases_solved["cases_counts"].cumsum()

    # missed opportunities calculated on total number rentals, where impact is positive
    df_def["impact"] = df_def["time_delta_with_previous_rental_in_minutes"] -  df_def["delay_at_checkout_in_minutes_y"]
    missed_opportunity = df_def[df_def["impact"] >= 0]

    # group by time "time_delta_with_previous_rental_in_minutes", count cumulated cases
    nb_missed_opportunity = pd.DataFrame(missed_opportunity.groupby("time_delta_with_previous_rental_in_minutes")["time_delta_with_previous_rental_in_minutes"].count())
    nb_missed_opportunity = nb_missed_opportunity.rename(columns = {"time_delta_with_previous_rental_in_minutes" : "cases_counts"})
    nb_missed_opportunity.reset_index(inplace = True)
    nb_missed_opportunity["cumulated_cases_count"] = nb_missed_opportunity["cases_counts"].cumsum()

    x = nb_cases_solved["time_delta_with_previous_rental_in_minutes"]
    y1 = nb_cases_solved["cumulated_cases_count"]
    y2 = nb_missed_opportunity["cumulated_cases_count"]

    fig8 = px.line(x =x, y = y1, 
                color = px.Constant("Nb problematic cases solved"), 
                labels = dict(x="Minutes between 2 rents", y= "Number of cases", color = "Case"), 
                title ="Nb of cases solved depending on threshold - Complete scope")
    fig8.add_scatter(x =x, y = y2, name = "Missed opportunities")

    st.plotly_chart(fig8, use_container_width=True)

with col2: # filter on scope, per filter applied at section "late check-outs"
    # Same logic as on total scope
    problematic_scope = df_delay_scope[df_delay_scope["impact"] < 0]
    problematic_scope = problematic_scope.copy()

    nb_cases_solved_scope = pd.DataFrame(problematic_scope.groupby("time_delta_with_previous_rental_in_minutes")["time_delta_with_previous_rental_in_minutes"].count())
    nb_cases_solved_scope = nb_cases_solved_scope.rename(columns = {"time_delta_with_previous_rental_in_minutes" : "cases_counts"})
    nb_cases_solved_scope.reset_index(inplace = True)
    nb_cases_solved_scope["cumulated_cases_count"] = nb_cases_solved_scope["cases_counts"].cumsum()

    df_def_scope["impact"] = df_def_scope["time_delta_with_previous_rental_in_minutes"] -  df_def_scope["delay_at_checkout_in_minutes_y"]
    missed_opportunity_scope = df_def_scope[df_def_scope["impact"] >= 0]

    nb_missed_opportunity_scope = pd.DataFrame(missed_opportunity_scope.groupby("time_delta_with_previous_rental_in_minutes")["time_delta_with_previous_rental_in_minutes"].count())
    nb_missed_opportunity_scope = nb_missed_opportunity_scope.rename(columns = {"time_delta_with_previous_rental_in_minutes" : "cases_counts"})
    nb_missed_opportunity_scope.reset_index(inplace = True)
    nb_missed_opportunity_scope["cumulated_cases_count"] = nb_missed_opportunity_scope["cases_counts"].cumsum()

    x = nb_cases_solved_scope["time_delta_with_previous_rental_in_minutes"]
    y1 = nb_cases_solved_scope["cumulated_cases_count"]
    y2 = nb_missed_opportunity_scope["cumulated_cases_count"]

    fig9 = px.line(x =x, y = y1, 
                color = px.Constant("Nb problematic cases solved"), 
                labels = dict(x="Minutes between 2 rents", y= "Number of cases", color = "Case"), 
                title ="Nb of cases solved depending on threshold - Mobile/connect")
    fig9.add_scatter(x =x, y = y2, name = "Missed opportunities")

    st.plotly_chart(fig9, use_container_width=True)
    st.markdown("""(Per filter applied on graphs section 'late check-outs')""")

# Separator
st.markdown("---")

# Conclusion
st.subheader("Conclusion")
st.markdown("""
More than 80% of the rents are done through mobile.

- Implementing a minimum threshold between 2 rents would concern 9% of the number of rents in average (6% for mobile scope and 19% for connect scope). 
Talking about number of cars, putting the threshold to 90 minutes would impact ~40% of the cars rented, while putting it to 480 minutes would impact over 70% of the cars rented. 
The threshold needs thus to be defined carefully to fix issues in the consecutive rents without killing opportunities of consecutive rents.
- Late check-outs concern about half of the cars with consecutive rents (mobile about 60% and connect about 40%). Third quartile is 86 minutes. 
In term of impact for next driver, the analysis focuses on time delta with previous rent minus delay: negative means friction with next driver. Most of the issues are below 120 minutes.
Most of late check-outs come from mobile with bigger and more frequent negative values.
- Applying a threshold means fixing issues but also missing opportunities of consecutive rents as the car would not be available during a given time for another rent. 
To balance both effects the threshold needs to be set as low as possible and on a limited scope. 

**As mobile generates more issues, best would be to set the threshold on mobile only.**

**The threshold pops between 30 minutes (solving 87 problematic cases out of 126) and 60 minutes (solving 102 problematic cases out of 126).**

""")


# Side bar 
st.sidebar.header("Content")
st.sidebar.markdown("""
    * [View the raw data here](#view-the-raw-data-here)
    * [Split Mobile/Connect](#split-mobile-connect-nb-of-rents)
    * [Share of revenue potentially impacted by the feature](#share-of-revenue-potentially-impacted-by-the-feature)
    * [Late check-outs](#late-check-outs)
    * [Number of problematic cases solved](#number-of-problematic-cases-solved)
    * [Conclusion](#conclusion)
""")
e = st.sidebar.empty()
e.write("")
st.sidebar.write("Optimum threshold definition 💶")

### Footer 
empty_space, footer = st.columns([1, 2])

with empty_space:
    st.write("")

with footer:
    st.markdown("""
        January 2023 🚗
    """)
