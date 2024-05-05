import cv2
import numpy as np


class panorama:
    def __init__(self, video_path, frame_step, filter_enable, sharp_enable):
        self.video_path = video_path
        self.frame_step = frame_step
        self.filter_enable = filter_enable
        self.sharp_enable = sharp_enable
        self.frames = []
        self.load_video(frame_step)

    def load_video(self, frame_step):
        cap = cv2.VideoCapture(self.video_path)
        frame_index = 0
        success, frame = cap.read()
        while success:
            if frame_index % frame_step == 0:
                self.frames.append(frame)
            frame_index += 1
            success, frame = cap.read()
        cap.release()

    def apply_filter(self, image):
      
        if image.dtype != np.uint8:
            image = (np.clip(image, 0, 255)).astype(np.uint8)
        if self.filter_enable ==True :
            return cv2.GaussianBlur(image, (7, 7), 0)
        else:
            return image
    
    def sharp_filter(self,image):
        
        if self.sharp_enable:
            kernel = np.array([[-1, -1, -1],
                            [-1,  9, -1],
                            [-1, -1, -1]])
            # Apply the kernel to the frame using filter2D
            return cv2.filter2D(image, -1, kernel)
        else:

            return image


    def stitch_frames(self):
        stitcher = cv2.Stitcher_create()
        (status, stitched) = stitcher.stitch(self.frames)
        if status == cv2.Stitcher_OK:
            return stitched
        else:
            print("error: ", status)
            return None
        
    def crop_panorama(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
        
        top, left = 0, 0
        bottom, right = thresh.shape[0] - 1, thresh.shape[1] - 1

        continue_left = continue_right = continue_top = continue_bottom = True
        # Check that the borders are all white
        while continue_left or continue_right or continue_top or continue_bottom:
           
            if continue_left and np.any(thresh[top:bottom+1, left] == 0):
                left += 1
            else:
                continue_left = False
            
           
            if continue_right and np.any(thresh[top:bottom+1, right] == 0):
                right -= 1
            else:
                continue_right = False
            
            
            if continue_top and np.any(thresh[top, left:right+1] == 0):
                top += 1
            else:
                continue_top = False
            
            
            if continue_bottom and np.any(thresh[bottom, left:right+1] == 0):
                bottom -= 1
            else:
                continue_bottom = False

            # Keep the index within the valid range
            top = min(top, thresh.shape[0] - 1)
            bottom = max(bottom, 0)
            left = min(left, thresh.shape[1] - 1)
            right = max(right, 0)

        if right > left and bottom > top:
            cropped_image = image[top:bottom+1, left:right+1]
            return cropped_image
        else:
            print("No valid rectangle found")
            return image



    def create_panorama(self):

        stitched_panorama = self.stitch_frames()
     
        if stitched_panorama is not None:
            crop = self.crop_panorama(stitched_panorama)
            blur_panorama = self.apply_filter(crop)

            return self.sharp_filter(blur_panorama)
        else:
            return None


# # example usage
# video_path = 'video\Roma.mp4'
# panorama_creator = panorama(video_path,10,True,False)
# panorama_image = panorama_creator.create_panorama()
# if panorama_image is not None:
#     cv2.imshow('Cropped Panorama', panorama_image)
#     cv2.imwrite('Roma_blured.jpg', panorama_image)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
# else:
#     print("error")
