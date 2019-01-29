#!/usr/bin/env python3
'''
Demo of using TrackingCamera
to track camera input and print tracking data in terminal
the data and video are saved (`example_4.csv` and `example_4.mov`)
'''

## import camera
import threading
from lab.tracking import TrackingCamera
from lab.cnc import CNC

cnc=CNC()

def move_cnc(x, y):
    cnc.move_to(x-30,y-30,0)

def run_camera():
    ## create camera with configuration, and init with resources
    # will throw exception for errors (such as broken camera or non-existing input/config files, ...)
    camera_kwargs = {
        'input_source': 0,                    # camera id (0, 1,...) or input video file name (default is camera 0)
        'output_video': 'example_4.mp4',      # optional, save the output video file (`mp4` format only)
        'output_data': 'example_4.csv',       # optional, save the tracking data (to `.csv` files)
        'camera_settings': (1920, 1080, 30),  # optional (width, height, fps), (1920, 1080, 30) by default
        'tracking_config_file': 'stickers',   # optional, markers for tracking or motion
                                              #           '<name>' for builtin config or '<name>.config' for local file
        'marker_names': [],                   # optional, selected markers in tracking config (empty for all)
        'crop': True,                         # optional, if True (default) frame is cropped to near square, otherwise the full resolution is used
        'builtin_plot_mode': 'default',       # optional, 'none' for no plotting by lib
                                              #           'default' for plotting center, contour, etc, may add 'trace' for future
    }

    cnc.home()

    with TrackingCamera(**camera_kwargs) as camera:
        i = 0
        last_x = 0
        last_y = 0
        while camera.is_running:
            ## read and track frame
            # return frame number and frame of earliest tracking job completed
            # return None values if camera is busy or if read fails (also cause camera to stop)
            tracking_frame_no, tracking_frame = camera.read_track()

            ## write frames to output video file (optional)
            camera.write_frame_to_video(tracking_frame_no, tracking_frame)

            ## display frame
            camera.display_frame(tracking_frame_no, tracking_frame)

            ## print tracking info in terminal
            if tracking_frame_no is None:
                continue

            # get timestamp of the frame
            tracking_frame_ts = camera.get_timestamp_of_frame(tracking_frame_no)
            print("Frame #{}, {:.1f}ms".format(tracking_frame_no, tracking_frame_ts))
            # get markers data in the frame
            for marker_name, marker_data in camera.get_tracking_data_of_frame(tracking_frame_no):
                i += 1
                print("Marker name: {}".format(marker_name))
                # print the position of marker in pixels
                y, x = marker_data["position_pixel"]
                if i % 30 == 0:
                    if abs(y-last_y) > 5 and abs(x-last_x) > 5:
                        last_x = x
                        last_y = y
                        t = threading.Thread(target=move_cnc, args=(x,y,))
                        t.start()

                print("\tposition in pixels: ({}, {})".format(y, x))
                # or loop over the properties of each object
                #for data_key, data_val in marker_data.items():
                #    print("\t{}: {}".format(data_key, data_val))

## run in command line
if __name__ == "__main__":
    run_camera()
