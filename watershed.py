import time
import cv2
import numpy as np
from IPython.display import Image, display
from matplotlib import pyplot as plt
from scipy.__config__ import show

image_path = "C:/Users/91826/Downloads/pic 4.jpg"
resize_factor = 0.2

# Plot the image
def imshow(img, ax=None):
    if ax is None:
        ret, encoded = cv2.imencode(".jpg", img)
        display(Image(encoded))
    else:
        ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        ax.axis('off')
 
def show_img(text, img):
    cv2.destroyAllWindows()
    cv2.imshow(text, img)
    cv2.waitKey(2000)

def show_plot():
    plt.show()
    # time.sleep(1)
    plt.pause(1)
    plt.close("all")

#Image loading
img = cv2.imread(image_path)
og_size = img.shape[:2]
img = cv2.resize(img, dsize=(int(og_size[1] * resize_factor), int(og_size[0] * resize_factor)))
show_img("coins colored", img)

# image grayscale conversion
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
show_img("coins greyscale", gray)

#Threshold Processing
ret, bin_img = cv2.threshold(gray,
                             0, 255, 
                             cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
show_img("threshold img", bin_img)

# noise removal
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
bin_img = cv2.morphologyEx(bin_img, 
                           cv2.MORPH_OPEN,
                           kernel,
                           iterations=2)
show_img("noise removal", bin_img)


# Create subplots with 1 row and 2 columns
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(8, 8))

# sure background area
sure_bg = cv2.dilate(bin_img, kernel, iterations=3)
imshow(sure_bg, axes[0, 0])
axes[0, 0].set_title('Sure Background')

# Distance transform
dist = cv2.distanceTransform(bin_img, cv2.DIST_L2, 5)
imshow(dist, axes[0, 1])
axes[0, 1].set_title('Distance Transform')

#foreground area
ret, sure_fg = cv2.threshold(dist, 0.5 * dist.max(), 255, cv2.THRESH_BINARY)
sure_fg = sure_fg.astype(np.uint8)  
imshow(sure_fg, axes[1, 0])
axes[1, 0].set_title('Sure Foreground')

# unknown area
unknown = cv2.subtract(sure_bg, sure_fg)
imshow(unknown, axes[1, 1])
axes[1, 1].set_title('Unknown')

show_plot()


# Marker labelling
# sure foreground 
ret, markers = cv2.connectedComponents(sure_fg)
 
# Add one to all labels so that background is not 0, but 1
markers += 1
# mark the region of unknown with zero
markers[unknown == 255] = 0
fig, ax = plt.subplots(figsize=(6, 6))
fig.suptitle("markers")
ax.imshow(markers, cmap="tab20b")
ax.axis('off')
show_plot()

# watershed Algorithm
markers = cv2.watershed(img, markers)
labels = np.unique(markers)
 
objs = []
for label in labels[2:]:  
 
# Create a binary image in which only the area of the label is in the foreground 
#and the rest of the image is in the background   
    target = np.where(markers == label, 255, 0).astype(np.uint8)
   
  # Perform contour extraction on the created binary image
    contours, hierarchy = cv2.findContours(
        target, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    objs.append(contours[0])
 
# Draw the outline
img = cv2.drawContours(img, objs, -1, color=(0, 23, 223), thickness=2)
show_img("drawn contours", img)