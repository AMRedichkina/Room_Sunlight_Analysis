import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

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
             # surface_normal = np.array([0, 0, 1])

    #         # # direction of the incident light (normalized)
    #         # light_direction = np.array([0.5, 0.5, -0.707])

    #         # # calculate cos(theta)
    #         # cos_theta = np.dot(surface_normal, light_direction)
            
            illumination = light_flux / (width*length) *10000
    #         #* np.exp(-dist))
    #         #print(light_flux)
    #         #print(illumination, dist)
    #         #data[i][j] = illumination
            data[i][j] = np.exp(-dist/illumination)                            #!!!

    # # data = np.zeros((length, width))
    # # for i in range(length):
    # #     for j in range(width):
    # #         dist = np.sqrt((i - source_y) ** 2 + (j - source_x) ** 2)
    # #         data[i][j] = np.exp(-dist/100)
    # Create the heatmap plot
    fig, ax = plt.subplots()
    ax.imshow(data, cmap='inferno')

    
    # Convert the plot to an image and return it
    image = fig_to_image(fig)

    # Define the dimensions of the room and the size of the floor in pixels

    # num_pixels_width = width 
    # num_pixels_length = length 

    # # Define the position of the window on the wall
    # window_position = (source_x, source_y, CONSTANTS.WINDOW_CENTER)

    # # Create a matrix of the distance of each pixel from the window
    # x_coords = np.linspace(0, width, num_pixels_width)
    # y_coords = np.linspace(0, length, num_pixels_length)
    # pixel_coords = np.meshgrid(x_coords, y_coords)
    # distances = np.sqrt((pixel_coords[0] - window_position[0])**2 + (pixel_coords[1] - window_position[1])**2 + CONSTANTS.WINDOW_CENTER**2)

    # # Define the surface normals for each pixel on the floor
    # surface_normals = np.zeros((num_pixels_length, num_pixels_width, 3))
    # surface_normals[..., 2] = 1  # Set the z-component of the normal to 1 for each pixel

    # # Define the direction of the light as a unit vector pointing down from the window
    # light_direction = np.array([0, 0, -1])

    # # Calculate the illumination of each pixel based on distance and angle
    # illuminations = (CONSTANTS.WINDOW_AREA / (4*np.pi*distances**2)) * np.maximum(np.dot(surface_normals, light_direction), 0)

    # Create a heat map of the floor
    # fig, ax = plt.subplots()
    # im = ax.imshow(illumination, cmap='inferno', origin='lower', extent=[0, width, 0, length])
    # plt.colorbar(im, ax=ax)
    # ax.set_title('Heat map of floor illumination')
    # ax.set_xlabel('Width (m)')
    # ax.set_ylabel('Length (m)')
    # ax.plot(source_x, source_y, 'r+')
    # # Display the heat map in the Streamlit app
    # image = fig_to_image(fig)

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
    st.title("The Indoor Lighting Data Visualizer")

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
    elif source_position == "West":
        source_x = room_width
        source_y = st.number_input("Y coordinate:", value=0, min_value=0, max_value=room_length)
        source_y *= 10
    elif source_position == "South":
        source_x = st.number_input("X coordinate:", value=0, min_value=0, max_value=room_width)
        source_x *= 10
        source_y = room_length
    elif source_position == "East":
        source_x = 0
        source_y = st.number_input("Y coordinate:", value=0, min_value=0, max_value=room_length)
        source_y *= 10

    # Create the heatmap based on the room dimensions
    heatmap = create_heatmap((room_width*10), (room_length*10), source_position, source_x, source_y)

    # Display the heatmap in the screen
    st.image(heatmap, use_column_width=True)

    

# Run the program
if __name__ == "__main__":
    main()
