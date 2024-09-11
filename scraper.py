import os
import requests
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup

# Sample data for the list of names
data = [
    ("tolstoy", "Leo Tolstoy"),
    ("solovyov", "Vladimir Solovyov"),
    ("berdyaev", "Nikolai Berdyaev"),
    ("bakunin", "Mikhail Bakunin"),
    ("kropotkin", "Peter Kropotkin"),
    ("florensky", "Pavel Florensky"),
    ("rozanov", "Vasily Rozanov")
]

# Define the directory to save images
output_dir = 'images'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Function to download and process image
def download_and_process_image(search_term, file_name):
    try:
        # Search for the image (this part would need a custom search or API implementation)
        # Here, we're assuming you already have a URL for the image
        search_url = f"https://commons.wikimedia.org/w/index.php?search={search_term}&title=Special:MediaSearch&go=Go&type=image"
        response = requests.get(search_url)
        # Parse the HTML content
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the first image in the search results
        img_element = soup.find('img', class_='sdms-image')
        
        if img_element and 'src' in img_element.attrs:
            image_url = img_element['src']
            if not image_url.startswith('http'):
                image_url = 'https:' + image_url
        else:
            raise Exception("No image found in search results")
        
        # Download the image
        img_response = requests.get(image_url)
        img = Image.open(BytesIO(img_response.content))
        
        # Convert to .png and save with the desired filename
        png_filename = os.path.join(output_dir, f"{file_name}.png")
        
        # Crop image to square
        width, height = img.size
        new_size = min(width, height)
        left = (width - new_size) / 2
        top = (height - new_size) / 2
        right = (width + new_size) / 2
        bottom = (height + new_size) / 2
        img = img.crop((left, top, right, bottom))
        
        # Save image as .png
        img.save(png_filename, "PNG")
        print(f"Image saved as: {png_filename}")
        
    except Exception as e:
        print(f"Failed to download or process image for {search_term}: {e}")

# Loop through the data and process each name
for file_name, full_name in data:
    download_and_process_image(full_name, file_name)