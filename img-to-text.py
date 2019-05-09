from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
import requests
import os
import time
import json

dbutils.fs.mount(
  source = "<date_factory_source>",
  mount_point = "/mnt/forms",
  extra_configs ={"fs.azure.account.key.forms.blob.core.windows.net":"<your_data_factory_key>"}
  )

# Construct Cognitive service information
class CognitiveConfig:
  def __init__(self, url, key):
    self.url = url
    self.key = key
    
#Construct Image Path
class Img:
  def __init__(self, storagePath, imgName):
    self.storagePath = storagePath
    self.imgName = imgName
    
  def getFullPath(self):
    return os.path.join(self.storagePath, self.imgName)

#Construct Image to Text Mode
class ImgToTextMode:
  def __init__(self, mode, isRaw):
    self.mode = mode
    self.isRaw = isRaw
    
cogConfig = CognitiveConfig("https://eastus.api.cognitive.microsoft.com/", "<your_cognitive_service_key>")
img = Img("/dbfs/mnt/forms", "medical_form.jpg")
mode = ImgToTextMode("HANDWRITTEN", True)


def retrieve_text_from_img(cogConfig, img, imgToTextMode):
    client = ComputerVisionClient(cogConfig.url, CognitiveServicesCredentials(cogConfig.key))
    
    with open(img.getFullPath(), "rb") as image_stream:
        txt_analysis = client.recognize_text_in_stream(image_stream, mode = imgToTextMode.mode, raw = imgToTextMode.isRaw)
    
    time.sleep(20)
    
    headers = {'Ocp-Apim-Subscription-Key':cogConfig.key}

    url = txt_analysis.response.headers['Operation-Location']

    return json.loads(requests.get(url, headers = headers).text)

words = retrieve_text_from_img(cogConfig, img, mode)


print(words)

