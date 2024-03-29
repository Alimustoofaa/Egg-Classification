import cv2
import time
import numpy as np
try:
	from config import SECOND_METODE
except:
	SECOND_METODE = True

# Config for Detection
IMAGE_HEIGHT, IMAGE_WIDTH = 416, 416
DET_MEDIAN_BLUR_1 = 11
DET_MEDIAN_BLUR_2 = 91
DET_THRESOLD = 40

IMAGE_FERTILE = cv2.imread('/home/pi/Projects/Egg-Detection/src/blured_fertile.jpg')
IMAGE_INFERTILE = cv2.imread('/home/pi/Projects/Egg-Detection/src/blured_infertile.jpg')
image_infertil =  cv2.imread('/home/pi/Projects/Egg-Detection/src/double/blured_infertile.jpg')
image_fertil = cv2.imread('/home/pi/Projects/Egg-Detection/src/double/blured_fertile_1.jpg')
image_fertil2 = cv2.imread('/home/pi/Projects/Egg-Detection/src/double/blured_fertile_2.jpg')
image_fertil3 = cv2.imread('/home/pi/Projects/Egg-Detection/src/double/blured_fertile_3.jpg')

def image_to_rgb(image):
	'''
		Change Image to RGB
	'''
	return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

def image_resize(image, w, h):
	'''
		Resize image
	'''
	return cv2.resize(
					image, 
					(w, h), 
					interpolation=cv2.INTER_AREA
				)

def image_median_blur(image, size_blur):
	'''
		Remove Noise
	'''
	return cv2.medianBlur(image, size_blur)

def image_to_gray(image):
	'''
		Change image RGB to Gray
	'''
	return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

def image_erocode(image):
	'''
		Image Erocode
	'''
	return cv2.erode(image, np.ones((5, 5), np.uint8))

def get_brightness(image):
    im = cv2.cvtColor(image, cv2.IMREAD_GRAYSCALE)
    # Calculate mean brightness as percentage
    meanpercent = np.mean(im) * 100 / 255
    low_condition = 50 if meanpercent < 34 else 150
    return low_condition

def morphological_trans(image_resize):
	frame = image_resize.copy()
	hsv = cv2.cvtColor(image_resize, cv2.COLOR_BGR2HSV)
	low_condition = get_brightness(image_resize)

	# lower_red = np.array([10,100,80])
	lower_red = np.array([50,100, low_condition])
	upper_red = np.array([250,255,255])

	mask = cv2.inRange(hsv, lower_red, upper_red)
	res = cv2.bitwise_and(frame,frame, mask= mask)

	kernel = np.ones((9,9),np.uint8)

	opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
	closing = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
	
	blur = cv2.medianBlur(closing, 55)
	
	return blur

def image_threshold(erode, thres):
	'''
		Thresolding image
	'''
	_, thresold = cv2.threshold(erode, thres, 255, cv2.THRESH_BINARY)
	return thresold

def get_contour_image(thresold):
	'''
		Get Contour image
	'''
	cnts, _ = cv2.findContours(thresold, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
	return cnts

def filter_contour(list_contour):
	'''
		Find max value and get on of max value contour
	'''
	len_contour = [len(i) for i in list_contour]
	print(len_contour)
	max_value = max(len_contour)
	idx = len_contour.index(max_value)
	max_contour = list_contour[idx]
	return max_contour

def draw_image(image, contour):
	return cv2.drawContours(image, contour, -1, (0,255,0), thickness = 10)

def change_background_to_white(image, thresold):
	# Change background
	kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
	morph = cv2.morphologyEx(thresold, cv2.MORPH_CLOSE, kernel)

	# Remove background using bitwise-and operation
	image = cv2.bitwise_and(image, image, mask=morph)
	image[thresold==0] = [255,255,255] # Turn background white
	return image

def crop_image_contour_bbox(image, contours, second_metode=False):
	if second_metode:
		gry = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		blur = cv2.GaussianBlur(gry,(3,3), 0)
		th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
		coords = cv2.findNonZero(th)
		x,y,w,h = cv2.boundingRect(coords)
		x_min, y_min, x_max, y_max = x, y, x+w, y+h
		image = image[y_min:y_max, x_min:x_max]
		return image, [x_min, y_min, x_max, y_max] 
	else:
		x, y, w, h = cv2.boundingRect(contours)
		x_min, y_min, x_max, y_max = x, y, x+w, y+h
		image = image[y_min:y_max, x_min:x_max]
		return image, [x_min, y_min, x_max, y_max]


# Config for Classification
CLASS_KERNEL_SIZE = 8
CLASS_SIG_COLOR = 15
CLASS_SIG_SPACE = 13
CLASS_CLIP_LIMIT = 136.0
CLASS_THRES  = 160
CLASS_MIN_CONTOUR = 10
CLASS_MAX_CONTOUR = 400
CLASS_IMAGE_WIDTH = 250
CLASS_IMAGE_HEIGH = 250
CLASS_MIN_AREA = 10

def image_bilateral(image_gray, kenel_size, sig_color, sig_space):
	'''
		Filtering bilateral
	'''
	return cv2.bilateralFilter(image_gray, kenel_size, sig_color, sig_space)

def object_clahe(image_blured_bil, clip_limit):
	'''
		create object contrast llimite adaptive histogram equalization
		to improve contast image
	'''
	clahe = cv2.createCLAHE(clipLimit=float(clip_limit), tileGridSize=(25, 25))
	cl1 = clahe.apply(image_blured_bil)
	cl1 = 255 - cl1
	return cl1

def image_thresold_tozero(cl1, thres):
	_, thresh = cv2.threshold(cl1, thres, 255, cv2.THRESH_TOZERO)
	return thresh

def image_morphology(thresh):
	current = np.copy(thresh)
	prev = np.copy(current)
	prev[:] = 0


	kernel3 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
	kernel5 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
	kernel7 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7))


	current = cv2.morphologyEx(current, cv2.MORPH_OPEN, kernel5)
	iter_num = 0
	max_iter = 100

	while np.sum(current - prev) > 0 and iter_num < max_iter:
		iter_num = iter_num+1
		prev = np.copy(current)
		current = cv2.dilate(current, kernel3)
		current[np.where(thresh == 0)] = 0
		
	return current

