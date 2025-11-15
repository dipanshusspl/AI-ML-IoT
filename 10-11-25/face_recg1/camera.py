import cv2
import datetime
import os 

saving_directory='media'
cam= cv2.VideoCapture(0) #here we put 0 to open the default camera, here we just created the camera
fourcc = cv2.VideoWriter_fourcc(*'XVID')
#here fourcc stands for four character code, it tells opencv which codec(video compression format to use)
#some codec are- MJPG, MP4V whose o/p file is .mp4
#al lare four characters and we always use *, and * is used to just unpack those four characters

out=None
#just a empty placeholder for video writer object
#videoWriter means something like that combines all the frames, i.e. images are being captured
#and combined to make videos

recording= False
#just a flag that keeps checking whether the current user is currently recording or not


print("Press 'r' = record/stop | 'c' = capture image | 'q' = quit")

while True:
    ret,frame=cam.read()   #ret is short form of return and it will tell us whether the camera successfully captured a frame or not
    #here the frame is actual image as NumPy array, basically it is the mage data in matrix of pixels
    #here ret and frame basically ask the camera that whether every frame is corrct or not
    #frame can be used for multiple things like to show image we do---> cv2.imshow("camera", frame)
    #to save image----> cv2.imwrite("photo.jpg", frame)
    #to make many images into a video using -----> out.write(frame)
    if not ret:
        print("Failed to grab frame.")
        break


    timestamp= datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #Fetches the current system date and time IN THE PARTICULAR FORMAT
    cv2.putText(frame, timestamp, (10,50),cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255),2)
    #frame we already viewed which is basically image in numPy array, 
    # timestamp is the text to be written on image(frame) which is current date-time as for now
    #(10, 50)---> the bottom-left position of text on screen
    #cv2.FONT_HERSHEY_SIMPLEX --->The font style used (OpenCV has a few built-in fonts)
    # 1 ---->text size or font size whatever we say
    #(255, 255, 255) ----->Text color in BGR format — here it’s white
    #2------> Thickness of the text outline (in pixels)

    #so basically this line draws a timestamp(with a particular design) on our video screen

    cv2.imshow("Camer feed", frame) ##to show live images at camera
    key= cv2.waitKey(1) & 0xFF
    #thisis basically waiting tome of key press which is 1 milli second, and if no
    #key pressed then it returns -1
    #if key is pressed it gives ASCII code of that character
    #& 0xFF ----> a small bitwise trick used to ensure compatibility on all the systems
    if key == ord('r'):
        if not recording:
            #if r pressed and not recording yet then make a file name and start to
            #transfer into the path, make the recording on 
            video_filename=datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".avi"
            video_path= os.path.join(saving_directory, video_filename)
            out=cv2.VideoWriter(video_path, fourcc, 20.0, (1280, 720))
            #here cv2.VideoWriter creates a video writer file with video path, forcc
            #here 20.0 is basically 20 frames per second
            #(1280, 720) means the resolution of the video
            recording=True
            print(f"🎥 Recording started: {video_path}")
        else:
            recording = False #stop the “recording” mode.
            out.release()  #properly close and save the .avi file
            out = None     #clear the variable (so it’s not accidentally reused).
            print("🛑 Recording stopped.")

     # 📸 Capture image
    elif key == ord('c'):
        image_filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"
        image_path = os.path.join(saving_directory, image_filename)
        cv2.imwrite(image_path, frame)
        #here we did imwrite to write image into a file
        print(f"📸 Image captured: {image_path}")

    # ❌ Quit program
    elif key == ord('q'):
        print("👋 Exiting...")
        break

# 🧹 Cleanup
cam.release()  #it safely closes everything. #Stops the webcam.
if out is not None: #Checks if a video was being recorded (out exists).
    out.release()  #and if it was recorded then used to close the video file properly

cv2.destroyAllWindows()    #Closes all OpenCV windows (the “Camera Feed” display).










