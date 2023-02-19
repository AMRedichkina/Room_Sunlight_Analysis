import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import datetime
import pytz

from calculations import calculations
from receive_current_data_api import recive_data_from_table, recive_data_api

import CONSTANTS

# Define a function to create a custom colormap with three zones
def create_custom_cmap():
    # Define the colors for the three zones
    colors = ['#1f77b4', '#ff7f0e', '#d62728']
    # Define the thresholds for the three zones
    thresholds = [0.65, 0.75, 0.90, 1]
    # Create a colormap that maps each zone to a specific color
    cmap = plt.matplotlib.colors.LinearSegmentedColormap.from_list('custom', list(zip(thresholds, colors)))
    return cmap

# Define a function to create a heatmap based on the room dimensions
def create_heatmap(width, length, source_position, source_x, source_y):
    recive_data_api()
    data_api = recive_data_from_table()
    light_flux = calculations(source_position, data_api)
    data = np.zeros((length, width))
    for i in range(length):
         for j in range(width):
            dist = np.sqrt((i - source_y) ** 2 + (j - source_x) ** 2)
            illumination = light_flux / (width*length) * 10000
            data[i][j] = np.exp(-dist/illumination)
    
    # # Create the first heatmap plot with a gradient fill
    # fig, axs = plt.subplots(1, 2, figsize=(12, 5))
    # axs[0].imshow(data, cmap='inferno')
    # axs[0].set_title('Gradient Fill')

    # # Create the second heatmap plot with three zones
    # bins = np.digitize(data, np.linspace(0, 1, 4))
    # cmap = create_custom_cmap()
    # axs[1].imshow(bins, cmap=cmap)
    # axs[1].set_title('Three Zones')

    fig, ax = plt.subplots()
    im = ax.imshow(data, cmap='inferno', vmin=0, vmax=1)  # set vmin and vmax here
    fig.colorbar(im)
    image = fig_to_image(fig)
    return image

# Define a function to convert a matplotlib figure to an image
def fig_to_image(fig):
    from io import BytesIO
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    return buf

# Launching the program
def main():
    st.title("The Solar Illumination Data Visualizer")

    # Get the dimensions of the fiber from the user
    room_width = st.number_input("Room width (meters):", value=10, min_value=1)
    room_length = st.number_input("Room lenght (meters):", value=10, min_value=1)

    # Get the position of the window from the user
    st.write("Select the location of the light source on the edge of the room (meters):")

    source_position = st.selectbox("Source position:", ["North", "West", "South", "East"])
    if source_position == "North":
        source_x = st.number_input("X coordinate:", value=0, min_value=0, max_value=room_width)
        source_x *= 10
        source_y = 0
    elif source_position == "East":
        source_x = room_width*10
        source_y = st.number_input("Y coordinate:", value=0, min_value=0, max_value=room_length)
        source_y *= 10
    elif source_position == "South":
        source_x = st.number_input("X coordinate:", value=0, min_value=0, max_value=room_width)
        source_x *= 10
        source_y = room_length*10
    elif source_position == "West":
        source_x = 0
        source_y = st.number_input("Y coordinate:", value=0, min_value=0, max_value=room_length)
        source_y *= 10

    # Create the heatmap based on the room dimensions
    heatmap = create_heatmap((room_width*10), (room_length*10), source_position, source_x, source_y)

    # Display the heatmap in the screen
    st.image(heatmap, use_column_width=True)

    # Create the sidebar with main information
    st.sidebar.title("Information")
    data_for_sidebar = recive_data_from_table()
    # Add the current time
    current_time = datetime.datetime.now(pytz.UTC) 
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    st.sidebar.subheader("Current Time")
    st.sidebar.write(formatted_time)

    # Add the sunset time
    sunset_time = data_for_sidebar[1]
    
    st.sidebar.subheader("Sunset Time")
    st.sidebar.write(sunset_time)

    # Add the time of dawn
    dawn_time = data_for_sidebar[2]
    st.sidebar.subheader("Time of Dawn")
    st.sidebar.write(dawn_time)

    # Add the intensity
    intens = calculations(source_position, data_for_sidebar)  
    st.sidebar.subheader("The total light intensity entering the room through the window")
    st.sidebar.write(intens)

    # Add the recommendation
    recommendation = "Recommendation" 
    st.subheader("Recommendation")
    st.write(recommendation)    

# Run the program
if __name__ == "__main__":
    main()
