# bilderchord
I made a little app that turns pictures into chords. It is implemented with a GUI via wxPython. You can run that GUI either by running the Bildakkord.py-script itself or by creating a stand-alone app with setup.py. 

The Bildakkord.py-script also includes an implementation of the k-means algorithm, because I was running into problems using the kmeans of sklearn together with wxPython.


This is the interface without any picture loaded into it:

![Bildakkord1](https://user-images.githubusercontent.com/106880521/172020431-4644758a-2df4-4dd3-924d-79307b88db03.PNG)


And this is how it looks like after it assigned a chord to a picture:

![Bildakkord2](https://user-images.githubusercontent.com/106880521/172020512-660d08a5-8d43-41ee-827e-bd447a203d02.PNG)

The staked bar underneath the picture represents the colors of the centroids determined by kmeans. The length of the color represents the cluster-size. 

Clustersize is also represented in the playable chord by note-length. The cluster's colors get translated to hsv-color-codes (hue, satuaration and value) which are then interpreted by the chord as:
Hue - played note within an octave
Saturation - loudness of a note
Value - determines the octave the note gets played in

I limited the notes within an octave to the notes within the key of C-major. In line 216 of the Bildakkord.py-script, you can choose which notes you want to select from the scale. Every selectable note would be accessed by storing "range(12)" in the variable "keyselected".
