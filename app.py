import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
plt.style.use('ggplot')

import math
import epyestim.covid19 as covid19

class Application():
    def __init__(self):
        self.confirmed_file = "data/data_Confirmed.csv"
        self.deaths_file = "data/data_Deaths.csv"
        self.recovered_file = "data/data_Recovered.csv"

        self.confirmed_df = self.get_df(self.confirmed_file)
        self.deaths_df = self.get_df(self.deaths_file)
        self.recovered_df = self.get_df(self.recovered_file)

        self.countries = self.get_countries()

    def get_countries(self):
        df = pd.read_csv("data/data_Confirmed.csv")
        countries = list(df["Country/Region"].unique())
        return countries

    def get_df(self, path, transform=True):
        df = pd.read_csv(path)
        df = df.T
        
        headers = df.iloc[0]
        new_df  = pd.DataFrame(df.values[1:], columns=headers, index=pd.DatetimeIndex(df.index[1:]))
        new_df.columns.name = ""
        new_df.index.name = "Date"
        if transform:
            new_df = new_df.diff()
            new_df.fillna(value=0, inplace=True)
            new_df[new_df < 0] = 0 
        return new_df

    def plot_r(self, country):
        R_t = covid19.r_covid(self.confirmed_df[country], smoothing_window=21)
        fig, ax = plt.subplots(1,1, figsize=(13, 8))

        R_t.loc[:,'Q0.5'].plot(ax=ax, color='#2c78c9')
        ax.fill_between(R_t.index, 
                        R_t['Q0.025'], 
                        R_t['Q0.975'], 
                        color='#2c78c9', alpha=0.2)
        ax.set_xlabel('Date')
        ax.set_ylabel('$R_{t}$ with 95%-CI')
        ax.set_ylim([0, math.ceil(R_t["Q0.5"].max())])
        ax.axhline(y=1, color="black", alpha=0.7, linestyle='--')
        ax.set_title('Estimate of time-varying effective reproduction number $R_{t}$ (' + country + ')')
        return fig

    def plot_confirmed(self, country):
        daily = self.confirmed_df[country]
        weekly_mean = daily.rolling(7).mean()
        df = pd.DataFrame({"daily": daily, "weekly_mean": weekly_mean}, index=daily.index)

        fig, ax = plt.subplots(figsize=(13,8))
        ax.bar(x=df.index, height=df["daily"], width=1, color='gray', alpha=0.5)
        ax.plot(df.index, df["weekly_mean"], color='#dd494e', alpha=1, linewidth=2)
        
        ax.set_xlabel('Date')
        ax.set_ylabel('No. of new cases')
        ax.set_ylim([0, math.ceil(df["daily"].max())])
        ax.set_title('Number of new daily cases, with a seven-day moving average (' + country + ')')
        return fig

    def plot_deaths(self, country):
        daily = self.deaths_df[country]
        weekly_mean = daily.rolling(7).mean()
        df = pd.DataFrame({"daily": daily, "weekly_mean": weekly_mean}, index=daily.index)

        fig, ax = plt.subplots(figsize=(13,8))
        ax.bar(x=df.index, height=df["daily"], width=1, color='gray', alpha=0.5)
        ax.plot(df.index, df["weekly_mean"], color='black', alpha=1, linewidth=2)
        
        ax.set_xlabel('Date')
        ax.set_ylabel('No. of new deaths')
        ax.set_ylim([0, math.ceil(df["daily"].max())])
        ax.set_title('Number of new daily deaths attributed to COVID-19, with a seven-day moving average (' + country + ')')
        return fig

    def plot_recovered(self, country):
        daily = self.recovered_df[country]
        weekly_mean = daily.rolling(7).mean()
        df = pd.DataFrame({"daily": daily, "weekly_mean": weekly_mean}, index=daily.index)

        fig, ax = plt.subplots(figsize=(13,8))
        ax.bar(x=df.index, height=df["daily"], width=1, color='gray', alpha=0.5)
        ax.plot(df.index, df["weekly_mean"], color='#10ba57', alpha=1, linewidth=2)
        
        ax.set_xlabel('Date')
        ax.set_ylabel('No. of recoveries')
        ax.set_ylim([0, math.ceil(df["daily"].max())])
        ax.set_title('Number of daily recoveries, with a seven-day moving average (' + country + ')')
        return fig

    def render_app(self):
        st.title('COVID-19 Data Tracker: Time-Varying Reproduction Number, Daily Confirmed Cases, Deaths and Recoveries')
        st.text("")
        st.text("")
        st.markdown("Using [data](https://doi.org/10.7910/DVN/L20LOT) available up to the: 2021-02-12")
        st.markdown("See the [method](http://github.com/ekibasprojects) of how these estimates are derived.")
        st.text("")
        st.text("")
    

        idx = self.countries.index("US")
        country = st.selectbox(
            'Choose a country',
            self.countries,
            idx)

        st.write(self.plot_r(country))
        st.write(self.plot_confirmed(country))
        st.write(self.plot_deaths(country))
        st.write(self.plot_recovered(country))

app = Application()
app.render_app()