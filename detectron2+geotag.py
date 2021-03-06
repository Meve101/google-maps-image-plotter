

"""# Installing & importing """

!pip install pyyaml==5.1

import torch
TORCH_VERSION = ".".join(torch.__version__.split(".")[:2])
CUDA_VERSION = torch.__version__.split("+")[-1]
print("torch: ", TORCH_VERSION, "; cuda: ", CUDA_VERSION)
!pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/$CUDA_VERSION/torch$TORCH_VERSION/index.html
!pip install piexif
!pip install GPSPhoto
!pip install EXIF
!pip install exifread
!pip install gmplot
!pip install exif
!pip install Pillow
!pip install numpy
!pip install pandas
!pip install gmaps

# You may need to restart your runtime prior to this, to let your installation take effect
# Some basic setup
# Setup detectron2 logger
import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()

# import some common libraries
import matplotlib.pyplot as plt
import numpy as np
import cv2
from google.colab.patches import cv2_imshow
import os

# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog

#importing drive 
from google.colab import auth
auth.authenticate_user()
import gspread
from oauth2client.client import GoogleCredentials
gc = gspread.authorize(GoogleCredentials.get_application_default())

#checks for metadata in image list
import PIL
from PIL import Image
from PIL.ExifTags import TAGS
from PIL.ExifTags import GPSTAGS
import gmplot

from detectron2.engine import DefaultTrainer
from detectron2.config import get_cfg

"""**Mapping & plotting (all the pictures in library)**"""

#takes images from file in project if they are jpgs
image_dir = os.listdir('/content/drive/MyDrive/UAVVaste-main/UAVVaste-main/Test_fotos')
image_list = [a for a in image_dir if a.endswith('JPG')] # .jp werkt niet?
print(image_list)

coordinates_list = []

  #No metadata at all found
def get_geotagging(exif):
      if not exif:
          raise ValueError("No EXIF metadata found")
  #No geotagging at all found
      geotagging = {}
      for (idx, tag) in TAGS.items():
          if tag == 'GPSInfo':
              if idx not in exif:
                  raise ValueError("No EXIF geotagging found")

              for (key, val) in GPSTAGS.items():
                  if key in exif[idx]:
                      geotagging[val] = exif[idx][key]

      return geotagging
  
# path to the image or video and collects exifdata 
for a in range(len(image_list)):
  image_dir = '/content/drive/MyDrive/UAVVaste-main/UAVVaste-main/Test_fotos/' + image_list[a]
  # read the image data using PIL
  image = Image.open(image_dir)
  exifdata = image._getexif()
  geotags = get_geotagging(exifdata)
  
#converting from dms to decimal
  exif = image._getexif() 
  def get_decimal_from_dms(dms, ref):

    degrees = dms[0][0] / dms[0][1]
    minutes = dms[1][0] / dms[1][1] / 60.0
    seconds = dms[2][0] / dms[2][1] / 3600.0

    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds

    return round(degrees + minutes + seconds, 5)

  def get_coordinates(geotags):
    lat = get_decimal_from_dms(geotags['GPSLatitude'], geotags['GPSLatitudeRef'])
    lon = get_decimal_from_dms(geotags['GPSLongitude'], geotags['GPSLongitudeRef'])
    print(lat, lon)
    return(lat,lon) 
  #puts decimal coordinates into coordinates list
  decimal_coordinates = get_coordinates(get_geotagging(exif))
  coordinates_list.insert(0, decimal_coordinates)

apikey = 
gmap1 = gmplot.GoogleMapPlotter(0, 0 , 13, apikey = apikey)
# scatter points on the google map
for a in coordinates_list:
  lat = a[0]
  lon = a[1]
  gmap1.marker(lat, lon, 'blue', size = 40, marker = True )

# Pass the absolute path
gmap1.draw("/content/drive/MyDrive/UAVVaste-main/UAVVaste-main/test_plot.html")

"""**Defining the predictor function**"""

cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 2 
cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
# cfg.MODEL.WEIGHTS = os.path.join(cfg.OUTPUT_DIR, "model_final.pth")  # If the model was re-trained, save the weights and use this 
cfg.MODEL.WEIGHTS = "/content/drive/MyDrive/UAVVaste-main/UAVVaste-main/output/model_final.pth"
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.7   # set the testing threshold for this model
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 2
cfg.DATASETS.TEST = ("dataset_val", )
predictor = DefaultPredictor(cfg)

"""**Running the inference (+ showing on image)**"""

from detectron2.utils.visualizer import ColorMode
import random
im = cv2.imread('/content/drive/MyDrive/UAVVaste-main/UAVVaste-main/images/BATCH_d06_img_1390.jpg')
outputs = predictor(im)
print(outputs["instances"].pred_classes)
print(outputs["instances"].pred_boxes)

v = Visualizer(im[:, :, ::-1],
                   scale=0.8, 
                   instance_mode=ColorMode.IMAGE_BW   # remove the colors of unsegmented pixels
    )
v = v.draw_instance_predictions(outputs["instances"].to("cpu"))
cv2_imshow(v.get_image()[:, :, ::-1])

"""**Functions necessary for plotting on map**"""

def get_geotagging(exif):
      if not exif:
          raise ValueError("No EXIF metadata found")
  #No geotagging at all found
      geotagging = {}
      for (idx, tag) in TAGS.items():
          if tag == 'GPSInfo':
              if idx not in exif:
                  raise ValueError("No EXIF geotagging found")

              for (key, val) in GPSTAGS.items():
                  if key in exif[idx]:
                      geotagging[val] = exif[idx][key]

      return geotagging

def get_decimal_from_dms(dms, ref):

    degrees = dms[0][0] / dms[0][1]
    minutes = dms[1][0] / dms[1][1] / 60.0
    seconds = dms[2][0] / dms[2][1] / 3600.0

    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds

    return round(degrees + minutes + seconds, 5)

def get_coordinates(geotags):
    lat = get_decimal_from_dms(geotags['GPSLatitude'], geotags['GPSLatitudeRef'])
    lon = get_decimal_from_dms(geotags['GPSLongitude'], geotags['GPSLongitudeRef'])
    print(lat, lon)
    return(lat,lon)

"""**Adding images with trash**"""

image_dir = os.listdir('/content/drive/MyDrive/UAVVaste-main/UAVVaste-main/Test_fotos')
image_list = [a for a in image_dir if a.endswith('JPG')] # .jpg werkt niet?
print(image_list)

coordinates_list = []
apikey = "AIzaSyA7JvXONuenKF4ec46w4YLJDl5hQNgZIYg"
gmap1 = gmplot.GoogleMapPlotter(51.9, 4.4 , 13, apikey = apikey)

for a in range(len(image_list)):
  # Per image in image_list: Counting boxes
  im = cv2.imread('/content/drive/MyDrive/UAVVaste-main/UAVVaste-main/Test_fotos/' + image_list[a])
  outputs = predictor(im)
  boxes = len(outputs["instances"].pred_boxes)

  if boxes > 0:
    # Per image in image_list: Getting exifdata
    image_dir = '/content/drive/MyDrive/UAVVaste-main/UAVVaste-main/Test_fotos/' + image_list[a]
    image = Image.open(image_dir)
    exifdata = image._getexif()
    geotags = get_geotagging(exifdata)

    # Inserting the coordinates in coordinates_list
    exif = image._getexif() 
    decimal_coordinates = get_coordinates(get_geotagging(exif))
    coordinates_list.insert(0, decimal_coordinates)
  else:
    pass

"""**Plotting point on the map**"""

for a in coordinates_list:
  lat = a[0]
  lon = a[1]
  gmap1.marker(lat, lon, 'blue', size = 20, marker = True )

# Pass the absolute path
gmap1.draw("/content/drive/MyDrive/UAVVaste-main/UAVVaste-main/test_plot.html")
