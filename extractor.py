from PIL import Image
from skimage import color
from clusterer import *
import numpy as np

orig_term_colours={
    "color0":  "#000000",
    "color8":  "#555753",
    "color1":  "#ff6565",
    "color9":  "#ff8d8d",
    "color2":  "#93d44f",
    "color10": "#c8e7a8",
    "color3":  "#eab93d",
    "color11": "#ffc123",
    "color4":  "#204a87",
    "color12": "#3465a4",
    "color5":  "#ce5c00",
    "color13": "#f57900",
    "color6":  "#89b6e2",
    "color14": "#46a4ff",
    "color7":  "#cccccc",
    "color15": "#ffffff"
    }

def get_colours(file_name, thumb_size):
    img=Image.open(file_name)
    img.thumbnail(thumb_size)
    img=np.asarray(img)/255.
    img=color.rgb2lab(img)
    colours=[]
    for i in range(len(img)):
        for j in range(len(img[i])):
            colours.append((img[i][j][0], img[i][j][1], img[i][j][2]))
    return colours

def k_means_to_np_array(k_means_out):
    out_array=np.zeros((1, len(k_means_out), 3))
    for i in range(len(k_means_out)):
        for j in range(3):
            out_array[0][i][j]=k_means_out[i][j]
    return out_array

def extract_colours_from_image(file_name, num_colours, img_sample_size, min_distance=1):
    outed=k_means_to_np_array(k_means(get_colours(file_name, img_sample_size), num_colours, min_distance))
    outed=color.lab2rgb(outed)
    return_colours=[]
    for i in range(len(outed)):
        for j in range(len(outed[i])):
            return_colours.append([])
            for k in range(len(outed[i][j])):
                return_colours[j].append(int(np.round(outed[i][j][k]*255)))
    return return_colours

def scale_colours(colours, minval, maxval): 
    hcolours=[]
    for colour in colours:
        hcolours.append(rgb2hsv(colour))
    minv=min(hcolours, key=lambda x:x[2])[2]
    maxv=max(hcolours, key=lambda x:x[2])[2]
    for i in range(len(hcolours)):
        hcolours[i][2]=scale(hcolours[i][2], minv, maxv, minval, maxval)
    scaled_colours=[]
    for colour in hcolours:
        scaled_colours.append(hsv2rgb(colour))
    return scaled_colours


def rgb2hsv(colour):
    r=colour[0]/255.
    g=colour[1]/255.
    b=colour[2]/255.
    cmax=max(r, max(g, b))
    cmin=min(r, min(g, b))
    delta=cmax-cmin
    if delta==0: h=0
    else:
        if cmax==r: h=60.*(((g-b)/delta)%6.)
        elif cmax==g: h=60.*((b-r)/delta+2.)
        else: h=60.*((r-g)/delta+4.)

    if cmax==0: s=0.
    else: s=delta/cmax

    v=cmax
    return [h, s, v]

def find_closest(hex_col, colours):
    closest_dist=float('inf')
    closest=None
    for colour in colours:
        dist=distance(hex2rgb(hex_col), colour)
        if dist<closest_dist:
            closest_dist=dist
            closest=colour
    return closest

def hsv2rgb(colour):
    h, s, v=colour
    c=v*s
    x=c*(1-abs((h/60.)%2.-1))
    m=v-c
    if h>=0 and h<60.:
        r=c
        g=x
        b=0
    elif h>=60. and h<120.:
        r=x
        g=c
        b=0
    elif h>=120. and h<180.:
        r=0
        g=c
        b=x
    elif h>=180. and h<240.:
        r=0
        g=x
        b=c
    elif h>=240. and h<300.:
        r=x
        g=0
        b=c
    else:
        r=c
        g=0
        b=x
    return [int(round((r+m)*255.)), int(round((g+m)*255.)), int(round((b+m)*255.))]

def get_hue(colour):
    r, g, b = colour
    mini = min(r, min(g, b))
    maxi = max(r, max(g, b))
    if (maxi==mini): return int(round(360*r/255.))
    if maxi==r: hue = (g-b)/(maxi-mini)
    elif maxi==g: hue = 2.+(b-r)/(maxi-mini)
    else: hue = 4. + (r-g)/(maxi-mini)
    hue*=60
    if hue<0: hue+=360
    return int(round(hue))

def scale(v, vmin, vmax, mmin, mmax):
    return ((v-vmin)/(vmax-vmin)*(mmax-mmin)+mmin)

def hex2rgb(hex_string):
    return list(int(hex_string.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

def rgb2hex(colour):
    return "#%02x%02x%02x" % tuple(i for i in colour)

def prepare_for_terminal(file_name, separate_bnw=False):
    nums=16
    #if separate_bnw: nums=18
    colours=scale_colours(extract_colours_from_image(file_name, nums, (200, 200), 1), 0.3, 0.95)
    colours.sort(key=lambda x: rgb2hsv(x)[2])
    if separate_bnw:
        background=tuple(int(round(i)) for i in average_points([colours[0], (0, 0, 0)]))
        background=colours[0]
        foreground=colours[-1]
    else:
        background=colours[0]
        foreground=colours[-1] 
    colour_dict={}
    colour_dict['foreground']=rgb2hex(foreground)
    colour_dict['background']=rgb2hex(background)
    for key in orig_term_colours:
        colour_dict[key]=rgb2hex(colours.pop(colours.index(find_closest(orig_term_colours[key], colours))))
    return colour_dict

def prepare_nice(file_name):
    nums=16
    colours=scale_colours(extract_colours_from_image(file_name, nums, (200, 200), 1), 0.3, 0.95)
    colours.sort(key=lambda x: rgb2hsv(x)[2])
    new_colours=[]
    for i in range(len(colours)):
        if i%2==0 and i<len(colours)-1:
            c1s=0
            c2s=0
            for j in range(len(colours[i])):
                c1s+=colours[i][j]**2
                c2s+=colours[i+1][j]**2
            if c1s<c2s:
                new_colours.append(colours[i])
                new_colours.append(colours[i+1])
            else:
                new_colours.append(colours[i+1])
                new_colours.append(colours[i])
    return new_colours

def prepare_pypalette(file_name):
    colours=prepare_for_terminal(file_name)
    colour_dict={}
    colour_dict['colour_fg']=colours['foreground']
    colour_dict['colour_bg']=colours['background']
    for i in range(16):
        colour_dict['colour_{0}'.format(i)]=colours['color{0}'.format(i)]
    return colour_dict

def prepare_pypalette_9(file_name):
    colours=scale_colours(extract_colours_from_image(file_name, 9, (200, 200), 1), 0.3, 0.95)
    colours.sort(key=lambda x: rgb2hsv(x)[2])
    colour_dict={}
    colour_dict['colour_bg']=rgb2hex(colours.pop(0))
    for i in range(len(colours)):
        colour_dict['colour_{0}'.format(i)]=rgb2hex(colours[i])
    return colour_dict
