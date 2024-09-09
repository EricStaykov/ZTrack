from __future__ import division
from Tkinter import *
from math import *
from numpy import *
from ttk import *
from scipy import stats
from time import clock
from datetime import datetime
from urllib2 import urlopen
import ImageTk, Image, cv, math, tkFileDialog, ImageDraw, os, csv, numpy, copy, random, tkFont, matplotlib.mlab as mlab, matplotlib.pyplot as plt, shutil, io, base64, Tkinter as tk

# Made by Eric Staykov, 2013.
# Please do not distribute without consent.
# Contact email: estay@bigpond.com

class AutoVivification(dict):

    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

class Controller(object):

    def __init__(self,master):
        self.master = master
        master.resizable(0,0)
        master.title("ZTrack")

        self.message_box = Label(master, text = "Message: ", foreground = "dark green")
        self.message_box.grid(columnspan = 3, sticky = "W", pady = 4, padx = 5)

        # logo init
        self.photo = ImageTk.PhotoImage(Image.open('logo.png'))
        self.can = Canvas(master, height = 256, width = 114)
        self.can.grid(row = 1, column = 2, rowspan = 7, pady = 4)
        self.can.create_image(57,128, image=self.photo)

        # icon init
        master.iconbitmap(default='icon.ico')

        # main GUI init        
        self.start_stop_button = Button(master, text = "Start", command = self.prep, state = "disabled")
        self.start_stop_button.grid(row = 1, column = 0, sticky = "W", pady = 4, ipadx = 18, padx = 5)
        
        self.turn_cam_on_off_button = Button(master, text = "Turn on", command = self.turn_on)
        self.turn_cam_on_off_button.grid(row = 1, column = 1, sticky = "W", pady = 4, ipadx = 16)

        self.fps_combo_select = Combobox(master, state = "readonly", width = 14, values = ["30 fps", "25 fps", "24 fps", "20 fps", "15 fps", "10 fps", "5 fps"])
        self.fps_combo_select.set("15 fps")
        self.fps_combo_select.grid(row = 2, column = 0, sticky = "W", pady = 4, padx = 5)
        self.fps_combo_select.bind('<<ComboboxSelected>>', self.fps_combo_report)
        
        self.roi_combo_select = Combobox(master, state = "readonly", width = 14, values = ["1920 x 1080 pix", "1280 x 720 pix", "800 x 600 pix", "640 x 480 pix", "320 x 240 pix"])
        self.roi_combo_select.set("1920 x 1080 pix")
        self.roi_combo_select.grid(row = 2, column = 1, sticky = "W", pady = 4)
        self.roi_combo_select.bind('<<ComboboxSelected>>', self.roi_combo_report)

        self.folder_name_entry = Button(master, text = "Select Folder", command = self.select_folder)
        self.folder_name_entry.grid(row = 3, column = 0, sticky = "W", pady = 4, ipadx = 17, padx = 5)
        
        self.norm_thresh_cont_button = Button(master, text = "Display Threshold", command = self.from_normal_to_threshold)
        self.norm_thresh_cont_button.grid(row = 3, column = 1, sticky = "W", pady = 4, ipadx = 2)

        self.clear_hall = Button(master, text = "Clear All and Reset", command = self.clear_all)
        self.clear_hall.grid(row = 4, column = 0, sticky = "W", ipadx = 2, pady = 4, padx = 5)
        
        self.select_apply_roi = Button(master, text = "Select ROI", command = self.select_roi)
        self.select_apply_roi.grid(row = 4, column = 1, sticky = "W", pady = 4, ipadx = 16)

        self.set_scale_button = Button(master, text = "Set Scale", command = self.set_scale)
        self.set_scale_button.grid(row = 5, column = 0, sticky = "W", pady = 4, ipadx = 18, padx = 5)
        
        self.input_scale = Entry(master, width = 17)
        self.input_scale.grid(row = 5, column = 1, sticky = "W", pady = 4)
        self.input_scale.insert(END, "Scale Value")
        
        self.scale_label = Label(master, text = 'mm')
        self.scale_label.grid(row = 5, column = 1, sticky = "E", padx = 25, pady = 4)
        
        self.start_stop_next_phase_button = Button(master, text = "Start Next Phase (1)", command = self.start_next_phase, state = "disabled")
        self.start_stop_next_phase_button.grid(row = 6, column = 0, sticky = "W", pady = 4, padx = 5)
        
        self.input_time = Entry(master, width = 17)
        self.input_time.grid(row = 6, column = 1, sticky = "W", pady = 4)
        self.input_time.insert(END, "Phase Time")
        
        self.time_label = Label(master, text = 'sec')
        self.time_label.grid(row = 6, column = 1, sticky = "E", padx = 30, pady = 4)
        
        self.start_stop_analysis = Button(master, text = "Start Analysis", command = self.start_analysis, state = "disabled")
        self.start_stop_analysis.grid(row = 7, column = 0, sticky = "W", pady = 4, padx = 5, ipadx = 16)
        
        self.fps = Label(master, text = "Not Recording")
        self.fps.grid(row = 7, column = 1, sticky = "W", pady = 4)

        self.sizebar = Scale(master, command = self.adjust_slider_passive, orient = HORIZONTAL, to = 0, length = 500)
        self.sizebar.grid(columnspan=3)
        self.sizebar_reporter = Label(master, text = "ROI Slider")
        self.sizebar_reporter.grid(columnspan=3)        
        self.adaptive_slider = Scale(master, command = self.adjust_adaptive_slider, orient = HORIZONTAL, from_ = 3, to = 99, length = 500)
        self.adaptive_slider.grid(columnspan=3)
        self.adaptive_slider_reporter = Label(master, text = "Adaptive Value = 11")
        self.adaptive_slider_reporter.grid(columnspan=3)
        self.adaptive_slider.set(11)        
        self.minimum_cont_area_slider = Scale(master, command = self.adjust_minimum_cont_area, orient = HORIZONTAL, to = 250, length = 500)
        self.minimum_cont_area_slider.grid(columnspan=3)
        self.minimum_cont_area_slider_reporter = Label(master, text = "Minimum Area = 0")
        self.minimum_cont_area_slider_reporter.grid(columnspan=3)
        self.minimum_scoot_velocity_slider = Scale(master, command = self.adjust_minimum_scoot_velocity, orient = HORIZONTAL, to = 3000, length = 500)
        self.minimum_scoot_velocity_slider.grid(columnspan=3)
        self.minimum_scoot_velocity_slider_reporter = Label(master, text = "Minimum Scoot Velocity = 2.50 mm/sec")
        self.minimum_scoot_velocity_slider_reporter.grid(columnspan=3)
        self.minimum_scoot_velocity_slider.set(250)
        self.minimum_scoot_duration_slider = Scale(master, command = self.adjust_minimum_scoot_duration, orient = HORIZONTAL, to = 500, length = 500)
        self.minimum_scoot_duration_slider.grid(columnspan=3)
        self.minimum_scoot_duration_slider_reporter = Label(master, text = "Minimum Scoot Duration = 0.15 sec")
        self.minimum_scoot_duration_slider_reporter.grid(columnspan=3)
        self.minimum_scoot_duration_slider.set(15)
        self.minimum_scoot_distance_slider = Scale(master, command = self.adjust_minimum_scoot_distance, orient = HORIZONTAL, to = 2000, length = 500)
        self.minimum_scoot_distance_slider.grid(columnspan=3)
        self.minimum_scoot_distance_slider_reporter = Label(master, text = "Minimum Scoot Distance = 0.50 mm")
        self.minimum_scoot_distance_slider_reporter.grid(columnspan=3)
        self.minimum_scoot_distance_slider.set(50)
        self.maximum_scoot_distance_slider = Scale(master, command = self.adjust_maximum_scoot_distance, orient = HORIZONTAL, to = 2000, length = 500)
        self.maximum_scoot_distance_slider.grid(columnspan=3)
        self.maximum_scoot_distance_slider_reporter = Label(master, text = "Maximum Scoot Distance = 3.50 mm")
        self.maximum_scoot_distance_slider_reporter.grid(columnspan=3)
        self.maximum_scoot_distance_slider.set(350)
        self.playback_trackbar = Scale(master, command = self.playback_bar_blank, orient = HORIZONTAL, to = 0, length = 500)
        self.playback_trackbar.grid(columnspan=3)
        self.playback_trackbar_reporter = Label(master, text = "Playback Slider")
        self.playback_trackbar_reporter.grid(columnspan=3)

        self.menubar = Menu(master)       
        self.file_menu = Menu(self.menubar, tearoff = 0)
        self.file_menu.add_command(label = "Import XY Coordinates", command = self.import_xy_coords)
        self.file_menu.add_command(label = "Exit", command = master.destroy)
        self.menubar.add_cascade(label = "File", menu = self.file_menu)               
        master.config(menu = self.menubar)

        self.tk_loop_needed = None
        self.checkpoint = False
        self.capture = None
        self.counta = None
        self.start_time = None
        self.showing_normal = True
        self.showing_threshold = False
        self.showing_contours = False

        self.adaptive_value = 11
        self.minimum_contour_area = 0
        self.outer_roi_x = 1920
        self.outer_roi_y = 1080
        self.inner_roi = 0
        # min_velocity = 30.00 max, slider 3000 max, division by 10, 2.50 default, mm/sec, 2 dp
        # min_duration = 5.00 max, slider 500 max, division by 100, 0.15 default, sec, 2 dp
        # min_distance = 20.00 max, slider 2000 max, division by 100, 0.50 default, mm, 2 dp
        # max_distance = 20.00 max, slider 2000 max, division by 100, 3.50 default, mm, 2 dp
        self.minimum_scoot_velocity = 2.50
        self.minimum_scoot_duration = 0.15
        self.minimum_scoot_distance = 0.50
        self.maximum_scoot_distance = 3.50

        self.scale_calibrate = False
        self.scale_mm_per_pixel = None
        self.phase_number = 1
        self.current_recording_frame_number = 1
        self.phase_start_time = None
        self.phase_time_total = None
        self.recording_now = False
        self.positional_data = AutoVivification()
        # Description for self.positional_data: contains the coordinates for each contour during the session.
        # self.positional_data[x] = phase number x
        # self.positional_data[x][0] = information tuple for the phase x: (outer roi x, outer roi y, inner roi percentage of smallest outer roi dimension, scale in mm/pix, phase time in sec)
        # self.positional_data[x][n] = tuple for frame n of phase x: (time in seconds since start of phase, [list of ellipse information tuples for each point identified])
        # self.positional_data[x][n][1][m] = ellipse information tuple m of frame n of phase x (centre, radius, angle)
        self.fish_positions = AutoVivification()
        # Description for self.fish_positions: contains the coordinates for each fish during the session.
        # self.fish_positions[x] = phase number x
        # self.fish_positions[x][0] = information tuple for the phase: (outer roi x, outer roi y, inner roi percentage of smallest outer roi dimension, scale in mm/pix, phase time in sec, mode number of points)
        # self.fish_positions[x][n][0] = the time in seconds since the beginning of phase x
        # self.fish_positions[x][n][m] = the xy coordinates tuple for fish m of frame n of phase x
        self.fish_scoots = AutoVivification()
        # Description for self.fish_scoots: contains the scoot distances for each fish during the session and their duration, start time and whether they were inside or outside of the inner ROI
        # self.fish_scoots[x] = phase number x
        # self.fish_scoots[x][0] = information tuple for the phase: (outer roi x, outer roi y, inner roi percentage of smallest outer roi dimension, scale in mm/pix, phase time in sec, mode number of points)
        # self.fish_scoots[x][n] = dictionary access for fish n of phase x
        # self.fish_scoots[x][n][m] = scoot number m of fish n of phase x - tuple containing (start frame, end frame, scoot distance, duration of scoot in seconds, whether inside inner ROI)
        self.backup = None
        self.selected_folder = None
        self.folder_name = None
        self.folder_name_small = None
        self.current_video_file = None
        self.video_x = None
        self.video_y = None
        self.base_framerate = 15
        self.base_width = 1920
        self.base_height = 1080
        self.changing_x = False
        self.changing_y = False
        self.framerates = {}

        self.doing_initial = False
        self.doing_initialising_analysis = False
        self.doing_assigning_points_to_larvae = False
        self.doing_saving_excel_fish_positions = False
        self.doing_calculating_scoot_distances = False
        self.doing_saving_excel_scoot_distances_mixed = False
        self.doing_saving_excel_scoot_distances_inner_roi = False
        self.doing_initiating_playback = False
        self.doing_producing_graphs_distance_time = False
        self.doing_producing_graphs_distance_scoot_no = False
        self.doing_producing_path_composites = False
        self.doing_producing_scoot_parameters = False

        self.jabba = None
        self.poppy = None
        self.nabba = False
        self.analysis_timer = None

    def turn_on(self):
        cv.NamedWindow("ZTrack", 1)
        self.capture = cv.CaptureFromCAM(0)
        cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FPS, self.base_framerate)
        cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_WIDTH, self.base_width)
        cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_HEIGHT, self.base_height)
        self.turn_cam_on_off_button.config(text = "Turn off", command = self.turn_off)
        self.start_stop_button.config(state = "normal")
        self.start_stop_next_phase_button.config(state = "normal")
        self.prep()

    def turn_off(self):
        self.stop(True)
        cv.DestroyWindow("ZTrack")
        self.turn_cam_on_off_button.config(text = "Turn on", command = self.turn_on)
        self.start_stop_button.config(state = "disabled")
        self.start_stop_next_phase_button.config(state = "disabled")

    def prep(self):
        self.start_stop_button.config(text = "Stop", command = self.stop)
        self.counta = 1
        self.start_time = clock()
        self.start()

    def start(self):
        if not self.checkpoint:
            frameImg = cv.QueryFrame(self.capture)
            cv.SetImageROI(frameImg, (int((self.base_width/2)-(self.outer_roi_x/2)),int((self.base_height/2)-(self.outer_roi_y/2)),int(self.outer_roi_x),int(self.outer_roi_y)))
            frame_size = cv.GetSize(frameImg)

            if self.counta == 10:
                self.counta = 1
                frames = 10/(clock() - self.start_time)
                self.fps.config(text = "{0:.2f} fps".format(frames))
                self.start_time = clock()
            else:
                self.counta += 1

            if self.recording_now:
                time_left = self.phase_time_total - (clock() - self.phase_start_time)
                if time_left <= 0:
                    self.message_box.config(text = "Message: Finished recording phase {0}.".format(self.phase_number), foreground = "dark green")
                    self.input_time.delete(0, END)
                    self.input_time.insert(END, str(int(self.phase_time_total)))
                    self.recording_now = False
                    self.phase_number += 1
                    self.start_stop_next_phase_button.config(text = "Start Next Phase ({0})".format(self.phase_number), command = self.start_next_phase)
                    self.start_stop_next_phase_button.grid(ipadx = 0)
                    self.start_stop_analysis.config(state = "normal")
                    self.select_apply_roi.config(state = "normal")
                    self.roi_combo_select.config(state = "readonly")
                    self.fps_combo_select.config(state = "readonly")                    
                    self.current_recording_frame_number = 1

                    self.current_video_file = None
                    if self.phase_number == 2:
                        os.makedirs((self.folder_name + "/xy_data"))
                    xy_data_excel = open(self.folder_name + "/xy_data/" + "xy_data " + self.folder_name_small + " P" + str(self.phase_number - 1) + " " + str(self.phase_time_total) + " sec" + ".csv", "wb")
                    xy_writer = csv.writer(xy_data_excel, quoting=csv.QUOTE_MINIMAL)
                    xy_writer.writerow([''] + ['Time (sec)'])
                    for n in self.positional_data[(int(self.phase_number-1))]:
                        if n != 0:
                            x_temp_list = ["X", self.positional_data[(int(self.phase_number-1))][n][0]] + [zero[0][0] for zero in self.positional_data[(int(self.phase_number-1))][n][1]]
                            y_temp_list = ["Y", ""] + [zero[0][1] for zero in self.positional_data[(int(self.phase_number-1))][n][1]]
                            xy_writer.writerow(x_temp_list)
                            xy_writer.writerow(y_temp_list)
                    xy_data_excel.close()

                    self.stop()
                    self.playback_trackbar.config(command = self.playback_after_phase, from_ = 1, to = int(len(self.positional_data[(int(self.phase_number-1))]))-1) # Note: -1 at end because 0 is the frame information
                    self.playback_trackbar.set(1)
                    return
                self.input_time.delete(0, END)
                self.input_time.insert(END, "{0:.2f}".format(time_left))
                self.positional_data[self.phase_number][self.current_recording_frame_number] = ((clock() - self.phase_start_time),[])
            
            blacknwhite = cv.CreateImage(frame_size, cv.IPL_DEPTH_8U, 1)
            smoothed = cv.CreateImage(frame_size, cv.IPL_DEPTH_8U, 1)
            after_threshold = cv.CreateImage(frame_size, cv.IPL_DEPTH_8U, 1)
            before_contours = cv.CreateImage(frame_size, cv.IPL_DEPTH_8U, 1)
            cv.CvtColor(frameImg, blacknwhite, cv.CV_RGB2GRAY)
            cv.Smooth(blacknwhite, smoothed, smoothtype=cv.CV_BLUR, param1=5, param2=0, param3=0, param4=0)
            cv.AdaptiveThreshold(smoothed, after_threshold, 255, adaptive_method=cv.CV_ADAPTIVE_THRESH_MEAN_C, thresholdType=cv.CV_THRESH_BINARY, blockSize=self.adaptive_value, param1=self.adaptive_value)           
            # adpative: appears that if increase block and param, get less noise
            # smooth: blur seems to work best
            # smooth: param1 = 3 gives large larvae, param1 = 5 gives less noise and more circular larvae because no tail (more useful?)
            cv.Copy(after_threshold, before_contours, mask=None)
            
            hello_contours = 0
            contours = cv.FindContours(before_contours, cv.CreateMemStorage(), mode=cv.CV_RETR_TREE, method=cv.CV_CHAIN_APPROX_NONE, offset=(0,0))
            try_it = None                    
            try_it = contours.v_next()
            if not try_it:
                while not try_it:
                    if contours:
                        contours = contours.h_next()
                    if contours:
                        try_it = contours.v_next()
                    hello_contours += 1
                    if hello_contours > 10:
                        break
            contours = try_it
            while contours:
                if len(contours) >= 5:
                    if cv.ContourArea(contours) >= self.minimum_contour_area:
                        PointArray2D32f = cv.CreateMat(1, len(contours), cv.CV_32FC2)
                        for (i, (x, y)) in enumerate(contours):
                            PointArray2D32f[0, i] = (x, y)
                        centre, radius, angle = cv.FitEllipse2(PointArray2D32f) # centre is the centre of the circle
                        cv.Circle(img=before_contours, center=(int(centre[0]),int(centre[1])), radius=1, color=(255), thickness=-1, lineType=8, shift=0)
                        if self.recording_now:
                            self.positional_data[self.phase_number][self.current_recording_frame_number][1].append((centre, radius, angle))
                contours = contours.h_next()

            if frame_size[0] <= frame_size[1]:
                take_in = int((self.inner_roi/200)*frame_size[0])
            else:
                take_in = int((self.inner_roi/200)*frame_size[1])
            inner_roi_points = (take_in, take_in, frame_size[0] - take_in, frame_size[1] - take_in)

            if self.showing_normal:
                cv.Rectangle(frameImg, (inner_roi_points[0], inner_roi_points[1]), (inner_roi_points[2], inner_roi_points[3]), (255,108,33), thickness=2, lineType=8, shift=0)
                if self.scale_calibrate:
                    if not self.recording_now:
                        cv.Rectangle(frameImg, (int(frame_size[0]/2 - 300),int(frame_size[1]/2)), (int(frame_size[0]/2 + 300),int(frame_size[1]/2)), (113,179,60), thickness=2, lineType=8, shift=0)
                cv.ShowImage("ZTrack", frameImg)
            elif self.showing_threshold:
                cv.Rectangle(after_threshold, (inner_roi_points[0], inner_roi_points[1]), (inner_roi_points[2], inner_roi_points[3]), (0), thickness=2, lineType=8, shift=0)
                if self.scale_calibrate:
                    if not self.recording_now:
                        cv.Rectangle(after_threshold, (int(frame_size[0]/2 - 300),int(frame_size[1]/2)), (int(frame_size[0]/2 + 300),int(frame_size[1]/2)), (0), thickness=2, lineType=8, shift=0)                
                cv.ShowImage("ZTrack", after_threshold)
            elif self.showing_contours:
                cv.Rectangle(before_contours, (inner_roi_points[0], inner_roi_points[1]), (inner_roi_points[2], inner_roi_points[3]), (255), thickness=2, lineType=8, shift=0)
                if self.scale_calibrate:
                    if not self.recording_now:
                        cv.Rectangle(before_contours, (int(frame_size[0]/2 - 300),int(frame_size[1]/2)), (int(frame_size[0]/2 + 300),int(frame_size[1]/2)), (255), thickness=2, lineType=8, shift=0)
                cv.ShowImage("ZTrack", before_contours)

            if self.recording_now:
                self.current_recording_frame_number += 1
            if self.current_video_file:
                if not self.showing_normal:
                    cv.Rectangle(frameImg, (inner_roi_points[0], inner_roi_points[1]), (inner_roi_points[2], inner_roi_points[3]), (255,108,33), thickness=2, lineType=8, shift=0)
                resized_frame_for_video = cv.CreateImage((self.video_x,self.video_y), cv.IPL_DEPTH_8U, 3)
                cv.Resize(frameImg, resized_frame_for_video, cv.CV_INTER_LINEAR)
                cv.WriteFrame(self.current_video_file, resized_frame_for_video)

            cv.WaitKey(1)           
            self.tk_loop_needed = self.master.after(1, self.start)
        else:
            self.stop()
    
    def stop(self, value = None):
        self.checkpoint = True
        if self.tk_loop_needed is not None:
            self.master.after_cancel(self.tk_loop_needed)
            self.tk_loop_needed = None
            self.checkpoint = False
            self.start_stop_button.config(text = "Start", command = self.prep)
            self.fps.config(text = "Not Recording")
        elif value is not None:
            self.tk_loop_needed = None
            self.checkpoint = False
            self.start_stop_button.config(text = "Start", command = self.prep)
            self.fps.config(text = "Not Recording")            

    def from_normal_to_threshold(self):
        self.norm_thresh_cont_button.config(text = "Display Contours", command = self.from_threshold_to_contours)
        self.norm_thresh_cont_button.grid(ipadx = 4)
        self.showing_normal = False
        self.showing_threshold = True
        self.showing_contours = False

    def from_threshold_to_contours(self):
        self.norm_thresh_cont_button.config(text = "Display Normal", command = self.from_contours_to_normal)
        self.norm_thresh_cont_button.grid(ipadx = 9)
        self.showing_normal = False
        self.showing_threshold = False
        self.showing_contours = True

    def from_contours_to_normal(self):
        self.norm_thresh_cont_button.config(text = "Display Threshold", command = self.from_normal_to_threshold)
        self.norm_thresh_cont_button.grid(ipadx = 2)
        self.showing_normal = True
        self.showing_threshold = False
        self.showing_contours = False

    def select_roi(self):
        self.select_apply_roi.config(text = "Outer ROI X", command = self.apply_outer_roi_x)
        self.sizebar.config(command = self.adjust_outer_roi_x_with_slider, to = self.base_width)
        self.sizebar.set(self.outer_roi_x)
        self.changing_x = True

    def apply_outer_roi_x(self):
        self.select_apply_roi.config(text = "Outer ROI Y", command = self.apply_outer_roi_y)
        self.sizebar.config(command = self.adjust_outer_roi_y_with_slider, to = self.base_height)
        self.sizebar.set(self.outer_roi_y)
        self.changing_x = False
        self.changing_y = True

    def apply_outer_roi_y(self):
        self.select_apply_roi.config(text = "Inner ROI", command = self.apply_inner_roi)
        self.sizebar.config(command = self.adjust_inner_roi_with_slider, to = 100)
        self.sizebar.set(self.inner_roi)
        self.changing_y = False
    
    def apply_inner_roi(self):
        self.select_apply_roi.config(text = "Select ROI", command = self.select_roi)
        self.sizebar.config(command = self.adjust_slider_passive, to = 0)
        self.sizebar_reporter.config(text = "ROI Slider")

    def adjust_slider_passive(self, value):
        pass

    def adjust_outer_roi_x_with_slider(self, value):
        self.outer_roi_x = int(float(value))
        self.sizebar_reporter.config(text = "{0} pixels".format(str(int(float(value)))))

    def adjust_outer_roi_y_with_slider(self, value):
        self.outer_roi_y = int(float(value))
        self.sizebar_reporter.config(text = "{0} pixels".format(str(int(float(value)))))

    def adjust_inner_roi_with_slider(self, value):
        self.inner_roi = int(float(value))
        self.sizebar_reporter.config(text = "{0} percent".format(str(int(float(value)))))

    def start_next_phase(self):
        try:
            float(self.input_scale.get())
            if float(self.input_scale.get()) <= 0:
                self.message_box.config(text = "Message: Please input a number larger than zero into the scale box.", foreground = "dark green")
                return
        except Exception:
            self.message_box.config(text = "Message: Please input a valid number into the scale box.", foreground = "dark green")
            return
        try:
            int(float(self.input_time.get()))
            if int(float(self.input_time.get())) <= 0:
                self.message_box.config(text = "Message: Please input a number larger than zero into the phase time box.", foreground = "dark green")
                return
        except Exception:
            self.message_box.config(text = "Message: Please input a valid number into the phase time box.", foreground = "dark green")
            return        
        if self.phase_number == 1:
            to_convert = (str(os.path.expanduser('~/Desktop'))).split("\\")
            converted = ""
            for n in to_convert:
                converted += n + "/"
            converted = converted[0:-1]
            if self.selected_folder == converted:
                self.message_box.config(text = "Message: Please create and/or select a folder within the desktop or elsewhere.", foreground = "dark green")
                return
            if not self.selected_folder:
                self.message_box.config(text = "Message: Please select a folder then try again.", foreground = "dark green")
                return
            to_convert = (str(datetime.now())[0:-7]).split(":")
            converted = ""
            for n in to_convert:
                converted += n + "-"
            datentime = converted[0:-1]
            self.folder_name = self.selected_folder + "/ZTrack " + datentime
            self.folder_name_small = "ZTrack " + datentime
            os.makedirs(self.folder_name)
            os.makedirs((self.folder_name + "/settings"))
            os.makedirs((self.folder_name + "/raw_video"))
            self.folder_name_entry.config(state = "disabled")
        self.message_box.config(text = "Message: ", foreground = "dark green")
        if self.backup:
            self.positional_data = None
            self.positional_data = AutoVivification()
            self.positional_data = copy.deepcopy(self.backup)
            self.backup = None
        self.playback_trackbar.config(command = self.playback_bar_blank, from_ = 0, to = 0)
        self.playback_trackbar_reporter.config(text = "Playback Slider")
        self.start_stop_next_phase_button.config(text = "Stop Phase", command = self.stop_next_phase)
        self.start_stop_next_phase_button.grid(ipadx = 18)
        self.start_stop_analysis.config(state = "disabled")
        self.select_apply_roi.config(state = "disabled")
        self.roi_combo_select.config(state = "disabled")
        self.fps_combo_select.config(state = "disabled")        
        self.phase_time_total = int(float(self.input_time.get()))
        self.recording_now = True
        self.current_recording_frame_number = 1
        self.scale_mm_per_pixel = (float(self.input_scale.get()))/600 # 600 because the calibration bar is 600 pixels long
        self.positional_data[self.phase_number][0] = (self.outer_roi_x, self.outer_roi_y, self.inner_roi, self.scale_mm_per_pixel, self.phase_time_total)
        recording_settings = open(self.folder_name + "/settings/" + "settings " + self.folder_name_small + " P" + str(self.phase_number) + " " + str(self.phase_time_total) + " sec" + ".txt", "w")
        recording_settings.write("Adaptive value = " + str(self.adaptive_value) + "\n")
        recording_settings.write("Minimum contour area = " + str(self.minimum_contour_area) + " pixels^2\n")
        recording_settings.write("Scale input value = " + str((float(self.input_scale.get()))) + "\n")
        recording_settings.write("Scale = " + str(self.scale_mm_per_pixel) + " mm/pixel\n")
        recording_settings.write("Base resolution = " + str(self.base_width) + " x " + str(self.base_height) + " pixels\n")
        recording_settings.write("Outer ROI X = " + str(self.outer_roi_x) + " pixels\n")
        recording_settings.write("Outer ROI Y = " + str(self.outer_roi_y) + " pixels\n")
        recording_settings.write("Inner ROI = " + str(self.inner_roi) + "%\n")
        recording_settings.write("Session start time = " + str(datetime.now()) + "\n")
        recording_settings.write("Phase time = " + str(self.phase_time_total) + " seconds\n")
        recording_settings.write("Frame rate = " + str(int(cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FPS))) + "\n")   
        recording_settings.write("Brightness = " + str(cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_BRIGHTNESS)) + "\n")  
        recording_settings.write("Contrast = " + str(cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_CONTRAST)) + "\n")  
        recording_settings.write("Saturation = " + str(cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_SATURATION)) + "\n")  
        recording_settings.write("Exposure = " + str(cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_EXPOSURE)))
        recording_settings.close()
        self.video_x = int((90000*(self.outer_roi_x/self.outer_roi_y))**0.5)
        self.video_y = int((90000/(self.outer_roi_x/self.outer_roi_y))**0.5)
        self.framerates[self.phase_number] = self.base_framerate
        self.current_video_file = cv.CreateVideoWriter(self.folder_name + "/raw_video/" + "raw_video " + self.folder_name_small + " P" + str(self.phase_number) + " " + str(self.phase_time_total) + " sec" + ".avi", 1, self.base_framerate, (self.video_x, self.video_y), 1)
        cv.QueryFrame(self.capture)
        self.phase_start_time = clock() # this needs to be as close to the start of recording as possible
        self.checkpoint = False
        if not self.tk_loop_needed:
            self.prep()

    def stop_next_phase(self):
        self.start_stop_next_phase_button.config(text = "Start Next Phase ({0})".format(self.phase_number), command = self.start_next_phase)
        self.start_stop_next_phase_button.grid(ipadx = 0)
        self.input_time.delete(0, END)
        self.input_time.insert(END, str(int(self.phase_time_total)))
        self.recording_now = False
        self.current_recording_frame_number = 1
        self.positional_data.pop(self.phase_number)
        if self.phase_number > 1:
            self.start_stop_analysis.config(state = "normal")
            self.current_video_file = None
            os.remove(self.folder_name + "/raw_video/" + "raw_video " + self.folder_name_small + " P" + str(self.phase_number) + " " + str(self.phase_time_total) + " sec" + ".avi")
            os.remove(self.folder_name + "/settings/" + "settings " + self.folder_name_small + " P" + str(self.phase_number) + " " + str(self.phase_time_total) + " sec" + ".txt")            
        else:
            self.start_stop_analysis.config(state = "disabled")
            self.folder_name_entry.config(state = "normal")
            self.current_video_file = None
            shutil.rmtree(self.folder_name)            
        self.select_apply_roi.config(state = "normal")
        self.roi_combo_select.config(state = "readonly")
        self.fps_combo_select.config(state = "readonly")

    def clear_all(self):
        # all values and variables (apart from configuration ones) are reset so that the user can start a new session
        self.stop()
        self.turn_off()
        self.start_stop_next_phase_button.config(text = "Start Next Phase (1)", command = self.start_next_phase)
        self.start_stop_next_phase_button.grid(ipadx = 0)
        self.playback_trackbar.config(command = self.playback_bar_blank, from_ = 0, to = 0)
        self.playback_trackbar_reporter.config(text = "Playback Slider")
        self.start_stop_analysis.config(state = "disabled")
        self.tk_loop_needed = None        
        self.checkpoint = False        
        self.counta = None        
        self.start_time = None        
        self.scale_calibrate = False        
        self.phase_number = 1        
        self.current_recording_frame_number = 1
        self.phase_start_time = None
        self.recording_now = False
        self.positional_data = None
        self.positional_data = AutoVivification()
        self.fish_positions = None
        self.fish_positions = AutoVivification()
        self.fish_scoots = None
        self.fish_scoots = AutoVivification()
        self.backup = None
        self.selected_folder = None
        self.folder_name = None
        self.folder_name_small = None
        self.framerates = {}
        self.folder_name_entry.config(state = "normal")
        self.message_box.config(text = "Message: ", foreground = "dark green")
        self.current_video_file = None
        self.turn_on()

    def playback_after_phase(self, value):        
        self.playback_trackbar_reporter.config(text = "Frame = {0}, Time = {1:.2f}".format(str(int(float(value))),self.positional_data[(int(self.phase_number-1))][int(float(value))][0]))
        playback = cv.CreateImage(((self.positional_data[(int(self.phase_number-1))][0][0]),(self.positional_data[(int(self.phase_number-1))][0][1])), cv.IPL_DEPTH_8U, 3)        
        if self.positional_data[(int(self.phase_number-1))][0][0] <= self.positional_data[(int(self.phase_number-1))][0][1]:
            take_in = int((self.positional_data[(int(self.phase_number-1))][0][2]/200)*self.positional_data[(int(self.phase_number-1))][0][0])
        else:
            take_in = int((self.positional_data[(int(self.phase_number-1))][0][2]/200)*self.positional_data[(int(self.phase_number-1))][0][1])
        inner_roi_points = (take_in, take_in, self.positional_data[(int(self.phase_number-1))][0][0] - take_in, self.positional_data[(int(self.phase_number-1))][0][1] - take_in)
        cv.Rectangle(playback, (inner_roi_points[0], inner_roi_points[1]), (inner_roi_points[2], inner_roi_points[3]), (255,255,255), thickness=2, lineType=8, shift=0)       
        for n in self.positional_data[(int(self.phase_number-1))][(int(float(value)))][1]:
            phase = (int(self.phase_number-1))
            if self.positional_data[phase][0][0] <= self.positional_data[phase][0][1]:
                inner_roi_x_left = (self.positional_data[phase][0][2]/200) * self.positional_data[phase][0][0]
                inner_roi_y_up = (self.positional_data[phase][0][2]/200) * self.positional_data[phase][0][0]                
                inner_roi_x_right = self.positional_data[phase][0][0] - ((self.positional_data[phase][0][2]/200) * self.positional_data[phase][0][0])                
                inner_roi_y_down = self.positional_data[phase][0][1] - ((self.positional_data[phase][0][2]/200) * self.positional_data[phase][0][0])
            else:
                inner_roi_x_left = (self.positional_data[phase][0][2]/200) * self.positional_data[phase][0][1]
                inner_roi_y_up = (self.positional_data[phase][0][2]/200) * self.positional_data[phase][0][1]                
                inner_roi_x_right = self.positional_data[phase][0][0] - ((self.positional_data[phase][0][2]/200) * self.positional_data[phase][0][1])                
                inner_roi_y_down = self.positional_data[phase][0][1] - ((self.positional_data[phase][0][2]/200) * self.positional_data[phase][0][1])
            wow = True
            if n[0][0] <= inner_roi_x_right:
                if n[0][0] >= inner_roi_x_left:
                    if n[0][1] <= inner_roi_y_down:
                        if n[0][1] >= inner_roi_y_up:
                            colour = (0,255,0)
                            wow = False
            if wow:
                colour = (0,0,255)            
            cv.Circle(img=playback, center=(int(n[0][0]),int(n[0][1])), radius=1, color=colour, thickness=-1, lineType=8, shift=0)
        cv.ShowImage("ZTrack", playback)

    def playback_bar_blank(self, value):
        pass

    def set_scale(self):
        self.set_scale_button.config(text = "Apply Scale", command = self.apply_scale)
        self.scale_calibrate = True

    def apply_scale(self):
        self.set_scale_button.config(text = "Set Scale", command = self.set_scale)
        self.scale_calibrate = False

    def adjust_minimum_cont_area(self, value):
        self.minimum_contour_area = int(float(value))
        self.minimum_cont_area_slider_reporter.config(text = "Minimum Area = {0}".format(str(int(float(value)))))

    def adjust_adaptive_slider(self, value):
        self.adaptive_value = int(float(value))
        self.adaptive_slider_reporter.config(text = "Adaptive Value = {0}".format(str(int(float(value)))))
        if self.adaptive_value % 2 == 0:
            self.adaptive_slider.set(self.adaptive_value + 1)

    def adjust_minimum_scoot_velocity(self, value):
        self.minimum_scoot_velocity = float("{0:.2f}".format(float(value)/100))
        self.minimum_scoot_velocity_slider_reporter.config(text = "Minimum Scoot Velocity = {0:.2f} mm/sec".format(self.minimum_scoot_velocity))

    def adjust_minimum_scoot_duration(self, value):
        self.minimum_scoot_duration = float("{0:.2f}".format(float(value)/100))
        self.minimum_scoot_duration_slider_reporter.config(text = "Minimum Scoot Duration = {0:.2f} sec".format(self.minimum_scoot_duration))

    def adjust_minimum_scoot_distance(self, value):
        self.minimum_scoot_distance = float("{0:.2f}".format(float(value)/100))
        self.minimum_scoot_distance_slider_reporter.config(text = "Minimum Scoot Distance = {0:.2f} mm".format(self.minimum_scoot_distance))
        
    def adjust_maximum_scoot_distance(self, value):
        self.maximum_scoot_distance = float("{0:.2f}".format(float(value)/100))
        self.maximum_scoot_distance_slider_reporter.config(text = "Maximum Scoot Distance = {0:.2f} mm".format(self.maximum_scoot_distance))
 
    def fps_combo_report(self, event):
        selected = self.fps_combo_select.get()
        if selected == "30 fps":
            self.base_framerate = 30
        elif selected == "25 fps":
            self.base_framerate = 25
        elif selected == "24 fps":
            self.base_framerate = 24
        elif selected == "20 fps":
            self.base_framerate = 20
        elif selected == "15 fps":
            self.base_framerate = 15
        elif selected == "10 fps":
            self.base_framerate = 10
        elif selected == "5 fps":
            self.base_framerate = 5

        if self.capture:
            cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FPS, self.base_framerate)

        self.roi_combo_report(None)

    def roi_combo_report(self, event):
        selected = self.roi_combo_select.get()
        if selected == "1920 x 1080 pix":
            self.base_width = 1920
            self.base_height = 1080
            self.outer_roi_y = 1080
            self.outer_roi_x = 1920
        elif selected == "1280 x 720 pix":
            self.base_width = 1280
            self.base_height = 720
            self.outer_roi_y = 720
            self.outer_roi_x = 1280
        elif selected == "800 x 600 pix":
            self.base_width = 800
            self.base_height = 600
            self.outer_roi_y = 600
            self.outer_roi_x = 800
        elif selected == "640 x 480 pix":
            self.base_width = 640
            self.base_height = 480
            self.outer_roi_y = 480
            self.outer_roi_x = 640
        elif selected == "320 x 240 pix":
            self.base_width = 320
            self.base_height = 240
            self.outer_roi_y = 240
            self.outer_roi_x = 320
            
        if self.capture:
            cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_WIDTH, self.base_width)
            cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_HEIGHT, self.base_height)
            
        if self.changing_x:
            self.sizebar_reporter.config(text = "{0} pixels".format(self.outer_roi_x))
            self.sizebar.config(to = self.base_width)
            self.sizebar.set(self.outer_roi_x)            
        elif self.changing_y:
            self.sizebar_reporter.config(text = "{0} pixels".format(self.outer_roi_y))            
            self.sizebar.config(to = self.base_height)
            self.sizebar.set(self.outer_roi_y)    

    def start_analysis(self):
        if os.path.exists((self.folder_name + "/fish_position_data")):
            try:
                shutil.rmtree((self.folder_name + "/fish_position_data"))
                shutil.rmtree((self.folder_name + "/scoots_inner_roi"))
                shutil.rmtree((self.folder_name + "/scoots_mixed"))
                shutil.rmtree((self.folder_name + "/distance_vs_number"))
                shutil.rmtree((self.folder_name + "/distance_vs_time"))
                shutil.rmtree((self.folder_name + "/path_composite"))
            except:
                self.message_box.config(text = "Message: Please close all previously analysed files then try again.", foreground = "dark green")
                return

        self.doing_initial = False
        self.doing_initialising_analysis = False
        self.doing_assigning_points_to_larvae = False
        self.doing_saving_excel_fish_positions = False
        self.doing_calculating_scoot_distances = False
        self.doing_saving_excel_scoot_distances_mixed = False
        self.doing_saving_excel_scoot_distances_inner_roi = False
        self.doing_initiating_playback = False
        self.doing_producing_graphs_distance_time = False
        self.doing_producing_graphs_distance_scoot_no = False
        self.doing_producing_path_composites = False
        self.doing_producing_scoot_parameters = False
        self.doing_initial = True
        
        self.nabba = True
        self.poppy = Popup(self, self.master)
        self.main_analysis()

    def main_analysis(self):
        if self.nabba:

            if self.doing_initial:
                self.doing_initial = False
                self.doing_initialising_analysis = True
                self.poppy.label1.config(text = "")
                self.poppy.label2.config(text = "")
                self.poppy.label1.config(text = "Step 1/11, time elapsed = 0 sec")
                self.poppy.label2.config(text = "Initiating the analysis...")
                self.poppy.update(1)
                self.analysis_timer = clock()
                self.message_box.config(text = "Message: Performing the analysis. This may take several minutes.", foreground = "dark green")


            elif self.doing_initialising_analysis:

                self.start_stop_analysis.config(state = "disabled")
                self.stop()
                if not self.backup:
                    self.backup = copy.deepcopy(self.positional_data)
                else:
                    self.positional_data = None
                    self.positional_data = AutoVivification()
                    self.positional_data = copy.deepcopy(self.backup)
                self.fish_positions = None
                self.fish_positions = AutoVivification()
                self.fish_positions = copy.deepcopy(self.positional_data)
                # finds the mode for each phase and appends it to the info tuple of each phase for self.fish_positions
                for phase in self.positional_data:
                    temporary_points = []
                    for points in self.positional_data[phase]:
                        if points != 0:
                            temporary_points.append(len(self.positional_data[phase][points][1]))
                    temporary_array = numpy.array(temporary_points)
                    self.fish_positions[phase][0] += (int(numpy.argmax(numpy.bincount(temporary_array))),)

                # preparing self.fish_positions for the analysis
                for phase in self.fish_positions:
                    for frame in self.fish_positions[phase]:
                        if frame != 0:
                            self.fish_positions[phase][frame] = {}
                            self.fish_positions[phase][frame][0] = self.positional_data[phase][frame][0]

                self.doing_initialising_analysis = False
                self.doing_assigning_points_to_larvae = True
                self.poppy.label1.config(text = "")
                self.poppy.label2.config(text = "")
                self.poppy.label1.config(text = "Step 2/11, time elapsed = {0:.2f} sec".format(float(clock() - self.analysis_timer)))
                self.poppy.label2.config(text = "Assigning points to larvae...")
                self.poppy.update(2)


            elif self.doing_assigning_points_to_larvae:

                ## assign_points_to_larvae
                # find the mode number of points for the phase
                # for each frame make a list of fish based on the mode number, e.g. if 10 fish, [1,2,3,4,5,6,7,8,9,10]
                # then make a list of the available points, e.g. if 5 points [(2,4),(5,2),(10,39),(250, 99),(3,23)]
                # then make a list of the closest interactions between the last positions of the fish and the current positions, e.g. [(2,2,4),(8,250,99)] this means fish 2 is closest to 2,4 and fish 8 is closest to 250,99
                # start from the beginning of this list and assign points to each fish, while taking away each point and fish from the respective list once it is used up
                # repeat until either one of two things happen: the fish run out or the points run out
                # if the fish list runs out, break then move on to the next frame
                # if the points list runs out, add False to the remaining fish. current point is m and last known point is n for a fish. have to go back to n then find the distance, average it across points
                # then add them instead of False - if the point of original loss was 0 (i.e. the first frame), make the current position the same position for all frames up to the current frame
                # -----------------------------------------------------
                # make fish list using xrange and list comprehension
                # make available points list
                # make new list that contains the proximity of the previous known position of each fish. so start the loop going through each fish and establish the last known position (that isn't False,False) then
                    # loop through the available points list and compare
                # sort the new list so that the closest points are first - should be like this: [(distance, fish x, point tuple)]                        
                # loop through the new list and assign points to fish. then delete the respective point and fish off the original list, i.e. if not in original list, skip because already used
                    # when assigning, if the previous point was False need to trace back to a frame that isn't False
                    # if reach frame 1, make the current position as the position for all frames so far
                    # if find a point, measure the distance between that and the current point, split it up by the number of frames, then assign points as the averages for the frames in between
                # have a checking mechanism to see whether the individual lists are empty or not. if fish list empty then go on to the next frame
                # if the points list runs out first, loop through the fish list and assign False for the current frame
                # third possibility = both fish list and point list are not empty because a fish that has not had a point since the start of the phase gets a point now
                    # so i would have to loop through the available points list and assign a point to a fish (
                    # what if excess points and no fish? then break. what if no points left but still fish left? check after the loop if fish available, if so, give them False)
                for phase in self.fish_positions:
                    for frame in self.fish_positions[phase]:
                        if frame != 0:
                            if frame == 1:
                                # start of each phase
                                available_points = [n[0] for n in self.positional_data[phase][frame][1]]
                                for fish in xrange(1, (self.fish_positions[phase][0][5] + 1)):
                                    if available_points:
                                        self.fish_positions[phase][frame][fish] = available_points.pop()
                                    else:
                                        self.fish_positions[phase][frame][fish] = False
                            else:
                                available_points = [n[0] for n in self.positional_data[phase][frame][1]]
                                available_fish = [n for n in xrange(1, (self.fish_positions[phase][0][5] + 1))]
                                proximity_list = []
                                for fishy in available_fish:
                                    # find the last position of the fish. if all False, don't do anything
                                    frame_to_look = frame - 1
                                    while True:
                                        if frame_to_look < 1:
                                            last_known = False
                                            break
                                        else:
                                            if self.fish_positions[phase][frame_to_look][fishy]:
                                                last_known = self.fish_positions[phase][frame_to_look][fishy]
                                                break
                                        frame_to_look -= 1
                                    if last_known:
                                        for pointy in available_points:
                                            proximity_list.append((math.hypot((last_known[0] - pointy[0]),(last_known[1] - pointy[1])), fishy, pointy))
                                proximity_list.sort()
                                for element in proximity_list:
                                    if element[1] in available_fish:
                                        if element[2] in available_points:
                                            available_fish.remove(element[1])
                                            available_points.remove(element[2])
                                            self.fish_positions[phase][frame][(element[1])] = element[2]
                                            if not self.fish_positions[phase][(frame - 1)][(element[1])]:
                                                # go through and do linear stuff
                                                frame_to_look = frame - 2
                                                while True:
                                                    if self.fish_positions[phase][frame_to_look][(element[1])]:
                                                        # calc distance and fill in
                                                        ex = element[2][0] - self.fish_positions[phase][frame_to_look][(element[1])][0]
                                                        why = element[2][1] - self.fish_positions[phase][frame_to_look][(element[1])][1]
                                                        total_length = math.hypot(ex,why)
                                                        dist_to_add = total_length/(frame - frame_to_look)
                                                        current_distance = dist_to_add
                                                        for nom_nom in xrange((frame_to_look + 1), frame):
                                                            if total_length > 0:
                                                                coordinates = ((((current_distance/total_length)*ex)+self.fish_positions[phase][frame_to_look][(element[1])][0]),(((current_distance/total_length)*why)+self.fish_positions[phase][frame_to_look][(element[1])][1]))
                                                            else:
                                                                coordinates = self.fish_positions[phase][frame_to_look][(element[1])]
                                                            self.fish_positions[phase][nom_nom][(element[1])] = coordinates
                                                            current_distance += dist_to_add
                                                        break
                                                    frame_to_look -= 1
                                # now have to check whether available_points and available_fish are empty
                                if available_fish:
                                    if available_points:
                                        for aaavail in available_points:
                                            if available_fish:
                                                popped = available_fish.pop()
                                                for framed in xrange(1, (frame + 1)):                                            
                                                    self.fish_positions[phase][framed][popped] = aaavail
                                            else:
                                                break
                                        if available_fish:
                                            for fffish in available_fish:
                                                self.fish_positions[phase][frame][fffish] = False
                                    else:
                                        for fffish in available_fish:
                                            self.fish_positions[phase][frame][fffish] = False                       
                    # since there could be fish that have been missing from one point to the end, have to get rid of the Falses by filling them in with the last known position
                    for fishay in xrange(1, (self.fish_positions[phase][0][5] + 1)):
                        if not self.fish_positions[phase][(len(self.fish_positions[phase]) - 1)][fishay]:
                            last_known = len(self.fish_positions[phase]) - 2
                            while True:
                                if self.fish_positions[phase][last_known][fishay]:
                                    for frame_to_use in xrange((last_known + 1),(len(self.fish_positions[phase]))):
                                        self.fish_positions[phase][frame_to_use][fishay] = self.fish_positions[phase][last_known][fishay]
                                    break
                                if last_known < 1:
                                    break
                                last_known -= 1

                self.doing_assigning_points_to_larvae = False
                self.doing_saving_excel_fish_positions = True
                self.poppy.label1.config(text = "")
                self.poppy.label2.config(text = "")
                self.poppy.label1.config(text = "Step 3/11, time elapsed = {0:.2f} sec".format(float(clock() - self.analysis_timer)))
                self.poppy.label2.config(text = "Saving excel fish positions...")
                self.poppy.update(3)
                

            elif self.doing_saving_excel_fish_positions:

                os.makedirs((self.folder_name + "/fish_position_data"))
                os.makedirs((self.folder_name + "/scoots_inner_roi"))
                os.makedirs((self.folder_name + "/scoots_mixed"))
                os.makedirs((self.folder_name + "/distance_vs_number"))
                os.makedirs((self.folder_name + "/distance_vs_time"))
                os.makedirs((self.folder_name + "/path_composite"))

                ## save_excel_fish_positions
                for gg in self.fish_positions:
                    xy_data_excel = open(self.folder_name + "/fish_position_data/" + "fish_position_data " + self.folder_name_small + " P" + str(gg) + " " + str(self.fish_positions[gg][0][4]) + " sec" + ".csv", "wb")
                    xy_writer = csv.writer(xy_data_excel, quoting=csv.QUOTE_MINIMAL)
                    xy_writer.writerow([''] + ['Time (sec)'] + [str(n) for n in self.fish_positions[gg][1] if n != 0])
                    for nn in self.fish_positions[gg]:
                        if nn != 0:
                            x_temp_list = ["X", self.fish_positions[gg][nn][0]] + [self.fish_positions[gg][nn][n][0] for n in self.fish_positions[gg][nn] if n != 0]
                            y_temp_list = ["Y", ""] + [self.fish_positions[gg][nn][n][1] for n in self.fish_positions[gg][nn] if n != 0]
                            xy_writer.writerow(x_temp_list)
                            xy_writer.writerow(y_temp_list)
                    xy_data_excel.close()

                self.doing_saving_excel_fish_positions = False
                self.doing_calculating_scoot_distances = True
                self.poppy.label1.config(text = "")
                self.poppy.label2.config(text = "")
                self.poppy.label1.config(text = "Step 4/11, time elapsed = {0:.2f} sec".format(float(clock() - self.analysis_timer)))
                self.poppy.label2.config(text = "Calculating scoot distances...")
                self.poppy.update(4)                


            elif self.doing_calculating_scoot_distances:

                ## calculate_scoot_distances
                # consider the variable time between frames
                # consider the inner roi
                # consider the scale
                # strategy: when a fish moves above a threshold velocity, will register it as scooting. when it moves below this threshold, registered as having finished the scoot.
                # to avoid registering jitters and random jumps, the scoot will need to last a threshold time
                # only scoots above and below threshold distances (e.g. above 0.5 mm and below 3 mm) will be registered
                # make these thresholds unadjustable by the user and base them on data
                # if the velocity threshold is reached, the start of the scoot is at frame n - 1
                self.fish_scoots = AutoVivification()
                # preparing self.fish_scoots for the analysis
                for phase in self.fish_positions:
                    self.fish_scoots[phase][0] = self.fish_positions[phase][0]
                # main scoot detection algorithm
                for phase in self.fish_scoots:
                    for fish_number in xrange(1, (self.fish_scoots[phase][0][5] + 1)):
                        during_scoot = False
                        current_scoot_details = ()
                        for frame in xrange(2, len(self.fish_positions[phase])):
                            # at the end of the following line is a threshold for distance per frame in mm/sec
                            if ((math.hypot((self.fish_positions[phase][frame][fish_number][0] - self.fish_positions[phase][frame - 1][fish_number][0]),(self.fish_positions[phase][frame][fish_number][1] - self.fish_positions[phase][frame - 1][fish_number][1])))/(self.fish_positions[phase][frame][0] - self.fish_positions[phase][frame - 1][0])) * self.fish_scoots[phase][0][3] >= self.minimum_scoot_velocity:
                                if not during_scoot:
                                    during_scoot = True
                                    # start the scoot details
                                    current_scoot_details = ((frame - 1),)
                            else:
                                if during_scoot:
                                    during_scoot = False
                                    scoot_distance = self.fish_scoots[phase][0][3] * (math.hypot((self.fish_positions[phase][frame][fish_number][0] - self.fish_positions[phase][(current_scoot_details[0])][fish_number][0]),(self.fish_positions[phase][frame][fish_number][1] - self.fish_positions[phase][(current_scoot_details[0])][fish_number][1])))
                                    duration = (self.fish_positions[phase][frame][0]) - (self.fish_positions[phase][(current_scoot_details[0])][0])
                                    if self.fish_scoots[phase][0][0] <= self.fish_scoots[phase][0][1]:
                                        inner_roi_x_left = (self.fish_scoots[phase][0][2]/200) * self.fish_scoots[phase][0][0]
                                        inner_roi_y_up = (self.fish_scoots[phase][0][2]/200) * self.fish_scoots[phase][0][0]
                                        inner_roi_x_right = self.fish_scoots[phase][0][0] - ((self.fish_scoots[phase][0][2]/200) * self.fish_scoots[phase][0][0])                                
                                        inner_roi_y_down = self.fish_scoots[phase][0][1] - ((self.fish_scoots[phase][0][2]/200) * self.fish_scoots[phase][0][0])
                                    else:
                                        inner_roi_x_left = (self.fish_scoots[phase][0][2]/200) * self.fish_scoots[phase][0][1]
                                        inner_roi_y_up = (self.fish_scoots[phase][0][2]/200) * self.fish_scoots[phase][0][1]
                                        inner_roi_x_right = self.fish_scoots[phase][0][0] - ((self.fish_scoots[phase][0][2]/200) * self.fish_scoots[phase][0][1])                                
                                        inner_roi_y_down = self.fish_scoots[phase][0][1] - ((self.fish_scoots[phase][0][2]/200) * self.fish_scoots[phase][0][1])                            
                                    wow = True
                                    if self.fish_positions[phase][frame][fish_number][0] <= inner_roi_x_right:
                                        if self.fish_positions[phase][frame][fish_number][0] >= inner_roi_x_left:
                                            if self.fish_positions[phase][frame][fish_number][1] <= inner_roi_y_down:
                                                if self.fish_positions[phase][frame][fish_number][1] >= inner_roi_y_up:
                                                    if self.fish_positions[phase][current_scoot_details[0]][fish_number][0] <= inner_roi_x_right:
                                                        if self.fish_positions[phase][current_scoot_details[0]][fish_number][0] >= inner_roi_x_left:
                                                            if self.fish_positions[phase][current_scoot_details[0]][fish_number][1] <= inner_roi_y_down:
                                                                if self.fish_positions[phase][current_scoot_details[0]][fish_number][1] >= inner_roi_y_up:
                                                                    inside_roi = True
                                                                    wow = False
                                    if wow:
                                        inside_roi = False
                                    current_scoot_details += (frame, scoot_distance, duration, inside_roi)
                                    if scoot_distance <= self.maximum_scoot_distance:
                                        if scoot_distance >= self.minimum_scoot_distance:
                                            if duration >= self.minimum_scoot_duration:
                                                self.fish_scoots[phase][fish_number][int(len(self.fish_scoots[phase][fish_number]) + 1)] = current_scoot_details
                                    current_scoot_details = ()

                self.doing_calculating_scoot_distances = False
                self.doing_saving_excel_scoot_distances_mixed = True
                self.poppy.label1.config(text = "")
                self.poppy.label2.config(text = "")
                self.poppy.label1.config(text = "Step 5/11, time elapsed = {0:.2f} sec".format(float(clock() - self.analysis_timer)))
                self.poppy.label2.config(text = "Saving excel scoot distances mixed...")
                self.poppy.update(5)                


            elif self.doing_saving_excel_scoot_distances_mixed:

                ## save_excel_scoot_distances_mixed
                # include the outer roi scoots
                for gg in self.fish_scoots:
                    keysorted = (self.fish_scoots[gg]).keys()
                    keysorted.sort()            
                    scoot_data_excel = open(self.folder_name + "/scoots_mixed/" + "scoots_mixed " + self.folder_name_small + " P" + str(gg) + " " + str(self.fish_scoots[gg][0][4]) + " sec" + ".csv", "wb")
                    scoot_writer = csv.writer(scoot_data_excel, quoting=csv.QUOTE_MINIMAL)
                    first = ['Fish No.']
                    largest = 0            
                    for n in keysorted:
                        if n != 0:
                            first.append(str(n))
                            first.append(str(n))
                            first.append(str(n))
                            first.append(str(n))
                            if len(self.fish_scoots[gg][n]) > largest:
                                largest = len(self.fish_scoots[gg][n])                    
                    scoot_writer.writerow(first)
                    scoot_writer.writerow(['Scoot No.'] + (len(self.fish_scoots[gg]) - 1) * ['Time (sec)', 'Distance (mm)', 'Duration (sec)', 'Within ROI'])
                    for tral in xrange(1, largest + 1):
                        write = [str(tral)]
                        for eng in keysorted:
                            if eng != 0:
                                if self.fish_scoots[gg][eng][tral]:
                                    timeo = self.fish_scoots[gg][eng][tral][0]
                                    write.append(str(self.fish_positions[gg][timeo][0]))
                                    write.append(str(self.fish_scoots[gg][eng][tral][2]))
                                    write.append(str(self.fish_scoots[gg][eng][tral][3]))
                                    write.append(str(self.fish_scoots[gg][eng][tral][4]))
                                else:
                                    write.append(" ")
                                    write.append(" ")
                                    write.append(" ")
                                    write.append(" ")
                        scoot_writer.writerow(write)
                    scoot_data_excel.close()

                self.doing_saving_excel_scoot_distances_mixed = False
                self.doing_saving_excel_scoot_distances_inner_roi = True
                self.poppy.label1.config(text = "")
                self.poppy.label2.config(text = "")
                self.poppy.label1.config(text = "Step 6/11, time elapsed = {0:.2f} sec".format(float(clock() - self.analysis_timer)))
                self.poppy.label2.config(text = "Saving excel scoot distances inner ROI...")
                self.poppy.update(6)                


            elif self.doing_saving_excel_scoot_distances_inner_roi:

                ## save_excel_scoot_distances_just_inner_roi
                for gg in self.fish_scoots:
                    keysorted = (self.fish_scoots[gg]).keys()
                    keysorted.sort()            
                    scoot_data_excel = open(self.folder_name + "/scoots_inner_roi/" + "scoots_inner_roi " + self.folder_name_small + " P" + str(gg) + " " + str(self.fish_scoots[gg][0][4]) + " sec" + ".csv", "wb")
                    scoot_writer = csv.writer(scoot_data_excel, quoting=csv.QUOTE_MINIMAL)
                    first = ['Fish No.']
                    largest = 0
                    knowswhether = {}            
                    for n in keysorted:
                        if n != 0:
                            first.append(str(n))
                            first.append(str(n))
                            first.append(str(n))
                            first.append(str(n))
                            knowswhether[n] = 1
                            numba = 0
                            for scooooot in self.fish_scoots[gg][n]:
                                if self.fish_scoots[gg][n][scooooot]:
                                    if self.fish_scoots[gg][n][scooooot][4]:
                                        numba += 1
                            if numba > largest:
                                largest = numba
                    scoot_writer.writerow(first)
                    scoot_writer.writerow(['Scoot No.'] + (len(self.fish_scoots[gg]) - 1) * ['Time (sec)', 'Distance (mm)', 'Duration (sec)', 'Within ROI'])
                    for tral in xrange(1, largest + 1):
                        write = [str(tral)]
                        for eng in keysorted:
                            if eng != 0:
                                while True:
                                    if self.fish_scoots[gg][eng][knowswhether[eng]]:
                                        if self.fish_scoots[gg][eng][knowswhether[eng]][4]:
                                            timeo = self.fish_scoots[gg][eng][knowswhether[eng]][0]
                                            write.append(str(self.fish_positions[gg][timeo][0]))
                                            write.append(str(self.fish_scoots[gg][eng][knowswhether[eng]][2]))
                                            write.append(str(self.fish_scoots[gg][eng][knowswhether[eng]][3]))
                                            write.append(str(self.fish_scoots[gg][eng][knowswhether[eng]][4]))
                                            knowswhether[eng] += 1
                                            break
                                        else:
                                            knowswhether[eng] += 1
                                    else:
                                        write.append(" ")
                                        write.append(" ")
                                        write.append(" ")
                                        write.append(" ")
                                        break
                        scoot_writer.writerow(write)
                    scoot_data_excel.close()

                self.doing_saving_excel_scoot_distances_inner_roi = False
                self.doing_initiating_playback = True
                self.poppy.label1.config(text = "")
                self.poppy.label2.config(text = "")                
                self.poppy.label1.config(text = "Step 7/11, time elapsed = {0:.2f} sec".format(float(clock() - self.analysis_timer)))
                self.poppy.label2.config(text = "Initiating playback...")
                self.poppy.update(7)
                

            elif self.doing_initiating_playback:
            
                ## initiate_playback
                # consider the inner roi
                # when larvae are outside the inner roi make them a different colour, e.g. green when moving, red when stopped and purple when outside inner roi
                # have coloured trails and larvae
                # have the whole session on one trackbar, i.e. include all phases (but fish 1 in phase 1 should have a different colour from fish 1 in phase 2 because it's a different fish)
                # first, assign colours to each fish
                for phase in self.fish_positions:            
                    colours = []
                    for col in xrange((0),(self.fish_positions[phase][0][5] + 1)):
                        if col == 0:
                            colours.append("")
                        else:
                            colours.append((random.randint(85,255),random.randint(85,255),random.randint(85,255)))    
                    for frame in self.fish_positions[phase]:
                        if frame != 0:
                            for fish in self.fish_positions[phase][frame]:
                                if fish != 0:
                                    self.fish_positions[phase][frame][fish] += colours[fish]
                # put scoots in self.fish_positions
                for phase in self.fish_scoots:
                    for fish in self.fish_scoots[phase]:
                        if fish != 0:
                            for scoot in self.fish_scoots[phase][fish]:
                                if self.fish_scoots[phase][fish][scoot]:
                                    for coverage in xrange(self.fish_scoots[phase][fish][scoot][0], self.fish_scoots[phase][fish][scoot][1] + 1):
                                        self.fish_positions[phase][coverage][fish] += (True,)
                # trackbar configuration
                length = 0
                for phase in self.fish_positions:
                    length += int(len(self.fish_positions[phase]) - 1)
                self.playback_trackbar.config(command = self.playback_after_analysis, from_ = 1, to = length)
                self.playback_trackbar.set(1)

                self.doing_initiating_playback = False
                self.doing_producing_graphs_distance_time = True
                self.poppy.label1.config(text = "")
                self.poppy.label2.config(text = "")
                self.poppy.label1.config(text = "Step 8/11, time elapsed = {0:.2f} sec".format(float(clock() - self.analysis_timer)))
                self.poppy.label2.config(text = "Producing distance vs time graph...")
                self.poppy.update(8)
                

            elif self.doing_producing_graphs_distance_time:

                ## produce_graphs
                # consider the inner roi - exlude all scoots that are outside of it
                # have one with scoot number for x-axis and the other with time for x-axis
                # larvae all have different colours and also between phases so that no one thinks two larvae are the same if they lead on from phase-to-phase
                # scoot distance vs. time
                for phase in self.fish_scoots:
                    if phase != 0:
                        plt.figure()
                        plt.title('Phase {0} Scoot Distance vs. Time'.format(phase))
                        plt.ylabel('Scoot Distance (mm)')
                        plt.xlabel('Time (sec)')
                        plt.axis([0, int(self.fish_scoots[phase][0][4]), self.minimum_scoot_distance, self.maximum_scoot_distance])
                        for fish in self.fish_scoots[phase]:
                            if fish != 0:
                                time_list = []
                                scoot_dist_list = []
                                for scoot in self.fish_scoots[phase][fish]:
                                    if self.fish_scoots[phase][fish][scoot][4]:
                                        scoot_dist_list.append(self.fish_scoots[phase][fish][scoot][2])
                                        time_list.append(self.fish_positions[phase][(self.fish_scoots[phase][fish][scoot][0])][0])
                                time_list = numpy.array(time_list)
                                scoot_dist_list = numpy.array(scoot_dist_list)
                                plt.plot(time_list, scoot_dist_list, color = (0,0,0), linewidth = 0.5)
                                plt.plot(time_list, scoot_dist_list, 'o', markerfacecolor=((self.fish_positions[phase][1][fish][4]/255),(self.fish_positions[phase][1][fish][3]/255),(self.fish_positions[phase][1][fish][2]/255)), markersize=3)                        
                        plt.savefig(self.folder_name + "/distance_vs_time/" + "distance_vs_time " + self.folder_name_small + " P" + str(phase) + " " + str(self.fish_scoots[phase][0][4]) + " sec" + ".png", dpi = 300, transparent = True, bbox_inches = None)

                self.doing_producing_graphs_distance_time = False
                self.doing_producing_graphs_distance_scoot_no = True
                self.poppy.label1.config(text = "")
                self.poppy.label2.config(text = "")
                self.poppy.label1.config(text = "Step 9/11, time elapsed = {0:.2f} sec".format(float(clock() - self.analysis_timer)))
                self.poppy.label2.config(text = "Producing distance vs scoot number graph...")
                self.poppy.update(9)                


            elif self.doing_producing_graphs_distance_scoot_no:

                # scoot distance vs. scoot number
                for phase in self.fish_scoots:
                    if phase != 0:
                        plt.figure()
                        plt.title('Phase {0} Scoot Distance vs. Scoot Number'.format(phase))
                        plt.ylabel('Scoot Distance (mm)')
                        plt.xlabel('Scoot Number')
                        largest_scoots = 0
                        for fish in self.fish_scoots[phase]:
                            if fish != 0:
                                number_list = []
                                scoot_dist_list = []
                                for scoot in self.fish_scoots[phase][fish]:
                                    if self.fish_scoots[phase][fish][scoot][4]:
                                        scoot_dist_list.append(self.fish_scoots[phase][fish][scoot][2])
                                        number_list.append(scoot)
                                if len(self.fish_scoots[phase][fish]) > largest_scoots:
                                    largest_scoots = int(len(self.fish_scoots[phase][fish]))
                                number_list = numpy.array(number_list)
                                scoot_dist_list = numpy.array(scoot_dist_list)
                                plt.plot(number_list, scoot_dist_list, color = (0,0,0), linewidth = 0.5)
                                plt.plot(number_list, scoot_dist_list, 'o', markerfacecolor=((self.fish_positions[phase][1][fish][4]/255),(self.fish_positions[phase][1][fish][3]/255),(self.fish_positions[phase][1][fish][2]/255)), markersize=3)                        
                        plt.axis([1, largest_scoots, self.minimum_scoot_distance, self.maximum_scoot_distance])
                        plt.savefig(self.folder_name + "/distance_vs_number/" + "distance_vs_number " + self.folder_name_small + " P" + str(phase) + " " + str(self.fish_scoots[phase][0][4]) + " sec" + ".png", dpi = 300, transparent = True, bbox_inches = None)

                self.doing_producing_graphs_distance_scoot_no = False
                self.doing_producing_path_composites = True
                self.poppy.label1.config(text = "")
                self.poppy.label2.config(text = "")
                self.poppy.label1.config(text = "Step 10/11, time elapsed = {0:.2f} sec".format(float(clock() - self.analysis_timer)))
                self.poppy.label2.config(text = "Producing path composite figure...")
                self.poppy.update(10)                


            elif self.doing_producing_path_composites:

                ## produce_path_composites
                for phase in self.fish_positions:
                    figure_phase = cv.CreateImage((self.fish_positions[phase][0][0],self.fish_positions[phase][0][1]), cv.IPL_DEPTH_8U, 3)
                    for frame in self.fish_positions[phase]:
                        if frame != 0:
                            for fish in self.fish_positions[phase][frame]:
                                if fish != 0:
                                    figure_phase[int(self.fish_positions[phase][frame][fish][1]),int(self.fish_positions[phase][frame][fish][0])] = ((self.fish_positions[phase][frame][fish][2]),(self.fish_positions[phase][frame][fish][3]),(self.fish_positions[phase][frame][fish][4]))
                    cv.SaveImage(self.folder_name + "/path_composite/" + "path_composite " + self.folder_name_small + " P" + str(phase) + " " + str(self.fish_positions[phase][0][4]) + " sec" + ".png", figure_phase)

                self.doing_producing_path_composites = False
                self.doing_producing_scoot_parameters = True
                self.poppy.label1.config(text = "")
                self.poppy.label2.config(text = "")
                self.poppy.label1.config(text = "Step 11/11, time elapsed = {0:.2f} sec".format(float(clock() - self.analysis_timer)))
                self.poppy.label2.config(text = "Writing scoot parameters...")
                self.poppy.update(11)
                

            elif self.doing_producing_scoot_parameters:

                ## produce_scoot_parameters
                scoot_settings = open(self.folder_name + "/" + "scoot_parameters_session " + self.folder_name_small + ".txt", "w")
                scoot_settings.write("Minimum scoot velocity = " + str(self.minimum_scoot_velocity) + " mm/sec\n")
                scoot_settings.write("Minimum scoot duration = " + str(self.minimum_scoot_duration) + " sec\n")
                scoot_settings.write("Minimum scoot distance = " + str(self.minimum_scoot_distance) + " mm\n")
                scoot_settings.write("Maximum scoot distance = " + str(self.maximum_scoot_distance) + " mm")
                scoot_settings.close()

                self.start_stop_analysis.config(state = "normal")
                self.message_box.config(text = "Message: Analysis complete. Time taken = {0:.2f} seconds.".format(float(clock() - self.analysis_timer)), foreground = "dark green")

                self.doing_initial = False
                self.doing_initialising_analysis = False
                self.doing_assigning_points_to_larvae = False
                self.doing_saving_excel_fish_positions = False
                self.doing_calculating_scoot_distances = False
                self.doing_saving_excel_scoot_distances_mixed = False
                self.doing_saving_excel_scoot_distances_inner_roi = False
                self.doing_initiating_playback = False
                self.doing_producing_graphs_distance_time = False
                self.doing_producing_graphs_distance_scoot_no = False
                self.doing_producing_path_composites = False
                self.doing_producing_scoot_parameters = False
                self.nabba = False


            self.jabba = self.master.after(500, self.main_analysis)

        else:
            self.end_analysis()

    def before_end_analysis(self):
        self.message_box.config(text = "Message: Analysis cancelled.", foreground = "dark green")
        self.end_analysis()

    def end_analysis(self):
        if self.jabba is not None:
            self.master.after_cancel(self.jabba)
            self.jabba = None
            self.poppy.destroy()
            self.poppy = None
            self.start_stop_analysis.config(state = "normal")

    def playback_after_analysis(self, value):
        # finding correct phase and frame
        for phase in self.fish_positions:
            total = 0
            for x in xrange(1, (phase + 1)):
                total += (len(self.fish_positions[x]) - 1)
            if total >= int(float(value)):
                frame_to_use = int((len(self.fish_positions[phase]) - 1) - (total - int(float(value))))
                phase_to_use = phase
                break
        self.playback_trackbar_reporter.config(text = "Phase = {0}, Frame = {1}, Time = {2:.2f}".format(str(phase_to_use), str(frame_to_use), self.fish_positions[phase_to_use][frame_to_use][0]))
        playback = cv.CreateImage(((self.fish_positions[phase_to_use][0][0]),(self.fish_positions[phase_to_use][0][1])), cv.IPL_DEPTH_8U, 3)
        # trail for each fish
        for fish in self.fish_positions[phase_to_use][frame_to_use]:
            if fish != 0:
                for frame in xrange((frame_to_use - 75),(frame_to_use + 1)):
                    if frame > 0:
                        playback[int(self.fish_positions[phase_to_use][frame][fish][1]),int(self.fish_positions[phase_to_use][frame][fish][0])] = ((self.fish_positions[phase_to_use][frame][fish][2]),(self.fish_positions[phase_to_use][frame][fish][3]),(self.fish_positions[phase_to_use][frame][fish][4]))
        # inner roi
        if self.fish_positions[phase_to_use][0][0] <= self.fish_positions[phase_to_use][0][1]:
            take_in = int((self.fish_positions[phase_to_use][0][2]/200)*self.fish_positions[phase_to_use][0][0])
        else:
            take_in = int((self.fish_positions[phase_to_use][0][2]/200)*self.fish_positions[phase_to_use][0][1])
        inner_roi_points = (take_in, take_in, self.fish_positions[phase_to_use][0][0] - take_in, self.fish_positions[phase_to_use][0][1] - take_in)
        cv.Rectangle(playback, (inner_roi_points[0], inner_roi_points[1]), (inner_roi_points[2], inner_roi_points[3]), (255,255,255), thickness=2, lineType=8, shift=0)
        # drawing each fish
        for n in self.fish_positions[phase_to_use][frame_to_use]:
            if n != 0:
                try:
                    self.fish_positions[phase_to_use][frame_to_use][n][5]
                    ccc = (0,255,0)
                except Exception:
                    ccc = (0,0,255)
                cv.Circle(img=playback, center=(int(self.fish_positions[phase_to_use][frame_to_use][n][0]),int(self.fish_positions[phase_to_use][frame_to_use][n][1])), radius=1, color = ccc, thickness=-1, lineType=8, shift=0)
        cv.ShowImage("ZTrack", playback)

    def change_roi_type(self):
        if self.rectangular_roi:            
            self.rectangular_roi = False
            self.rectangular_or_ellipse_roi.config(text = "Rectangular ROI")
            self.rectangular_or_ellipse_roi.grid(ipadx = 8)
        else:
            self.rectangular_roi = True
            self.rectangular_or_ellipse_roi.config(text = "Elliptical ROI")
            self.rectangular_or_ellipse_roi.grid(ipadx = 18)

    def import_xy_coords(self):
        self.importing = Importing(self, self.master)

    def select_folder(self):
        self.selected_folder = tkFileDialog.askdirectory(initialdir = os.path.expanduser('~/Desktop'), title = "Please select the folder that will contain the analysed files from the program.")
        self.selected_folder = str(self.selected_folder)

