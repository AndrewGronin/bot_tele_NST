import requests
import config
def up(image_URL):
    r = requests.post(
        "https://api.deepai.org/api/torch-srgan",
        data={
            'image': image_URL,
        },
        headers={'api-key': config.API_KEY}
    )
    print(r.json())
    return r.json()['output_url']

