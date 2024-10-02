import requests
import io


from PIL import Image


def trim_transparent(image_url):
    # Fetch the image from the URL
    response = requests.get(image_url)
    if response.status_code == 200:
        # Load the image from the response content using BytesIO
        img = Image.open(io.BytesIO(response.content)).convert("RGBA")

        # Get the alpha channel (transparency layer)
        alpha = img.split()[3]

        # Convert the alpha channel to a binary mask (0 for transparent, 255 for opaque)
        binary_alpha = alpha.point(lambda p: p > 0 and 255)

        # Get the bounding box of non-transparent regions
        bbox = binary_alpha.getbbox()

        if bbox:
            # Crop the image using the bounding box
            cropped_img = img.crop(bbox)
            return cropped_img  # Return the cropped image
        else:
            print("No non-transparent pixels found, nothing to crop.")
            return img  # Return the original image if no cropping is needed
    else:
        raise Exception(f"Failed to fetch image. HTTP status code: {response.status_code}")