class Popup(Toplevel):
    
    def __init__(self, parent, master):
        Toplevel.__init__(self, master)
        self.transient(master)
        self.parent = parent
        self.resizable(0,0)
        self.label2 = Label(self, text = '', width = 40)
        self.label2.grid()
        self.canlol = Canvas(self, width = 250, height = 15)
        self.canlol.grid()
        self.label1 = Label(self, text = '')
        self.label1.grid()
        self.button1 = Button(self, text = "Cancel", command = self.parent.before_end_analysis)
        self.button1.grid(pady = 5)
        self.grab_set()

    def update(self, upto):
        self.canlol.delete(ALL)
        self.canlol.create_rectangle((0,0,int((upto/11)*250),15), fill = "blue", width = 0, outline = "blue")

class Importing(Toplevel):
    
    def __init__(self, parent, master):
        Toplevel.__init__(self, master)
        self.parent = parent
        self.transient(master)        
        self.resizable(0,0)
        self.grab_set()
        
        self.folder_location_entry = Entry(self, width = 45)
        self.folder_location_entry.grid(row = 0, column = 0)
        self.folder_location_entry.insert(END, "Location of the folder you wish to save into")
        self.folder_location_browse_button = Button(self, text = "Browse", command = self.select_folder)
        self.folder_location_browse_button.grid(row = 0, column = 1)
        
        self.xy_coords_entry = Entry(self, width = 45)
        self.xy_coords_entry.grid(row = 1, column = 0)
        self.xy_coords_entry.insert(END, "Location of the XY coordinates csv file (unaltered)")
        self.xy_coords_browse_button = Button(self, text = "Browse", command = self.select_xy_coords)
        self.xy_coords_browse_button.grid(row = 1, column = 1)        

        self.settings_entry = Entry(self, width = 45)
        self.settings_entry.grid(row = 2, column = 0)
        self.settings_entry.insert(END, "Location of the settings txt file (unaltered)")
        self.settings_browse_button = Button(self, text = "Browse", command = self.select_settings)
        self.settings_browse_button.grid(row = 2, column = 1)

        self.start_analysis_button = Button(self, text = "Start Analysis", command = self.start_analysis)
        self.start_analysis_button.grid(row = 8, column = 0, sticky = "E")

        self.cancel_button = Button(self, text = "Cancel", command = self.destroy)
        self.cancel_button.grid(row = 8, column = 1)

        self.selected_folder = None
        self.selected_xy_coords = None
        self.selected_settings = None

        self.frame_rate = None
        self.phase_number = None
        self.outer_roi_x = None
        self.outer_roi_y = None
        self.inner_roi_percentage = None
        self.scale_mm_pix = None
        self.phase_time = None

        self.xy_data_temp = AutoVivification()

    def select_folder(self):
        temp = tkFileDialog.askdirectory(initialdir = os.path.expanduser('~/Desktop'), title = "Please select the folder that will contain the analysed files from the program.")
        temp = str(temp)
        if len(temp) > 0:
            self.folder_location_entry.delete(0, END)
            self.folder_location_entry.insert(END, temp)

    def select_xy_coords(self):
        temp = tkFileDialog.askopenfilename(initialdir = os.path.expanduser('~/Desktop/'))
        temp = str(temp)
        if len(temp) > 0:
            self.xy_coords_entry.delete(0, END)
            self.xy_coords_entry.insert(END, temp)

    def select_settings(self):
        temp = tkFileDialog.askopenfilename(initialdir = os.path.expanduser('~/Desktop/'))
        temp = str(temp)
        if len(temp) > 0:
            self.settings_entry.delete(0, END)
            self.settings_entry.insert(END, temp)

    def start_analysis(self):
        self.selected_folder = str(self.folder_location_entry.get())
        self.selected_xy_coords = str(self.xy_coords_entry.get())
        self.selected_settings = str(self.settings_entry.get())
        
        if self.selected_folder:
            if os.path.exists(self.selected_folder):
                if ".csv" in self.selected_xy_coords.split("/")[-1] and ("xydata" in self.selected_xy_coords.split("/")[-1] or "xy_data" in self.selected_xy_coords.split("/")[-1]):
                    if os.path.isfile(self.selected_xy_coords):                    
                        if ".txt" in self.selected_settings.split("/")[-1] and "settings" in self.selected_settings.split("/")[-1] and "P" in self.selected_settings.split("/")[-1] and "sec" in self.selected_settings.split("/")[-1]:
                            if os.path.isfile(self.selected_settings):
                                real_deal = ""
                                starter = 0
                                while True:
                                    try:
                                        real_deal += str(int((self.selected_settings.split("/")[-1]).split("P")[-1][starter]))
                                        starter += 1
                                    except:
                                        if starter == 0:
                                            stop = True
                                        else:                                            
                                            stop = False
                                        break
                                if stop:
                                    self.phase_number = None
                                else:
                                    self.phase_number = int(real_deal)
                                real_deal = ""
                                starter = -2
                                while True:
                                    try:
                                        real_deal += str(int((self.selected_settings.split("/")[-1]).split("sec")[0][starter]))
                                        starter -= 1
                                    except:
                                        if starter == -2:
                                            stop = True
                                        else:
                                            stop = False
                                        break
                                if stop:
                                    self.phase_time = None
                                else:
                                    self.phase_time = int(real_deal[-1::-1])
                                temp_read = open(self.selected_settings, 'rU')                                
                                for line in temp_read:
                                    if "Frame rate" in line:
                                        real_deal = ""
                                        starter = 1
                                        while True:
                                            try:
                                                real_deal += str(int(line.split("=")[-1][starter]))
                                                starter += 1
                                            except:
                                                if starter == 1:
                                                    stop = True
                                                else:                                            
                                                    stop = False
                                                break
                                        if stop:
                                            self.frame_rate = None
                                        else:
                                            self.frame_rate = int(real_deal)
                                    if "Outer ROI X" in line:
                                        real_deal = ""
                                        starter = 1
                                        while True:
                                            try:
                                                real_deal += str(int(line.split("=")[-1][starter]))
                                                starter += 1
                                            except:
                                                if starter == 1:
                                                    stop = True
                                                else:                                            
                                                    stop = False
                                                break
                                        if stop:
                                            self.outer_roi_x = None
                                        else:
                                            self.outer_roi_x = int(real_deal)
                                    if "Outer ROI Y" in line:
                                        real_deal = ""
                                        starter = 1
                                        while True:
                                            try:
                                                real_deal += str(int(line.split("=")[-1][starter]))
                                                starter += 1
                                            except:
                                                if starter == 1:
                                                    stop = True
                                                else:                                            
                                                    stop = False
                                                break
                                        if stop:
                                            self.outer_roi_y = None
                                        else:
                                            self.outer_roi_y = int(real_deal)
                                    if "Inner ROI" in line:
                                        real_deal = ""
                                        starter = 1
                                        while True:
                                            try:
                                                real_deal += str(int(line.split("=")[-1][starter]))
                                                starter += 1
                                            except:
                                                if starter == 1:
                                                    stop = True
                                                else:                                            
                                                    stop = False
                                                break
                                        if stop:
                                            self.inner_roi_percentage = None
                                        else:
                                            self.inner_roi_percentage = int(real_deal)
                                    if "mm/pixel" in line:
                                        real_deal = ""
                                        starter = -2
                                        while True:
                                            try:
                                                if str(line.split("mm/pixel")[0][starter]) == ".":
                                                    real_deal += str(line.split("mm/pixel")[0][starter])
                                                else:
                                                    real_deal += str(int(line.split("mm/pixel")[0][starter]))
                                                starter -= 1
                                            except:
                                                if starter == -2:
                                                    stop = True
                                                else:
                                                    stop = False
                                                break
                                        if stop:
                                            self.scale_mm_pix = None
                                        else:
                                            self.scale_mm_pix = float(real_deal[-1::-1])                                            
                                    if "Phase time" in line:
                                        real_deal = ""
                                        starter = 1
                                        while True:
                                            try:
                                                real_deal += str(int(line.split("=")[-1][starter]))
                                                starter += 1
                                            except:
                                                if starter == 1:
                                                    stop = True
                                                else:                                            
                                                    stop = False
                                                break
                                        if stop:
                                            self.phase_time = None
                                        else:
                                            self.phase_time = int(real_deal)
                                temp_read.close()
                                if not self.frame_rate or not self.phase_number or not self.outer_roi_x or not self.outer_roi_y or not self.scale_mm_pix or not self.phase_time:
                                    self.frame_rate = None
                                    self.phase_number = None
                                    self.outer_roi_x = None
                                    self.outer_roi_y = None
                                    self.inner_roi_percentage = None
                                    self.scale_mm_pix = None
                                    self.phase_time = None
                                    self.selected_settings = None
                                    self.settings_entry.delete(0, END)
                                    self.settings_entry.insert(END, "Location of the settings txt file (unaltered)")
                                else:
                                    try:
                                        self.phase_number = 1
                                        self.xy_data_temp = AutoVivification()
                                        self.xy_data_temp[self.phase_number][0] = (self.outer_roi_x, self.outer_roi_y, self.inner_roi_percentage, self.scale_mm_pix, self.phase_time)
                                        temp_excel = open(self.selected_xy_coords, 'rU')
                                        counter = 0
                                        for line in temp_excel:
                                            if counter == 0:
                                                pass
                                            elif counter % 2 == 1:
                                                listo = line.split(",")[2:]
                                                time = float(line.split(",")[1])
                                                for n in xrange(len(listo)):
                                                    listo[n] = (float(listo[n]),)
                                            elif counter % 2 == 0:
                                                pisto = (line.split(",")[2:])
                                                for n in xrange(len(listo)):
                                                    listo[n] += (float(pisto[n]),)
                                                for n in xrange(len(listo)):
                                                    listo[n] = (listo[n], 0, 0)
                                                self.xy_data_temp[self.phase_number][int(counter/2)] = (time, listo)
                                            counter += 1
                                        temp_excel.close()
                                        going = True
                                    except:
                                        self.xy_data_temp = None
                                        self.frame_rate = None
                                        self.phase_number = None
                                        self.outer_roi_x = None
                                        self.outer_roi_y = None
                                        self.inner_roi_percentage = None
                                        self.scale_mm_pix = None
                                        self.phase_time = None
                                        self.selected_settings = None
                                        self.selected_xy_coords = None
                                        self.xy_coords_entry.delete(0, END)
                                        self.xy_coords_entry.insert(END, "Location of the XY coordinates csv file (unaltered)")
                                        going = False
                                    if going:
                                        self.parent.clear_all()
                                        self.parent.framerates[self.phase_number] = self.frame_rate
                                        self.parent.positional_data = copy.deepcopy(self.xy_data_temp)
                                        self.parent.selected_folder = self.selected_folder
                                        to_convert = (str(datetime.now())[0:-7]).split(":")
                                        converted = ""
                                        for n in to_convert:
                                            converted += n + "-"
                                        datentime = converted[0:-1]
                                        self.parent.folder_name = self.selected_folder + "/ZTrack " + datentime
                                        self.parent.folder_name_small = "ZTrack " + datentime
                                        os.makedirs(self.parent.folder_name)
                                        self.parent.start_analysis()
                                        self.destroy()
                            else:
                                self.selected_settings = None
                                self.settings_entry.delete(0, END)
                                self.settings_entry.insert(END, "Location of the settings txt file (unaltered)")
                        else:
                            self.selected_settings = None
                            self.settings_entry.delete(0, END)
                            self.settings_entry.insert(END, "Location of the settings txt file (unaltered)")
                    else:
                        self.selected_xy_coords = None
                        self.xy_coords_entry.delete(0, END)
                        self.xy_coords_entry.insert(END, "Location of the XY coordinates csv file (unaltered)")
                else:
                    self.selected_xy_coords = None
                    self.xy_coords_entry.delete(0, END)
                    self.xy_coords_entry.insert(END, "Location of the XY coordinates csv file (unaltered)")
            else:
                self.selected_folder = None
                self.folder_location_entry.delete(0, END)
                self.folder_location_entry.insert(END, "Location of the folder you wish to save into")
        else:
            self.folder_location_entry.delete(0, END)
            self.folder_location_entry.insert(END, "Location of the folder you wish to save into")

root = Tk()
app = Controller(root)
root.mainloop()
