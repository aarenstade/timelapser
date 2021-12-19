import argparse
import subprocess as sp
import cv2
import os
import math

TMP_DIR = ""
VIDS_PATH = ""
TL_LENGTH = ""
OUTPUT_PATH = ""
WIDTH_PX = 1920
HEIGHT_PX = 1080
OUTPUT_FRAME_RATE = 24
VID_EXT = ['mov', 'mp4', 'avi']

def get_vid_length(path):
     try:
          video = cv2.VideoCapture(path)
          return round(video.get(cv2.CAP_PROP_FRAME_COUNT)/video.get(cv2.CAP_PROP_FPS))
     except:
          return 0
     
def main():
     global TMP_DIR
     global VIDS_PATH
     global TL_LENGTH
     global OUTPUT_PATH
     parser = argparse.ArgumentParser()
     parser.add_argument("videos", 
                         help="Absolute path to directory of video files.")
     parser.add_argument("length", 
                         help="Length of final timelapse in seconds.")
     parser.add_argument("output", 
                         help='Absolute path to directory to save timelapse.')
     args = parser.parse_args()
     VIDS_PATH = args.videos
     TL_LENGTH = args.length
     OUTPUT_PATH = args.output
     TMP_DIR = args.output.split('.')[0] + "_tmp/"
     TOTAL_OUTPUT_FRAMES = int(TL_LENGTH) * OUTPUT_FRAME_RATE
     
     # get files, lengths (seconds), and dimensions
     files = [os.path.join(VIDS_PATH, f) for f in os.listdir(VIDS_PATH) 
              if os.path.isfile(os.path.join(VIDS_PATH, f)) and f.split('.')[1].lower() in VID_EXT]
     lengths = [get_vid_length(p) for p in files]
     gross_length = sum(lengths)
     files.sort()
     print(f"Got {len(files)} Video Files")
     
     cap = cv2.VideoCapture(files[0])
     WIDTH_PX  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
     HEIGHT_PX = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
     print(f"{WIDTH_PX} x {HEIGHT_PX}px")

     if not os.path.exists(TMP_DIR):
          os.mkdir(TMP_DIR)
          
     frame_id = 0
     for i in range(len(files)):
          video = cv2.VideoCapture(files[i])
          num_frames = math.ceil((lengths[i]/gross_length) * TOTAL_OUTPUT_FRAMES)
          total_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
          frames = [n*(total_frames/num_frames) for n in range(num_frames)]
          print(f"Clip {i+1}/{len(files)} - Processing {num_frames} Frames - Total Frames {frame_id}/{TOTAL_OUTPUT_FRAMES} ")
          for frame in frames:
               video.set(cv2.CAP_PROP_POS_FRAMES, frame)
               res, frame_img = video.read()
               if res:
                    cv2.imwrite(os.path.join(TMP_DIR, f"{frame_id:05}.jpg"), frame_img)
                    frame_id +=1
          video.release()


     command = f"ffmpeg -r {OUTPUT_FRAME_RATE} -s {WIDTH_PX}x{HEIGHT_PX} -i {TMP_DIR}%05d.jpg \
          -vcodec libx264 -crf 15 -pix_fmt yuv420p {OUTPUT_PATH}"
     sp.run(command, shell=True)
     
     # os.remove(TMP_DIR)
     
if __name__ == '__main__':
     main()