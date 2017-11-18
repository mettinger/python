import cv2
import numpy as np
img = cv2.imread('/Users/marke/Desktop/newOffice.jpg')

while False:
    img = cv2.resize(img, (1500,1000), interpolation=cv2.INTER_CUBIC)
    cv2.namedWindow("test")
    cv2.imshow("test", img)
    cv2.waitKey(2000)
    cv2.destroyAllWindows()
    cv2.waitKey(2000)
    
if True:
    img = cv2.resize(img, (900,1440), interpolation=cv2.INTER_CUBIC)
    print img.shape
    cv2.namedWindow("test", cv2.WND_PROP_FULLSCREEN)
    cv2.namedWindow(cv2.CALIBRATE_FORM_NAME, cv2.CV_WINDOW_NORMAL)
    cv2.setWindowProperty("test", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow("test", img)
    cv2.waitKey(2000)
    cv2.destroyAllWindows()