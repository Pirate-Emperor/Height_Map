import os
os.system('mode con: cols=100 lines=60')
from bs4 import BeautifulSoup
import requests
import sys
from prettytable import *
from os import walk
from screeninfo import get_monitors

import math
import numpy as np
import matplotlib.pyplot as plt

from tkinter import *
import tkinter.font as TkFont

import json
# pip install pillow
from PIL import Image, ImageTk, ImageMath
Image.MAX_IMAGE_PIXELS = 1000000000
import PIL.ImageGrab as ImageGrab

import matplotlib as mpl
import matplotlib.pyplot as plt





class Window(Frame):
    def __init__(self, master=None, map=None, pixel_width=None, restore_session=None, subwindow=None):

        self.pixel_width = pixel_width
        self.subwindow = subwindow

        self.offset_x = 0
        self.offset_y = 0

        #self.font = 'Arial 12'
        PIXEL_HEIGHT = 15
        self.font = TkFont.Font(size = PIXEL_HEIGHT)

        Frame.__init__(self, master)
        self.master = master
        self._geom='200x200+0+0'
        master.bind('<Escape>',self.toggle_geom)
        master.bind("<Button 1>",self.left_click)
        master.bind('<B3-Motion>', self.right_click_drag)
        master.bind("<Button 3>",self.right_click)
        master.bind("<Motion>", self.getPosition)

        master.bind("q",self.recenter)
        master.bind("e",self.save_png)
        master.bind("c",self.crop_map)

        master.bind("w",self.go_top)
        master.bind("a",self.go_left)
        master.bind("s",self.go_bottom)
        master.bind("d",self.go_right)

        self.canvas = Canvas(self, width=800, height=800, bg='grey')
        self.canvas.pack(fill=BOTH, expand=1)
        self.pack(fill=BOTH, expand=1)

        self.map = map
        print('LOADING   \"' + map + '\" ', end=' ', flush=True)
        self.im = Image.open(map)
        print(f"Shape: {self.im.size}")
        self.data = self.im.load()

        print(self.data[0,0])
        
        self.data_min, self.data_max = self.im.getextrema()
        self.reference_offset = 1737400 # from LOLA label
        self.planet_diameter = (self.reference_offset + self.data_min) * 2
        self.scaling_factor = 0.05   # from LOLA label

        print(self.im.size, end=' ')
        map_res_x, map_res_y = self.im.size
        if self.subwindow:
            self.zoom = int((max(map_res_x,map_res_y) / 2500)*100)/100
        else:
            self.zoom = int((max(map_res_x,map_res_y) / 4000)*100)/100

        print('zoom', end='=')
        print(self.zoom, end=' ')

        print('extrema', end='=')
        print(self.im.getextrema())

        if not restore_session:
            print('RESIZE    \"session/display.png\" ', end='', flush=True)
            im2 = ImageMath.eval('im/256', {'im':self.im}).convert('L')

            display = im2.resize(tuple([int(x/self.zoom)  for x in self.im.size]))#.convert('RGB')
            print('done.')
            print('CONTRAST  \"session/display.png\" ', end='', flush=True)
            display_edit = display.load()
            display_edit_min, display_edit_max = display.getextrema()
            for y in range(0,display.size[1]):
                for x in range(0,display.size[0]):
                    display_edit[x,y] = int(((display_edit[x,y] - display_edit_min) / (display_edit_max - display_edit_min))*255)
            print('done.')
            print('COLOUR    \"session/display.png\" ', end='', flush=True)
            cm_hot = mpl.cm.get_cmap('magma')
            #cm_hot = mpl.cm.get_cmap('plasma')
            #cm_hot = mpl.cm.get_cmap('inferno')
            im_edit = np.array(display)
            im_edit = cm_hot(im_edit)
            im_edit = np.uint8(im_edit * 255)
            im_edit = Image.fromarray(im_edit)
            if self.subwindow:
                im_edit.save('session/display_crop.png')
            else:
                im_edit.save('session/display.png')
            print('done.')

            legend_array = [range(0,255)]*20
            im_legend = cm_hot(legend_array)
            im_legend = np.uint8(im_legend * 255)
            im_legend = Image.fromarray(im_legend)
            im_legend.save('session/legend.png')

        if self.subwindow:
            self.canvas.image = ImageTk.PhotoImage(Image.open('session/display_crop.png'))
        else:
            self.canvas.image = ImageTk.PhotoImage(Image.open('session/display.png'))

        # self.canvas.controls = ImageTk.PhotoImage(Image.open('controls.png'))

        self.display_image = self.canvas.create_image((0,0), image=self.canvas.image, anchor='nw')

        if not self.subwindow:
            self.display_grid_x = self.canvas.create_line(0,int(self.canvas.image.height()/2), self.canvas.image.width(),int(self.canvas.image.height()/2), fill="black",  width=1)
            self.display_grid_y = self.canvas.create_line(int(self.canvas.image.width()/2),0, int(self.canvas.image.width()/2),self.canvas.image.height(), fill="black",  width=1)


        # self.canvas.create_image(30,30, image=self.canvas.controls, anchor='nw')

        self.canvas.legend = ImageTk.PhotoImage(Image.open('session/legend.png'))
        self.canvas.create_image(root.winfo_screenwidth()-20,root.winfo_screenheight()-20-280, image=self.canvas.legend, anchor='se')

        self.canvas.create_line(root.winfo_screenwidth()-19,root.winfo_screenheight()-67-280, root.winfo_screenwidth()-19,root.winfo_screenheight()-20-280, fill="white",  width=2)
        self.canvas.create_rectangle(root.winfo_screenwidth()-20,root.winfo_screenheight()-47-280, root.winfo_screenwidth()-108,root.winfo_screenheight()-67-280, fill="white", outline='white')
        self.canvas.create_text(root.winfo_screenwidth()-65,root.winfo_screenheight()-57-280,fill="black", font=self.font,
                        text='{:.1f}'.format(((self.data_max - self.data_min)*self.scaling_factor)/1000)+' km', anchor='center')

        self.canvas.create_line(root.winfo_screenwidth()-275,root.winfo_screenheight()-67-280, root.winfo_screenwidth()-275,root.winfo_screenheight()-20-280, fill="white",  width=2)
        self.canvas.create_rectangle(root.winfo_screenwidth()-259,root.winfo_screenheight()-47-280, root.winfo_screenwidth()-275,root.winfo_screenheight()-67-280, fill="white", outline='white')
        self.canvas.create_text(root.winfo_screenwidth()-267,root.winfo_screenheight()-57-280,fill="black", font=self.font,
                        text='0', anchor='center')

        self.canvas.create_line(root.winfo_screenwidth()-20,root.winfo_screenheight()-95-280, root.winfo_screenwidth()-170, root.winfo_screenheight()-95-280, fill="white",  width=2)
        self.canvas.create_line(root.winfo_screenwidth()-20,root.winfo_screenheight()-90-280, root.winfo_screenwidth()-20, root.winfo_screenheight()-100-280, fill="white",  width=2)
        self.canvas.create_line(root.winfo_screenwidth()-170,root.winfo_screenheight()-90-280, root.winfo_screenwidth()-170, root.winfo_screenheight()-100-280, fill="white", width=2)
        self.canvas.create_rectangle(root.winfo_screenwidth()-45,root.winfo_screenheight()-103-280, root.winfo_screenwidth()-145,root.winfo_screenheight()-123-280, fill="white", outline='white')
        self.canvas.create_text(root.winfo_screenwidth()-95,root.winfo_screenheight()-113-280,fill="black", font=self.font,
                        text=str('{0:.4g}'.format((self.pixel_width*150*self.zoom)/1000))+' km', anchor='center')




        self.draw_line = None
        self.draw_result_box = None
        self.draw_result = None
        self.draw_dot_1 = None
        self.draw_dot_2 = None
        self.draw_dot_temp = None
        self.height_profile = None

        # Slope
        self.slope_profile = None

        self.new_dot = True
        self.crop_mode = False

        # jump to center
        self.center_x = int(self.canvas.image.width()/2) - int(root.winfo_screenwidth()/2)
        self.center_y = int(self.canvas.image.height()/2) - int(root.winfo_screenheight()/2)
        self.offset_x = -self.center_x
        self.offset_y = -self.center_y
        self.move_image(-self.center_x,-self.center_y)

    def right_click_drag(self,event):
        delta_x = self.old_drag_x - event.x
        delta_y = self.old_drag_y - event.y
        self.offset_x = self.offset_x - delta_x
        self.offset_y = self.offset_y - delta_y
        self.move_image(-delta_x,-delta_y)
        self.old_drag_x = event.x
        self.old_drag_y = event.y

    def save_png(self,event):
        #print(tuple((root.winfo_screenwidth(),root.winfo_screenheight())))
        ImageGrab.grab(bbox=(0, 0, root.winfo_screenwidth(), root.winfo_screenheight())).save("screenshot.png")
        print('SAVED     \"screenshot.png\"')

    def recenter(self,event):
        move_x = -(self.offset_x + self.center_x)
        move_y = -(self.offset_y + self.center_y)
        self.offset_x = self.offset_x + move_x
        self.offset_y = self.offset_y + move_y
        self.move_image(move_x,move_y)
        print('MOVE       re-centered ')

    def getPosition(self,event):
       if self.crop_mode and not self.new_dot:
           x = root.winfo_pointerx()-root.winfo_rootx()
           y = root.winfo_pointery()-root.winfo_rooty()
           if self.draw_rectangle is not None:
               self.canvas.delete(self.draw_rectangle)
           self.draw_rectangle = self.canvas.create_rectangle(self.crop_start_x + self.offset_x, self.crop_start_y + self.offset_y, x, y, outline="white")
       pass

    def crop_map(self,event):
        if self.subwindow:
            print('DENIED:      to crop again go back to main map with ESC')
        else:
            print('CROP MODE  Select rectangle:', end=' ',flush=True)
            self.draw_rectangle = None
            self.crop_mode = True
            self.new_dot = True
            self.canvas.config(cursor="tcross")

    def go_left(self,event):
        self.offset_x = self.offset_x + 200
        self.move_image(200,0)

    def go_right(self,event):
        self.offset_x = self.offset_x - 200
        self.move_image(-200,0)

    def go_top(self,event):
        self.offset_y = self.offset_y + 200
        self.move_image(0,200)

    def go_bottom(self,event):
        self.offset_y = self.offset_y - 200
        self.move_image(0,-200)


    def move_image(self,x,y):
        self.canvas.move(self.display_image, x, y)
        if not self.subwindow:
            self.canvas.move(self.display_grid_x, x, y)
            self.canvas.move(self.display_grid_y, x, y)

        if self.draw_dot_temp:
            self.canvas.move(self.draw_dot_temp, x, y)
        if self.draw_line:
            self.canvas.move(self.draw_line, x, y)
            self.canvas.move(self.draw_dot_1, x, y)
            self.canvas.move(self.draw_dot_2, x, y)
            self.canvas.move(self.draw_result, x, y)
            self.canvas.move(self.draw_result_box, x, y)


    def toggle_geom(self,event):
        print('ESC')
        self.master.destroy()
        try:
            self.master.update()
        except Exception:
            pass

    def left_click(self, content):
          global x,y
          x = content.x
          y = content.y
          #print(tuple((x,y)))
          if self.crop_mode:
              self.calc_crop(x,y)
          else:
              self.calc_line(x,y)


    def right_click(self,event):
          self.old_drag_x = event.x
          self.old_drag_y = event.y

    def create_crop_map(self,start_x,start_y,end_x,end_y):
        map_name = self.map[:len(self.map)-4] + '_crop.png'
        print('SAVING    \"'+ map_name + '\"')
        self.im.crop((start_x, start_y, end_x, end_y)).save(map_name)

        self.newWindow = Toplevel(root)
        subapp = Window(self.newWindow, map_name, pixel_width=self.pixel_width, restore_session=False, subwindow=True)

        self.newWindow.attributes('-fullscreen', True)
        self.newWindow.wm_title("Lunar Heightmap Calculator")
        self.newWindow.focus()
        self.newWindow.mainloop()



    def calc_crop(self,x,y):
        global start_x, start_y

        if self.new_dot:
            self.crop_start_x = x - self.offset_x
            self.crop_start_y = y - self.offset_y
            start_x = int((x - self.offset_x)*self.zoom)
            start_y = int((y - self.offset_y)*self.zoom)
            self.new_dot = False
            print('First ' + str(tuple((start_x,start_y))), end=' ',flush=True)
        else:
            end_x = int((x - self.offset_x)*self.zoom)
            end_y = int((y - self.offset_y)*self.zoom)
            self.crop_mode = False
            self.new_dot = True
            x1 = min(start_x,end_x)
            x2 = max(start_x,end_x)
            y1 = min(start_y,end_y)
            y2 = max(start_y,end_y)
            self.canvas.delete(self.draw_rectangle)
            self.canvas.config(cursor="")
            print('Second ' + str(tuple((end_x,end_y))))
            self.create_crop_map(x1,y1,x2,y2)

    def calc_line(self,x,y):
        print(x,y)
        global start_x, start_y

        if self.new_dot:
            start_x = x - self.offset_x
            start_y = y - self.offset_y
            self.draw_dot_temp = self.canvas.create_oval(x+5, y+5, x-5, y-5, fill="white", outline="black")
            self.new_dot = False
        else:
            end_x = x - self.offset_x
            end_y = y - self.offset_y
            if ((start_x != end_x ) and (start_y != end_y )):
                # check if its inside the picture dimensions - overflow otherwise
                max_x, max_y = self.im.size

                if (start_x*self.zoom < 0) or (start_y*self.zoom < 0) or (end_x*self.zoom < 0) or (end_y*self.zoom < 0) or (start_x*self.zoom > max_x) or (start_y*self.zoom > max_y) or (end_x*self.zoom > max_x) or (end_y*self.zoom > max_y):
                    print('ERROR: OUTSIDE OF PICTURE DIMENSIONS')
                    self.canvas.delete(self.draw_dot_temp)
                else:
                    self.get_line(start_x,start_y,end_x,end_y)
                self.new_dot = True

    def clear_results(self):

        if self.draw_line is not None:
            self.canvas.delete(self.draw_line)
        if self.draw_result_box  is not None:
            self.canvas.delete(self.draw_result_box)
        if self.draw_result is not None:
            self.canvas.delete(self.draw_result)
        if self.draw_dot_1 is not None:
            self.canvas.delete(self.draw_dot_1)
        if self.draw_dot_2 is not None:
            self.canvas.delete(self.draw_dot_2)
        if self.draw_dot_temp is not None:
            self.canvas.delete(self.draw_dot_temp)

        if self.height_profile is not None:
            self.canvas.delete(self.height_profile_element)

            self.canvas.delete(self.height_label_line)
            self.canvas.delete(self.height_label_box)
            self.canvas.delete(self.height_label_text)

            self.canvas.delete(self.zero_label_line)
            self.canvas.delete(self.zero_label_box)
            self.canvas.delete(self.zero_label_text)

            self.canvas.delete(self.flat_label_line)
            self.canvas.delete(self.flat_label_box)
            self.canvas.delete(self.flat_label_text)

    def get_line(self,start_x,start_y,end_x,end_y):

        self.clear_results()

        self.draw_line = self.canvas.create_line(start_x+self.offset_x, start_y+self.offset_y, end_x+self.offset_x, end_y+self.offset_y, fill="white", width=3)

        self.draw_dot_1 = self.canvas.create_oval(start_x+self.offset_x+5, start_y+self.offset_y+5, start_x+self.offset_x-5, start_y+self.offset_y-5, fill="white", outline="black")
        self.draw_dot_2 = self.canvas.create_oval(end_x+self.offset_x+5, end_y+self.offset_y+5, end_x+self.offset_x-5, end_y+self.offset_y-5, fill="white", outline="black")

        start_x_display = start_x
        start_y_display = start_y
        end_x_display = end_x
        end_y_display = end_y
        delta_x_display = end_x_display - start_x_display
        delta_y_display = end_y_display - start_y_display

        # adjust for zoom
        # start_x = start_x_display * self.zoom
        # start_y = start_y_display * self.zoom
        # end_x = end_x_display * self.zoom
        # end_y = end_y_display * self.zoom
        start_x = start_x_display 
        start_y = start_y_display
        end_x = end_x_display
        end_y = end_y_display


        delta_x = end_x - start_x
        delta_y = end_y - start_y

        # NEW CALCULATION METHOD

        self.sample_length = 1 # in pixel

        #alpha = mp.atan(delta_x/delta_y)
        alpha = math.atan(delta_x/delta_y)

        x_step_size = math.sin(alpha) * self.sample_length
        y_step_size = math.cos(alpha) * self.sample_length

        # recover correct direction
        if delta_x > 0:
            x_step_size = abs(x_step_size)
        else:
            x_step_size = abs(x_step_size) * (-1)

        if delta_y > 0:
            y_step_size = abs(y_step_size)
        else:
            y_step_size = abs(y_step_size) * (-1)

        flat_length = math.sqrt(delta_x**2 + delta_y**2)
        flat_length_meter = math.sqrt((delta_x * self.pixel_width)**2 + (delta_y * self.pixel_width)**2)

        steps = int(flat_length / self.sample_length)

        walk_x = start_x
        walk_y = start_y

        print(f"Display Start: ({start_x_display},{start_y_display})\n End: ({end_x_display},{end_y_display})")
        print(f"Start: ({start_x},{start_y})\n End: ({end_x},{end_y})")
        point_list = []
        # picture data features (y,x)
        point_list.append(tuple((start_x, start_y)))
        for i in range(0,steps):
            walk_x = walk_x + x_step_size
            walk_y = walk_y + y_step_size
            point_list.append(tuple((walk_x, walk_y)))

        point_list.append(tuple((end_x, end_y)))


        # BILINEAR INTERPOLATION
        #        x_1          x_2
        # y_1   P_11          P_21
        #
        #                  P
        #
        # y_2   P_12          P_22

        point_value_list = []

        for i in range(0,len(point_list)):

            P_x = point_list[i][0]
            P_y = point_list[i][1]

            P_11 = tuple((math.floor(point_list[i][0]),math.floor(point_list[i][1])))
            P_21 = tuple((math.ceil(point_list[i][0]),math.floor(point_list[i][1])))
            P_12 = tuple((math.floor(point_list[i][0]),math.ceil(point_list[i][1])))
            P_22 = tuple((math.ceil(point_list[i][0]),math.ceil(point_list[i][1])))

            x_1 = math.floor(point_list[i][0])
            x_2 = math.ceil(point_list[i][0])
            y_1 = math.floor(point_list[i][1])
            y_2 = math.ceil(point_list[i][1])

            interpolated_height_value = self.data[point_list[i]]
            point_value_list.append(tuple((P_x, P_y, interpolated_height_value)))
            
            # if ((x_2 - x_1)*(y_2 - y_1)) == 0:
            #     point_value_list.append(tuple((P_x, P_y, (self.data[point_list[i]]  * self.scaling_factor) )))
            # else:
            #     # weighted parts
            #     w_1 = ( ((x_2 - P_x)*(y_2 - P_y)) / ((x_2 - x_1)*(y_2 - y_1)) ) * self.data[P_11]
            #     w_2 = ( ((P_x - x_1)*(y_2 - P_y)) / ((x_2 - x_1)*(y_2 - y_1)) ) * self.data[P_21]
            #     w_3 = ( ((x_2 - P_x)*(P_y - y_1)) / ((x_2 - x_1)*(y_2 - y_1)) ) * self.data[P_12]
            #     w_4 = ( ((P_x - x_1)*(P_y - y_1)) / ((x_2 - x_1)*(y_2 - y_1)) ) * self.data[P_22]

            #     interpolated_height_value = (w_1 + w_2 + w_3 + w_4) * self.scaling_factor

            #     point_value_list.append(tuple((P_x, P_y, interpolated_height_value)))

        vector_list = []

        for i in range(1,len(point_value_list)):
            previous = np.array([point_value_list[i-1]])
            current = np.array([point_value_list[i]])
            delta = current-previous
            delta[0][0] = delta[0][0] * self.pixel_width
            delta[0][1] = delta[0][1] * self.pixel_width
            vector_list.append(delta[0])

        #print(vector_list)

        flat_vector_list = []

        for i in range(len(vector_list)):
            flat_vector_list.append(np.array((vector_list[i][0],vector_list[i][1])))


        # VECTOR NORM
        meter_count = 0
        flat_meter_count = 0

        for i in range(0,len(vector_list)):
            meter_count = meter_count + np.linalg.norm(vector_list[i])
            flat_meter_count = flat_meter_count + np.linalg.norm(flat_vector_list[i])


        # CURVATURE DISTORTION
        circle_segment = self.planet_diameter * math.asin(flat_length_meter/self.planet_diameter)
        #distortion = mp.mpf((1 - (flat_length_meter/circle_segment)) * 100)
        distortion = (1 - (flat_length_meter/circle_segment)) * 100


        # INFO OUTPUT
        print('DISTANCE_MAPPING    ',end='')
        print(f'{meter_count:,.0f}' + ' m')
        #print('             with ~' + f'{float(distortion):.4f}' + '% curvature distortion (' + f'{float(flat_length_meter):.4f}' + ' m flat vs. ' + f'{float(circle_segment):.4f}' + ' m curved)')
        #edge_distortion = abs((1 - (flat_length_meter/flat_meter_count)) *100)
        #print('             with ~' + f'{float(edge_distortion):.4f}' + '% edge distortion left (' + f'{float(flat_length_meter):.4f}' + ' m flat vs. ' + f'{float(flat_meter_count):.4f}' + ' m calculated flat)')

        result_text = f'{(meter_count):,.0f}'
        px_space = [0,10,30,40,45,50,55,65,70,75,90]
        self.draw_result_box = self.canvas.create_rectangle(start_x_display+self.offset_x+(delta_x_display*0.5)-(px_space[len(result_text)]), start_y_display+self.offset_y+(delta_y_display*0.5)-14, start_x_display+self.offset_x+(delta_x_display*0.5)+px_space[len(result_text)], start_y_display+self.offset_y+(delta_y_display*0.5)+14, fill='white')
        self.draw_result = self.canvas.create_text(start_x_display+self.offset_x+(delta_x_display*0.5), start_y_display+self.offset_y+(delta_y_display*0.5),fill="black",font=self.font, text=result_text+' m')

        # height profile plot

        point_only_value_list = []
        for i in range(0,len(point_value_list)):
            point_only_value_list.append(point_value_list[i][2])
        

        height_difference = max(point_only_value_list) - min(point_only_value_list)

        x_plot = np.linspace(0,flat_meter_count,len(point_only_value_list))

        fig = plt.figure(figsize=(10, 2), dpi=120)
        ax = plt.axes()
        ax.plot(x_plot, point_only_value_list,'w')
        #plt.gca().set_axis_off()
        plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0,
                    hspace = 0, wspace = 0)
        plt.margins(0,0.01)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')
        fig.savefig("session/height_profile.png", transparent=True,  bbox_inches = 'tight')
        plt.close()

        self.height_profile = ImageTk.PhotoImage(Image.open('session/height_profile.png'))
        self.height_profile_element = self.canvas.create_image(root.winfo_screenwidth()-12,root.winfo_screenheight()-21, image=self.height_profile, anchor='se')

        self.height_label_line = self.canvas.create_line(root.winfo_screenwidth()-1250,root.winfo_screenheight()-278, root.winfo_screenwidth()-1222,root.winfo_screenheight()-278, fill="white",  width=2)
        self.height_label_box = self.canvas.create_rectangle(root.winfo_screenwidth()-1250-70,root.winfo_screenheight()-279, root.winfo_screenwidth()-1230,root.winfo_screenheight()-279+24, fill="white", outline='white')
        self.height_label_text = self.canvas.create_text(root.winfo_screenwidth()-1250-25,root.winfo_screenheight()-278+12,fill="black", font=self.font,
                        text=f'{height_difference:.0f}' + ' m', anchor='center')

        self.zero_label_line = self.canvas.create_line(root.winfo_screenwidth()-1222,root.winfo_screenheight()-8, root.winfo_screenwidth()-1222,root.winfo_screenheight()-38, fill="white",  width=2)
        self.zero_label_box = self.canvas.create_rectangle(root.winfo_screenwidth()-1222,root.winfo_screenheight()-9, root.winfo_screenwidth()-1200,root.winfo_screenheight()-33, fill="white", outline='white')
        self.zero_label_text = self.canvas.create_text(root.winfo_screenwidth()-1212,root.winfo_screenheight()-20,fill="black", font=self.font,
                        text='0', anchor='center')

        px_space = [0,15,35,45,50,68,85,95,100,110,140]
        result_text_flat = f'{float(flat_length_meter):,.0f}'

        self.flat_label_line = self.canvas.create_line(root.winfo_screenwidth()-23,root.winfo_screenheight()-8, root.winfo_screenwidth()-23,root.winfo_screenheight()-38, fill="white",  width=2)
        self.flat_label_box = self.canvas.create_rectangle(root.winfo_screenwidth()-50-px_space[len(result_text_flat)],root.winfo_screenheight()-9, root.winfo_screenwidth()-23,root.winfo_screenheight()-33, fill="white", outline='white')
        self.flat_label_text = self.canvas.create_text(root.winfo_screenwidth()-32,root.winfo_screenheight()-20,fill="black", font=self.font,
                        text=result_text_flat + ' m', anchor='e')

        # Slope Profile Plot
        slope_const = 180/math.pi
        slope_list = []
        for i in range(0,len(point_only_value_list)-1):
            slope_list.append(slope_const*math.atan((point_only_value_list[i+1]-point_only_value_list[i])/(x_plot[i+1]-x_plot[i])))
        
        x_plot = np.linspace(0,flat_meter_count,len(slope_list))
        fig = plt.figure(figsize=(10, 2), dpi=120)
        ax = plt.axes()
        ax.plot(x_plot, slope_list,'w')
        #plt.gca().set_axis_off()
        plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0,
                    hspace = 0, wspace = 0)
        plt.margins(0,0.01)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')
        fig.savefig("session/slope_profile.png", transparent=True,  bbox_inches = 'tight')
        plt.close()

        slope_difference = max(slope_list) - min(slope_list)
        max_slope= max(slope_list)
        min_slope= min(slope_list)
        slope_profile_width = 300
        self.slope_profile = ImageTk.PhotoImage(Image.open('session/slope_profile.png'))
        self.slope_profile_element = self.canvas.create_image(root.winfo_screenwidth()-12,1, image=self.slope_profile, anchor='ne')

        self.slope_label_line = self.canvas.create_line(root.winfo_screenwidth()-1250,slope_profile_width-278, root.winfo_screenwidth()-1222,slope_profile_width-278, fill="white",  width=2)
        self.slope_label_box = self.canvas.create_rectangle(root.winfo_screenwidth()-1250-70,slope_profile_width-279, root.winfo_screenwidth()-1230,slope_profile_width-279+24, fill="white", outline='white')
        self.slope_label_text = self.canvas.create_text(root.winfo_screenwidth()-1250-25,slope_profile_width-278+12,fill="black", font=self.font,
                        text=f'{max_slope:.0f}' + ' deg', anchor='center')

        self.slope_zero_label_line = self.canvas.create_line(root.winfo_screenwidth()-1222,slope_profile_width-8, root.winfo_screenwidth()-1222,slope_profile_width-38, fill="white",  width=2)
        self.slope_zero_label_box = self.canvas.create_rectangle(root.winfo_screenwidth()-1222,slope_profile_width-9, root.winfo_screenwidth()-1200,slope_profile_width-33, fill="white", outline='white')
        self.slope_zero_label_text = self.canvas.create_text(root.winfo_screenwidth()-1212,slope_profile_width-20,fill="black", font=self.font,
                        text=f'{min_slope:.0f}' + ' deg', anchor='center')

        px_space = [0,15,35,45,50,68,85,95,100,110,140]
        result_text_flat = f'{float(flat_length_meter):,.0f}'

        self.slope_flat_label_line = self.canvas.create_line(root.winfo_screenwidth()-23,slope_profile_width-8, root.winfo_screenwidth()-23,slope_profile_width-38, fill="white",  width=2)
        self.slope_flat_label_box = self.canvas.create_rectangle(root.winfo_screenwidth()-50-px_space[len(result_text_flat)],slope_profile_width-9, root.winfo_screenwidth()-23,slope_profile_width-33, fill="white", outline='white')
        self.slope_flat_label_text = self.canvas.create_text(root.winfo_screenwidth()-32,slope_profile_width-20,fill="black", font=self.font,
                        text=result_text_flat + ' m', anchor='e')


