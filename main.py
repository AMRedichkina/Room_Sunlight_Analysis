import streamlit as st

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import datetime
import pytz

from calculations import calculations
from receive_current_data_api import recive_data_from_table, recive_data_api

import CONSTANTS



# Define a function to create a heatmap based on the room dimensions
def create_heatmap(width, length, source_position, source_x, source_y):
    recive_data_api()
    data_api = recive_data_from_table()
    light_flux = calculations(source_position, data_api)
    data = np.zeros((length, width))
    for i in range(length):
         for j in range(width):
            dist = np.sqrt((i - source_y) ** 2 + (j - source_x) ** 2)
            illumination = light_flux / (width*length)
            data[i][j] = np.exp(-dist/(illumination * 10000))

    fig, ax = plt.subplots()
    im = ax.imshow(data, cmap='inferno', vmin=0, vmax=1)  # set vmin and vmax here
    fig.colorbar(im)
    image1 = fig_to_image(fig)
    
    # Create heatmap with three zones
    
    colors = ['#f5c6cb', '#fce5cd', '#d4edda']  # Define colors for each zone
    cmap = ListedColormap(colors)
    bounds = [0.15, 0.66, 1]  # Define boundaries for each zone
    norm = plt.Normalize(bounds[0], bounds[-1])
    fig, ax = plt.subplots()
    im = ax.imshow(data, cmap=cmap, norm=norm)
    cbar = ax.figure.colorbar(im, ax=ax, ticks=bounds)
    cbar.ax.set_yticklabels(['Dark', 'Medium', 'Light'])
    image2 = fig_to_image(fig)

    return image1, image2

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
    st.image(heatmap[0], use_column_width=True)
    st.image(heatmap[1], use_column_width=True)

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
    recommendation = {
        'Dark zone': 'Since this area receives the least amount of natural light, it is best used as a space for activities that do not require bright light, such as a home theater or a cozy reading nook.',
        'Medium-light zone': 'This area receives moderate amounts of natural light and is perfect for a workspace, an art studio, or a craft room, where natural light can help with color accuracy and reduce eye strain.',
        'Light zone': 'The area that receives the most natural light is best suited for activities that require bright light, such as a dining area, a playroom, or a home gym.'
    }

    # Define the window treatments and plants recommendations
    window_treatments = 'In all zones, it is important to take advantage of natural light by using window treatments that allow for light to filter through while also providing privacy and controlling glare.'
    plants = 'Additionally, incorporating plants can help improve air quality and bring a touch of nature into the space, especially in areas that receive ample sunlight.'

    # Define the styling for the recommendation
    header_style = '<h3 style="text-align:center;font-weight:bold">Recommendation</h3>'
    zone_style = '<h4 style="font-weight:bold">{}</h4>'
    text_style = '<p style="text-align:justify">{}</p>'

    # Display the recommendation with the styling
    st.markdown(header_style, unsafe_allow_html=True)
    for zone, text in recommendation.items():
        st.markdown(zone_style.format(zone), unsafe_allow_html=True)
        st.markdown(text_style.format(text), unsafe_allow_html=True)
    st.markdown(text_style.format(window_treatments), unsafe_allow_html=True)
    st.markdown(text_style.format(plants), unsafe_allow_html=True)

# Run the program
if __name__ == "__main__":
    main()
