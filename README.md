Alrihgt I accidentally deleted this when i was fixing something so here it is again:Add commentMore actions

This is my booze compass, which points to the nearest LCBO/store that sells alcohol in ontario. 
It is meant to work with a raspberry pi and a few modules, namely; A SSD1306 screen, a NEO6M GPS, and a HMC5883L compass. 
There are three main python codes:
Boozevisual and lcbovisual both use pygame, so you can run it using a regular screen.
lcbovis_nopygame(awesome name i know) DOESN'T use pygame crazily enough, and just renders the compass using a library for the screen instead. 
This is my booze compass, which points to the nearest LCBO/store that sells alcohol in ontario. It is meant to work with a raspberry pi and a few modules, namely; A SSD1306 screen, a NEO6M GPS, and a HMC5883L compass. There are three main python codes: Boozevisual and lcbovisual both use pygame, so you can run it using a regular screen. lcbovis_nopygame(awesome name i know) DOESN'T use pygame crazily enough, and just renders the compass using a library for the screen instead.

I still don't have the modules yet(thanks to aliexpress), that's why a bunch of code is commented out. 
The way I determine the closest store to your coordinates is using an algorithm based off of kd-trees nearest neighbors. 
You can read more about it here: https://en.wikipedia.org/wiki/K-d_tree (scroll down to the nearest neighbors part). 
I save the structure of the tree in a .joblib file, and the python code that makes the .joblib files is tree.py. 
You give the code a list of stores and it creates the tree and saves it for you.

I'm planning on adding more features, specifically adding support for different stores to point to(mcdonalds, shawarma etc.) 
and some way to choose which store to point to, but the form of the code would stay the same. I still don't have the modules yet(thanks to aliexpress), 
that's why a bunch of code is commented out.

I will continue to make this as good as I can in the future, and that's about it. Thanks for reading!
