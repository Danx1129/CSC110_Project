"""CSC110 Fall 2020: Final Project (plot.py)
 
Plotting line graphs for correlation between donations
from fossil fuel companies to politicians and GHG emissions.
This was used for analysis alongside the graphing in Graph.py
"""

import data
import plotly.graph_objects as go
from typing import Tuple


def simple_linear_regression(list_x: list, list_y: list) -> Tuple[float, float]:
    """Perform a linear regression on the given points.
 
    list_x is a list of x-coordinates and list_y is the list of corresponding y-coordinates.
    This function returns a pair of floats (a, b) such that the line
    y = a + bx is the approximation of this data.
 
    Preconditions:
        - len(list_x) > 0
        - len(list_y) > 0
    """
    x_avg = find_average(list_x)
    y_avg = find_average(list_y)
    length = len(list_x)
 
    b_numerator = sum([(list_x[i] - x_avg) * (list_y[i] - y_avg) for i in range(0, length)])
    b_denominator = sum([(x - x_avg) ** 2 for x in list_x])
    b = b_numerator / b_denominator
    a = y_avg - b * x_avg
    return (a, b)


def find_average(nums: list) -> float:
    """Return the average of a list of numbers.
    """
    return sum(nums) / max(len(nums), 1)


def plot(years: list, list_x: list, list_y: list, a: float, b: float, country: str) -> None:
    """
    Plot the given x- and y-coordinates and linear regression model using plotly.
    """
    fig = go.Figure(data=go.Scatter(x=list_x, y=list_y, mode='markers',
                                    name='Year', text=years))
 
    fig.add_trace(go.Scatter(x=[0, max(list_x)], y=[a, a + b * max(list_x)],
                             mode='lines', name='Regression line'))
 
    title = ': Effect of donations from fossil fuel companies ' \
            'to politicians on annual GHG emissions'
    fig.update_layout(title=country + title,
                      xaxis_title='Donations ($)',
                      yaxis_title='Total GHG Emissions (megatonnes of CO2 equivalent)')
 
    fig.show()

def showPlots() -> None:
    """Show scatter plots for the datasets"""
    
    print('Importing data...')
    usa_data = data.UsaData()
    canada_data = data.CanadaData()
    print('Done')
    
    # get data from USA
    usa_years = usa_data.get_year()
    usa_donations = usa_data.get_donation()[1:]
    usa_emissions = usa_data.get_emission()[:-1]
    
    # get data from Canada
    canada_years = canada_data.get_year()
    canada_donations = canada_data.get_donation()
    print(canada_donations)
    canada_emissions = canada_data.get_emission()
    
    # plot graphs
    a_usa, b_usa = simple_linear_regression(usa_donations, usa_emissions)
    plot(usa_years, usa_donations, usa_emissions, a_usa, b_usa, 'USA')
    
    a_canada, b_canada = simple_linear_regression(canada_donations, canada_emissions)
    plot(canada_years, canada_donations, canada_emissions, a_canada, b_canada, 'Canada')

    print('Donations from USA: ' + str(usa_donations))
    print('Emissions from USA: ' + str(usa_emissions) + '\n')
    print('Donations from Canada: ' + str(canada_donations))
    print('Emissions from Canada: ' + str(canada_emissions))

if __name__ == "__main__":
    showPlots()