def filter_object_contour(current, image_bg_white, min_contour, max_contour):
	contours, _ = cv2.findContours(current, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	total_area = 0
	for contour in contours:
		area = cv2.contourArea(contour)
		if area > min_contour and area < max_contour:
			cv2.drawContours(image_bg_white, [contour], 0, [0,255,0], -1 )
			total_area+=1
	return total_area, image_bg_white

def compare_image(image_current):
	image_infertil=IMAGE_INFERTILE
	image_fertil=IMAGE_FERTILE
	image_infertil_g = cv2.cvtColor(image_infertil, cv2.COLOR_BGR2GRAY)
	image_fertil_g = cv2.cvtColor(image_fertil, cv2.COLOR_BGR2GRAY)
	image_current_g = cv2.cvtColor(image_current, cv2.COLOR_BGR2GRAY)

	image_infertil_h = cv2.calcHist([image_infertil_g], [0],
						 None, [256], [0, 256])
	image_fertil_h = cv2.calcHist([image_fertil_g], [0],
						 None, [256], [0, 256])
	image_current_h = cv2.calcHist([image_current_g], [0],
						 None, [256], [0, 256])

	c1, c2 = 0, 0

	# Euclidean Distance between data1 and test
	i = 0
	while i<len(image_current_h) and i<len(image_infertil_h):
		c1+=(image_current_h[i]-image_infertil_h[i])**2
		i+= 1
	c1 = c1**(1 / 2)


	# Euclidean Distance between data2 and test
	i = 0
	while i<len(image_current_h) and i<len(image_fertil_h):
		c2+=(image_current_h[i]-image_fertil_h[i])**2
		i+= 1
	c2 = c2**(1 / 2)

	if(c1<c2):
		return 200
	else:
		return 140

def compare_image_np(image_current):
	def calculate_euclidean_distance(hist1, hist2):
		return np.linalg.norm(hist1 - hist2)

	image_infertil_g = cv2.cvtColor(image_infertil, cv2.COLOR_BGR2GRAY)
	image_fertil_g = cv2.cvtColor(image_fertil, cv2.COLOR_BGR2GRAY)
	image_fertil2_g = cv2.cvtColor(image_fertil2, cv2.COLOR_BGR2GRAY)
	image_fertil3_g = cv2.cvtColor(image_fertil3, cv2.COLOR_BGR2GRAY)
	image_current_g = cv2.cvtColor(image_current, cv2.COLOR_BGR2GRAY)

	image_infertil_h = cv2.calcHist([image_infertil_g], [0], None, [256], [0, 256])
	image_fertil_h = cv2.calcHist([image_fertil_g], [0], None, [256], [0, 256])
	image_fertil2_h = cv2.calcHist([image_fertil2_g], [0], None, [256], [0, 256])
	image_fertil3_h = cv2.calcHist([image_fertil3_g], [0], None, [256], [0, 256])
	image_current_h = cv2.calcHist([image_current_g], [0], None, [256], [0, 256])

	distances = []

	# Calculate Euclidean Distance between image_infertil and image_current
	distance_infertil = calculate_euclidean_distance(image_infertil_h, image_current_h)
	distances.append(distance_infertil)

	# Calculate Euclidean Distance between image_fertil and image_current
	distance_fertil = calculate_euclidean_distance(image_fertil_h, image_current_h)
	distances.append(distance_fertil)

	# Calculate Euclidean Distance between image_fertil2 and image_current
	distance_fertil2 = calculate_euclidean_distance(image_fertil2_h, image_current_h)
	distances.append(distance_fertil2)

	# Calculate Euclidean Distance between image_fertil3 and image_current
	distance_fertil3 = calculate_euclidean_distance(image_fertil3_h, image_current_h)
	distances.append(distance_fertil3)

	min_distance = min(distances)

	if min_distance == distance_infertil:
		return 200
	elif min_distance == distance_fertil:
		return 140
	elif min_distance == distance_fertil2:
		return 140
	elif min_distance == distance_fertil3:
		return 140
    
def main_process(image=None):
	h, w  = image.shape[:2]
	# image = image[
	#     0:360, 0:w
	# ]
	cv2.imwrite(f'results/{int(time.time())}.jpg', image)
	# h,w = image.shape[:2]
	# change image to rgb
	image_rgb = image_to_rgb(image)
	# resize image
	image_resized = image_resize(image_rgb, IMAGE_WIDTH, IMAGE_HEIGHT)

	'''
		EGG DETECTION
		1. Image RGB
		2. image resize (416, 416)
		3. Median blur
		4. Image Grayscale
		5. Double remove noise
		6. Thresold Binary
		7. Find contours
		8. Change Background color to white
		9. Crop Image contours
	'''
	# blur 1 immage
	image_blur_1 = image_median_blur(image_resized, DET_MEDIAN_BLUR_1)
	# Change image to gray
	image_gray = image_to_gray(image_blur_1)

	# blur 2 image
	image_blur_2 = image_median_blur(image_gray, DET_MEDIAN_BLUR_2)
	image_erocoded = image_erocode(image_blur_2)

	# image_threshold
	image_thresolded = image_threshold(image_erocoded, DET_THRESOLD)

	# image contour
	image_contour_1 = get_contour_image(image_thresolded)

	# max contour 
	max_contour = filter_contour(image_contour_1)

	# image_morphology
	if SECOND_METODE:
		print('Crop Image')
		image_thresolded = morphological_trans(image_resized)
		cv2.imwrite('test.jpg', image_thresolded)
	# Visualize Image
	image_drawed = image_resized.copy()
	image_drawed = draw_image(image_drawed, max_contour)

	# Change background to white
	image_bg_white = image_resized.copy()
	image_bg_white = change_background_to_white(image_bg_white, image_thresolded)

	# Crop image contours
	image_cropped, bbox = crop_image_contour_bbox(image_bg_white, max_contour, SECOND_METODE)
	cv2.imwrite('test_bg.jpg', image_bg_white)
	'''
		EGG CLASSIFICATION
	'''
	# original shape 
	h_crop, w_crop = image_cropped.shape[:2]
	# resize_image
	try:	
		image_cropped_resize = image_resize(image_cropped,CLASS_IMAGE_WIDTH, CLASS_IMAGE_HEIGH)
	except:
		image_cropped_resize = 255 * np.ones((250,250,3), np.uint8)
		h_crop, w_crop = 250, 250
	# change image to gray
	image_gray_class = image_to_gray(image_cropped_resize)
	# blur image using bilateral
	image_blured_bil = image_bilateral(
										image_gray_class, 
										CLASS_KERNEL_SIZE, 
										CLASS_SIG_COLOR, 
										CLASS_SIG_SPACE
									)
	# improve image contrast using object clahe
	image_clahed = object_clahe(image_blured_bil, CLASS_CLIP_LIMIT)
	# compare image get val thresold
	image_blured_bil_com = cv2.cvtColor(image_blured_bil, cv2.COLOR_GRAY2BGR)
	thresold_val = compare_image_np(image_blured_bil_com)
	print(f'Value thresold : {thresold_val}')
	# thresolding image to zero
	image_thres_tozero = image_thresold_tozero(image_clahed, thresold_val)
	# image morphology
	image_morpho = image_morphology(image_thres_tozero)
	total_area, image_class_drawed = filter_object_contour(
											image_morpho, 
											image_cropped_resize,
											CLASS_MIN_CONTOUR, 
											CLASS_MAX_CONTOUR
										)
	print(f'Count area = {total_area}')
	classification = 'fertil' if total_area >= CLASS_MIN_AREA else 'infertil'
	image_class_drawed = image_resize(image_class_drawed, w_crop, h_crop)
	# image_class_drawed = draw_image(image_class_drawed, max_contour)
	# cv2.imwrite('crop.jpg', cv2.cvtColor(image_class_drawed, cv2.COLOR_BGR2RGB))
	# print(classification)
	image_class_drawed = cv2.cvtColor(image_class_drawed, cv2.COLOR_BGR2RGB)
	cv2.imwrite('fff.jpg', image_class_drawed)
	return image_class_drawed, classification
	
if __name__ == '__main__':
	image = cv2.imread('/home/pi/Projects/Egg-Detection/results/1689002131.jpg')
	print(main_process(image)[1])
