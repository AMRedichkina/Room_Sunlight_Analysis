import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Define a function to create a heatmap based on the room dimensions
def create_heatmap(width, height, source_x, source_y):
    data = np.zeros((height, width))
    for i in range(height):
        for j in range(width):
            dist = np.sqrt((i - source_y) ** 2 + (j - source_x) ** 2)
            data[i][j] = np.exp(-dist/100)

    # Create the heatmap plot
    fig, ax = plt.subplots()
    ax.imshow(data, cmap='inferno')

    ax.plot(source_x, source_y, 'r+')
    # Convert the plot to an image and return it
    image = fig_to_image(fig)
    return image

# Define a function to convert a matplotlib figure to an image
def fig_to_image(fig):
    from io import BytesIO
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    return buf

# Define the streamlit app
def main():
    st.title("The Indoor Lighting Data Visualizer Program")

    # Get the dimensions of the fiber from the user
    room_width = st.number_input("Room width (meters):", value=10, min_value=1)
    room_lenght = st.number_input("Room lenght (meters):", value=10, min_value=1)

    st.write("Select the location of the light source on the edge of the room (meters):")
    source_position = st.selectbox("Source position:", ["Top", "Right", "Bottom", "Left"])
    if source_position == "Top":
        source_x = st.number_input("X coordinate:", value=0, min_value=0, max_value=room_width)
        source_x *= 10
        source_y = 0
    elif source_position == "Right":
        source_x = room_width
        source_y = st.number_input("Y coordinate:", value=0, min_value=0, max_value=room_lenght)
        source_y *= 10
    elif source_position == "Bottom":
        source_x = st.number_input("X coordinate:", value=0, min_value=0, max_value=room_width)
        source_x *= 10
        source_y = room_lenght
    elif source_position == "Left":
        source_x = 0
        source_y = st.number_input("Y coordinate:", value=0, min_value=0, max_value=room_lenght)
        source_y *= 10
    # Create the heatmap based on the room dimensions
    heatmap = create_heatmap((room_width*10), (room_lenght*10), source_x, source_y)

    # Display the heatmap in the screen
    st.image(heatmap, use_column_width=True)

# Run the program
if __name__ == "__main__":
    main()
