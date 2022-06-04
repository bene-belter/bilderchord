# bilderchord
I made a little app that turns pictures into chords. It is implemented with a GUI via wxPython. You can run that GUI either by running the Bildakkord.py-script itself or by creating a stand-alone app with setup.py. 

The Bildakkord.py-script also includes an implementation of the k-means algorithm, because I was running into problems using the kmeans of sklearn together with wxPython.


This is the interface without any picture loaded into it:

![Bildakkord1](https://user-images.githubusercontent.com/106880521/172020431-4644758a-2df4-4dd3-924d-79307b88db03.PNG)


And this is how it looks like after a picture was loaded and the app has assigned a chord to the picture:

![Bildakkord2](https://user-images.githubusercontent.com/106880521/172021860-ebce12d6-2a7a-413f-812a-6fb0d6db2865.PNG)


The stacked bar underneath the picture represents the colors of the centroids determined by kmeans. The length of the color in the bar represents the cluster-size. 
Clustersize is also represented in the playable chord by note-length. The chord also represents the centroid's hsv-color-values as follows:

Hue - played note within an octave
Saturation - loudness of a note
Value - determines the octave the note gets played in


I limited the notes within an octave to the notes within the key of C-major. In line 216 of the Bildakkord.py-script, you can choose which notes you want to select from the scale. Every selectable note would be accessed by storing "range(12)" in the variable "keyselected".
