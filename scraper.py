import os
import requests
import time
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup

# Sample data for the list of names
data = [
    ("foucault", "Michel Foucault"),
    ("lyotard", "Jean-François Lyotard"),
    ("deleuze", "Gilles Deleuze"),
    ("guattari", "Félix Guattari"),
    ("rorty", "Richard Rorty"),
    ("butler", "Judith Butler")
]


headers = {'User-Agent': 'PantheonScrape/1.0 (https://pantheonchat.com/; pantheon@magicnumbers.io)'}

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
    # First, check if the image already exists (either jpg or png)
    jpg_filename = os.path.join(output_dir, f"{file_name}.jpg")
    png_filename = os.path.join(output_dir, f"{file_name}.png")
    if os.path.exists(jpg_filename) or os.path.exists(png_filename):
        print(f"Image already exists: {jpg_filename if os.path.exists(jpg_filename) else png_filename}")
        return

    try:
        # Get the image URL from Wikidata
        print(f"Searching for: {search_term}")
        image_url = get_image_url_from_wikidata(search_term)
        if image_url is None:
            print(f"No image URL found for {search_term}")
            return

        print(f"Image URL: {image_url}")

        # Download the image
        response = requests.get(image_url, headers=headers)
        response.raise_for_status()

        # Extract the file extension from the URL
        _, extension = os.path.splitext(os.path.basename(image_url))
        
        # Use the passed-in file_name with the original extension
        new_filename = f"{file_name}{extension}"
        
        # Save the image with the new filename
        filename = os.path.join(output_dir, new_filename)
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        print(f"Image saved as: {filename}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image for {search_term}: {e}")
    except Exception as e:
        print(f"Failed to process image for {search_term}: {e}")
    
    time.sleep(1)  # Add a 1-second delay to avoid rate limiting

# Loop through the data and process each name
for file_name, full_name in data:
    download_and_process_image(full_name, file_name)


# AFTER this is complete, loop through all the files in the output directory
# Convert them to PNG
# Crop them to a square
# Resize them to be max 1024x1024
# Save them in a new directory called "processed"

# Create the processed directory if it doesn't exist
processed_dir = os.path.join(os.path.dirname(output_dir), "processed")
os.makedirs(processed_dir, exist_ok=True)

# Loop through all files in the output directory
for filename in os.listdir(output_dir):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
        input_path = os.path.join(output_dir, filename)
        output_path = os.path.join(processed_dir, os.path.splitext(filename)[0] + '.png')
        
        try:
            with Image.open(input_path) as img:
                # Convert to PNG
                img = img.convert('RGBA')
                
                # Crop to square
                width, height = img.size
                size = min(width, height)
                left = (width - size) // 2
                top = 0  # Start cropping from the top
                right = left + size
                bottom = size
                img = img.crop((left, top, right, bottom))
                
                # Resize to max 1024x1024
                img.thumbnail((1024, 1024))
                
                # Save the processed image
                img.save(output_path, 'PNG')
                
            print(f"Processed and saved: {output_path}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

print("Image processing complete.")
