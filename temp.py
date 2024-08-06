import requests
from io import BytesIO
from PIL import Image

webhook_url = 'https://discord.com/api/webhooks/1268540301899993119/cbTTTJLAR0v3UyxG2Exe9QitnImh0ABeOnf8M3OmJ1rgN1_gb_XDr-xMO9KfrNGii10D'
payload = {'content': 'Check out this image!', 'username': 'ImageBot'}

# Load or create an image
# For demonstration, we'll create an image using Pillow
image = Image.new('RGB', (100, 100), color = 'red')

# Save the image to a BytesIO object
image_bytes = BytesIO()
image.save(image_bytes, format='PNG')
image_bytes.seek(0)

# Prepare the files and payload for the webhook
files = {
    'file': ('image.png', image_bytes, 'image/png')
}
payload = {
    'content': 'Here is an image from memory!'
}

# Send the POST request to the Discord webhook
response = requests.post(webhook_url, data=payload, files=files)

# Check the response
if response.status_code == 204:
    print('Image successfully sent!')
else:
    print(f'Failed to send image: {response.status_code}, {response.text}')