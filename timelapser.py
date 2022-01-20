import subprocess as sp
import argparse
import glob
import cv2
import os

TMP_DIR = ""
VIDS_PATH = ""
TL_LENGTH = ""
OUTPUT_PATH = ""
WIDTH_PX = 1920
HEIGHT_PX = 1080
OUTPUT_FRAME_RATE = 24
VID_EXT = ['mov', 'mp4', 'avi']

def get_vid_seconds_length(file):
     try:
          videocap = cv2.VideoCapture(file)
          seconds = round(videocap.get(cv2.CAP_PROP_FRAME_COUNT)/videocap.get(cv2.CAP_PROP_FPS))
          videocap.release()
          return seconds
     except:
          return 0
     
def get_vid_frames_length(file):
     try:
          videocap = cv2.VideoCapture(file)
          frames = videocap.get(cv2.CAP_PROP_FRAME_COUNT)
          videocap.release()
          return frames
     except:
         return 0
    
def path_to_filename(path):
     return path.split('.')[0].split('/')[len(path.split('/'))]
    
def ffmpeg_final_video():
     command = f"ffmpeg -r {OUTPUT_FRAME_RATE} -s {WIDTH_PX}x{HEIGHT_PX} -i {TMP_DIR}img_%05d.jpg \
          -vcodec libx264 -crf 15 -pix_fmt yuv420p {OUTPUT_PATH}"
     sp.run(command, shell=True)   
     
def prepare_dir(path):
     if not os.path.exists(path):
          os.mkdir(path)
     return path
     
def main():
     global videocap
     global TMP_DIR
     global VIDS_PATH
     global TL_LENGTH
     global OUTPUT_PATH
     global WIDTH_PX
     global HEIGHT_PX
     
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
     TMP_DIR = prepare_dir(args.output.split('.')[0] + "_tmp/")
     TOTAL_OUTPUT_FRAMES = int(TL_LENGTH) * OUTPUT_FRAME_RATE
     
     files = [os.path.join(VIDS_PATH, f) for f in os.listdir(VIDS_PATH) 
              if os.path.isfile(os.path.join(VIDS_PATH, f)) and f.split('.')[1].lower() in VID_EXT]
     files.sort()
     
     videocap = cv2.VideoCapture(files[0])
     WIDTH_PX  = int(videocap.get(cv2.CAP_PROP_FRAME_WIDTH))
     HEIGHT_PX = int(videocap.get(cv2.CAP_PROP_FRAME_HEIGHT)) 
     videocap.release()

     second_lengths = [get_vid_seconds_length(file) for file in files] 
     gross_seconds = sum(second_lengths)
     
     clip_frame_lengths = [(seconds / gross_seconds) * TOTAL_OUTPUT_FRAMES for seconds in second_lengths]
     
     print(f"Got {len(files)} files @ {WIDTH_PX}px x {HEIGHT_PX}px")
     print(f"Reducing {sum(second_lengths)} seconds to {TL_LENGTH} seconds.")
     
     last_output_id = 0
     for i in range(len(files)):
          frame_interval = clip_frame_lengths[i] / second_lengths[i]
          
          print(f"Producing {round(clip_frame_lengths[i])} frames for clip {i+1}.")
          command = "ffmpeg -i " + f'"{files[i]}"' + f" -r {frame_interval} -start_number {last_output_id+1}" \
               + f" {TMP_DIR}img_%05d.jpg"
          sp.run(command, shell=True)
          
          last_output_id = int(max(os.listdir(TMP_DIR)).split('.')[0].split('_')[1])
     
     ffmpeg_final_video()

if __name__ == '__main__':
     main()    