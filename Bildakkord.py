import pyo, math
import wx, time, random
import cv2 
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from PIL import Image
from collections import Counter


NCHNLS = 2
server = pyo.Server().boot()

### A basic audio process ###
f = []
d = []
for i in range(5):
    f.append(pyo.Fader(fadein=2, fadeout=2, dur=1, mul=0))
    d.append(pyo.RCOsc(freq = 1000, sharp=0.3, mul=f[i]).out())

def repeat():
    for i in range(5):
        f[i].play()

pat = pyo.Pattern(function=repeat, time=2).play()
am = pyo.Iter(pat, [1, 0, 0, 0] * 4)


class MyFrame(wx.Frame):
    def __init__(self, parent, title, pos=(50, 50), size=(500, 700)):
        wx.Frame.__init__(self, parent, -1, title, pos, size)

        self.Bind(wx.EVT_CLOSE, self.on_quit)

        self.panel = wx.Panel(self)

        #Audiointerface

        self.playBtn = wx.Button(self.panel, label='Play')
        self.playBtn.Bind(wx.EVT_BUTTON, self.onPlay)
        volslider = self.createOutputBox()

        #Photoviewer

        self.PhotoMaxWidth = 480
        self.PhotoMaxHight = 360

        instructions = "\n Select an image to listen to:"
        instructLbl = wx.StaticText(self.panel, label=instructions)

        img = wx.EmptyImage(480,360)
        self.imageCtrl = wx.StaticBitmap(self.panel, wx.ID_ANY, 
                                         wx.BitmapFromImage(img))

        self.photoTxt = wx.TextCtrl(self.panel, size=(390,-1))
        browseBtn = wx.Button(self.panel, label="Browse")
        browseBtn.Bind(wx.EVT_BUTTON, self.onBrowse)
        
        colorplot = wx.EmptyImage(480,48)
        self.plotCtrl = wx.StaticBitmap(self.panel, wx.ID_ANY,
                                        wx.BitmapFromImage(colorplot))
        
        colorNames = "hex-codes of detected colors: \n"
        self.colorsLbl = wx.StaticText(self.panel, label=colorNames)

        assignedKeys = "assigned keys for detected colors: \n"
        self.keysLbl = wx.StaticText(self.panel, label=assignedKeys)

        #Layout

        self.mainsizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)

        self.mainsizer.Add(instructLbl, 0, wx.ALL, 5)
        self.sizer1.Add(self.photoTxt, 0, wx.ALL, 5)
        self.sizer1.Add(browseBtn, 0, wx.ALL, 5)     
        self.mainsizer.Add(self.sizer1, 0, wx.ALL, 5)
        
        self.mainsizer.Add(self.imageCtrl, 0, wx.ALL, 5)
        self.mainsizer.Add(self.plotCtrl, 0, wx.ALL, 5)  
        self.mainsizer.Add(self.colorsLbl, 0, wx.ALL, 5)
        self.mainsizer.Add(self.keysLbl, 0, wx.ALL, 5)
        
        self.sizer2.Add(self.playBtn, 0, wx.CENTER, 5)
        self.sizer2.Add(volslider, 0, wx.ALL, 5)
        self.mainsizer.Add(self.sizer2, 0, wx.ALL, 5)

        self.panel.SetSizerAndFit(self.mainsizer)

    def onBrowse(self, event):
        """ 
        Browse for file
        """
        wildcard = "Image files (*.jpg;*.jpeg;*.png;*.bmp;*.gif;*.tiff;*.webp)" "|*.jpg;*.jpeg;*.png;*.bmp;*.gif;*.tiff;*.webp"
        dialog = wx.FileDialog(None, "Choose a file",
                               wildcard=wildcard,
                               style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            self.photoTxt.SetValue(dialog.GetPath())
        dialog.Destroy() 
        self.onView()

    def onView(self):
        filepath = self.photoTxt.GetValue()
        img = wx.Image(filepath, wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        W = img.GetWidth()
        H = img.GetHeight()

        if W > H:
            self.NewW = self.PhotoMaxWidth
            self.NewH = int(self.PhotoMaxWidth * (H / W)) 
        else:
            self.NewH = self.PhotoMaxHight
            self.NewW = int(self.PhotoMaxHight * (W / H))
        
        img = img.Scale(self.NewW,self.NewH)
        self.imageCtrl.SetBitmap(wx.BitmapFromImage(img))
        self.panel.Refresh()
        
        self.coreAlgorithm()

    def coreAlgorithm(self):
        filepath = self.photoTxt.GetValue()

        for i in range(5):
            f[i] = pyo.Fader(fadein=2, fadeout=2, dur=1, mul=0)
            d[i] = pyo.RCOsc(freq = 1000, sharp=0.3, mul=f[i]).out()

        def rgb_to_hex(rgb_color):
            hex_color = "#"
            for i in rgb_color:
                i = int(i)
                hex_color += ("{:02x}".format(i))
            return hex_color

        raw_img = cv2.imread(filepath)
        raw_img = cv2.cvtColor(raw_img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(raw_img, (self.NewW,self.NewH), interpolation = cv2.INTER_AREA)
        img = img.reshape(img.shape[0]*img.shape[1], 3)

        labels = {}
        centers = {}
        sse = {}

        for i in range(5):
            kmeans = KMeans(i+1)
            kmeans.fit(img)
            labels[i] = kmeans.classes
            centers[i] = kmeans.centroids
            sse[i] = kmeans.sse

            if i == 0 and sse[i] == 0:
                numClust = i+1
                break
            else:
                if i > 1 and (sse[i]/sse[i-1])/(sse[i-1]/sse[i-2]) > 2:
                    numClust = i
                    break
                else:
                    numClust = i+1
                    

        color_labels = labels[numClust-1]
        center_colors = centers[numClust-1]

        counts = Counter(color_labels)
        ordered_keys = sorted(counts, key=counts.get, reverse=True)
        ordered_values = sorted(counts.values(), reverse=True)
        hex_colors = [rgb_to_hex(center_colors[i]) for i in ordered_keys]
        onestringcolors = ", ".join(hex_colors)

        syntaxForHexCodes = "hex-codes of detected colors: \n"+ onestringcolors

        self.colorsLbl.Label = syntaxForHexCodes


        #create Barplot and turn it into an displayable image

        px = 1/plt.rcParams['figure.dpi'] 
        fig, ax = plt.subplots(figsize = (480*px,48*px))

        canvas = FigureCanvasAgg(fig)
        cumsum_values = np.cumsum(ordered_values)
        cumsum_values = np.insert(cumsum_values, 0, 0)

        for i in range(len(ordered_values)):
            ax.barh(0, ordered_values[i], 0.35, color = hex_colors[i], left = cumsum_values[i])
    
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.xlim([0,cumsum_values[len(cumsum_values)-1]])

        canvas.draw()
        rgba = np.asarray(canvas.buffer_rgba())
        pil_image = Image.fromarray(rgba)

        wx_image = wx.Image(pil_image.size[0], pil_image.size[1])
        wx_image.SetData(pil_image.convert("RGB").tobytes())
        bitmap = wx.Bitmap(wx_image)

        self.plotCtrl.SetBitmap(bitmap)


        #make chord

        centerpic = np.uint8(center_colors.reshape(1,numClust,3))

        centerpic_HSV_FULL = cv2.cvtColor(centerpic, cv2.COLOR_RGB2HSV_FULL)

        x = 0
        biggest_count = ordered_values[0]
        keynames = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        octavenames = [1,2,3,4,5,6,7]
        keyselected = [0,2,4,5,7,9,11]
        notenames = []

        for i in ordered_keys:
            newnoise = centerpic_HSV_FULL[0,i]
            whichkey = math.floor(newnoise[0] * (len(keyselected)/256))
            whichoctave = math.floor(newnoise[2] * ((len(keyselected)-1)/256))

            notenames.append(keynames[keyselected[whichkey]]+str(octavenames[whichoctave]))

            actualnote = pyo.midiToHz(24+keyselected[whichkey]+12*whichoctave)

            intensity = float((newnoise[1]/255)*0.9+0.1)

            quantity = float(ordered_values[x]/biggest_count)

            f[x] = pyo.Fader(fadein=2*quantity, fadeout=2*quantity, dur=1, mul=intensity)
            d[x] = pyo.RCOsc(freq = actualnote, sharp=0.3, mul=f[x]).out()

            x += 1

        onestringkeys = ", ".join(notenames)

        syntaxForKeys = "assigned keys for detected colors: \n" + onestringkeys

        self.keysLbl.Label = syntaxForKeys

        self.panel.Refresh()

    def on_quit(self, evt):
        server.stop()
        time.sleep(0.25)
        self.Destroy()

    def onPlay(self, evt):
        if server.getIsStarted() == False:
            server.start()
            self.playBtn.Label = "Pause"
        else:
            server.stop()
            self.playBtn.Label = "Play"

    def createOutputBox(self):
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        self.amp = pyo.PyoGuiControlSlider(
            parent=self.panel,
            minvalue=-60,
            maxvalue=18,
            init=-12,
            pos=(0, 0),
            size=(395, 16),
            log=False,
            integer=False,
            powoftwo=False,
            orient=wx.HORIZONTAL,
        )
        self.amp.Bind(pyo.EVT_PYO_GUI_CONTROL_SLIDER, self.changeGain)
        self.meter = pyo.PyoGuiVuMeter(
            parent=self.panel, nchnls=NCHNLS, pos=(0, 0), size=(5 * NCHNLS, 200), orient=wx.HORIZONTAL, style=0,
        )
        self.meter.setNchnls(1)
        # Register the VuMeter in the Server object.
        server.setMeter(self.meter)
        # or register its `setRms` method in a PeakAmp object.
        # pa.setFunction(self.meter.setRms)

        sizer1.Add(self.amp, 0, wx.ALL | wx.EXPAND, 5)
        sizer1.Add(self.meter, 0, wx.ALL | wx.EXPAND, 5)
        return sizer1

    def changeGain(self, evt):
        server.amp = pow(10, evt.value * 0.05)


class KMeans:
    def __init__(self,k):
        self.k = k

    def fit(self,X,MAXITER = 100, TOL = 1e-3):
        centroids = np.random.rand(self.k,X.shape[1])*255
        centroidsold = centroids.copy()
        for iter_ in range(MAXITER):
            dist = np.linalg.norm(X - centroids[0,:],axis=1).reshape(-1,1)
            for class_ in range(1,self.k):
                dist = np.append(dist,np.linalg.norm(X - centroids[class_,:],axis=1).reshape(-1,1),axis=1)
            classes = np.argmin(dist,axis=1)
            # update position
            for class_ in range(self.k):
                if any(classes == class_):
                    centroids[class_,:] = np.mean(X[classes == class_,:],axis=0)
                else:
                    centroids[class_,:] = np.random.rand(1,X.shape[1])*255
            if np.linalg.norm(centroids - centroidsold) < TOL:
                break
                print('Centroid converged')
        self.centroids = centroids

        dist = np.linalg.norm(X - self.centroids[0,:],axis=1).reshape(-1,1)
        for class_ in range(1,self.k):
            dist = np.append(dist,np.linalg.norm(X - self.centroids[class_,:],axis=1).reshape(-1,1),axis=1)
        self.classes = np.argmin(dist,axis=1)
        self.sse = np.square(np.min(dist,axis=1)).sum()


app = wx.App(False)
mainFrame = MyFrame(None, title="Bildakkord")
mainFrame.Show()
app.MainLoop()