def download():
    url = 'http://imbrium.mit.edu/DATA/LOLA_GDR/POLAR/JP2/'
    ext = 'JP2'

    print('Select map of interest')
    print('Preview: http://imbrium.mit.edu/BROWSE/LOLA_GDR/POLAR/SOUTH_POLE/')
    print()

    def listFD(url, ext=''):
        page = requests.get(url).text
        #print(page)
        soup = BeautifulSoup(page, 'html.parser')
        # url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)
        return [ node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]

    table = PrettyTable(['FILE NAMES'], horizontal_char='─', vertical_char='│', right_junction_char='┤',left_junction_char='├',top_right_junction_char='┐',top_left_junction_char='┌',bottom_right_junction_char='┘',bottom_left_junction_char='└',header=False)
    table.align['FILE NAMES'] = 'l'

    for file in listFD(url, ext):
        if file[0:4] == 'LDEM':
            table.add_row([file])

    print(table)
    print()
    file_name = input('Download File: ')


    with open('maps/' + file_name, "wb") as f:
        print("Downloading %s" % file_name)
        response = requests.get(url+file_name, stream=True)
        total_length = response.headers.get('content-length')

        if total_length is None: # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
                sys.stdout.write(' ' + "{:.2f}".format(dl/(1024*1024)) + ' MB' + ' / ' + "{:.2f}".format(total_length/(1024*1024)) + ' MB')
                sys.stdout.flush()


    print()
    print('maps/' + file_name, end=' ', flush=True)
    im = Image.open('maps/' + file_name)

    image_width, image_height = im.size
    print(f"\nWidth = {image_width}\nHeight = {image_height}")

    print('opened.', end=' ', flush=True)
    print('converting to .png', end=' ', flush=True)
    file_name_new = str(file_name[:len(file_name)-4])+'.png'
    im.save('maps/' + file_name_new)
    print('saved.')
    im.close()

    os.remove('maps/' + file_name)
    print('cleanup: ' + 'maps/' + file_name + ' deleted.')
    print()

    return file_name_new

