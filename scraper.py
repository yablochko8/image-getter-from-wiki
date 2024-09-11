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


# Function to query Wikidata API to get image URL
def get_image_url_from_wikidata(search_term):
    try:
        # Wikidata query to search for the individual
        url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={search_term}&language=en&format=json"
        response = requests.get(url).json()

        if response['search']:
            # Get the first entity id (assumes first result is the correct person)
            entity_id = response['search'][0]['id']
            
            # Query for the entity's data, including the image
            entity_url = f"https://www.wikidata.org/wiki/Special:EntityData/{entity_id}.json"
            entity_data = requests.get(entity_url).json()

            # Try to extract the image from the entity data
            claims = entity_data['entities'][entity_id]['claims']
            if 'P18' in claims:
                # P18 is the property for an image
                image_filename = claims['P18'][0]['mainsnak']['datavalue']['value']
                # Construct the URL to the image on Wikimedia Commons
                commons_url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{image_filename.replace(' ', '_')}"
                return commons_url
            else:
                print(f"No image found for {search_term}")
        else:
            print(f"No result found for {search_term}")
    except Exception as e:
        print(f"Error fetching image for {search_term}: {e}")
    
    return None


# Function to download and process image
def download_and_process_image(search_term, file_name):
    try:
        # Get the image URL from Wikidata
        image_url = get_image_url_from_wikidata(search_term)
        if image_url is None:
            return

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