def pixel_width(config, map):

    pw_M = map.split("_")[2].split(".")[0] # [LDEM, 45S, [400M,png]]
    pixel_width =  int(pw_M[:len(pw_M)-1]) # 400M -> 400

    config['map'] = map
    config['pixel_width'] = pixel_width

    with open('session/config.json', 'w') as f:
        json.dump(config, f)
    print('SAVED preset into session/config.json')

    return pixel_width

# ENTRY
# HEIGHTMAP PROPERTY SETTINGS

if not os.path.exists('maps') or not os.path.exists('session'):
    fresh_start = True
    if not os.path.exists('maps'):
        os.makedirs('maps')
    if not os.path.exists('session'):
        os.makedirs('session')
    config = {
    "map": "DOWNLOAD MORE",
    "pixel_width": 0,
    }
    with open('session/config.json', 'w') as f:
        json.dump(config, f)
else:
    fresh_start = False

with open('session/config.json', 'r') as f:
    config = json.load(f)

if config['map'] != "DOWNLOAD MORE":
    print('LOADED : ' + str(config))
    edit_input = input('Restore previous session? n/[y]: ')
    if edit_input == '' or edit_input == 'y':
        map = config['map']
        pixel_width = config['pixel_width']
        restore_session = True
    elif edit_input == 'n':
        print()
        map_table = PrettyTable(['AVAILABLE MAPS'] , horizontal_char='─', vertical_char='│', right_junction_char='┤',left_junction_char='├',top_right_junction_char='┐',top_left_junction_char='┌',bottom_right_junction_char='┘',bottom_left_junction_char='└',header=False)
        map_table.align['AVAILABLE MAPS'] = 'l'
        f = []
        for (dirpath, dirnames, filenames) in walk('./maps'):
            f.extend(filenames)
            break

        for file in f:
            if file[len(file)-4:len(file)] == '.png':
                map_table.add_row([file])
        map_table.add_row(['DOWNLOAD MORE'])
        print(map_table)
        select =  str(input('          Select map: '))
        if select == 'DOWNLOAD MORE':
            map = download()
        else:
            map = select
        pixel_width = pixel_width(config, map)
        restore_session = False
    else:
        sys.exit(0)
else:
    map = download()
    pixel_width = pixel_width(config, map)
    restore_session = False


for m in get_monitors():    # resets Windows DPI scaling
    print('',end='')


root = Tk()
root.tk.call('tk', 'scaling', 1.5)
app = Window(root, 'maps/' + map, pixel_width, restore_session, subwindow=False)

root.attributes('-fullscreen', True)
root.wm_title("Lunar Heightmap Calculator")
root.mainloop()
