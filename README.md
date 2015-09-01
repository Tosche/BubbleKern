# BubbleKern

BubbleKern is a set of new kerning tools for the [Glyphs font editor](http://glyphsapp.com/) by Georg Seifert. that is based on the shape of surrounding outlines you draw, which is called a bubble. Once you draw bubbles for all letters, BubbleKern automatically kerns the typeface in seconds. That’s right, you kern by drawing it!
A bubble needs to be made as a extra layer in each master, and it has to be named “bubble“. It doesn’t have to be straight segments or single path, and you craw however you want. Components automatically inherit the bubbles of base glyphs, so you don’t have to draw one for an accented glyph (for letters like Eth or Tbar, you just draw a bubble for the bar).
When asked to kern, first of all BubbleKern scans through each letter to make an approximation of bubble shape so that it’s faster to calculate. And the temporary dictionary of bubble sidebearings is built for every letter.
Then for a given pair, BubbleKern looks at every scan height, finds where bubbles touch each other first, and kerns by the distance. In the example below, it finds the closest distance of 30 units, and kerns by -30.
As for pairs to kern, a type designer needs to make a checklist for BubbleKern to work with. Don’t worry, there is a script to help you with that.
But why does it not simply look at all possible pairs, every glyph against every other glyph? Because that takes so much time to check, only to create a huge mess. If your font has 600 glyphs, the maximum number of possible pairs is 600²=360,000 which contains meaningless pairs like %& or some other junk that you won’t enjoy cleaning up.
A good tool is something the user can control. BubbleKern will kern a font for you, but only do the obvious, not do some mysterious calculation in the background (e.g. Adobe’s optical kerning). That’s why I leave bubble shapes and pairs to designers.

This is a plugin for the [Glyphs font editor](http://glyphsapp.com/) by Georg Seifert.
It fills closed paths with almost black even while you are still drawing (yes, not perfectly black).
After installation, it will add the menu item *View > Show Black Fill*.
You can set a keyboard shortcut in System Preferences. I personally set it to Option+Command+B (I could make it as default, but don’t want to force it).
There is a similar plugin called [Show Filled Preview](https://github.com/mekkablue/ShowFilledPreview), and my version focuses more on neat fill without outlines, admittedly causing other info (guidelines and anchors) to be much less visible.
Huge thanks to [mekkablue](https://github.com/mekkablue) for debugging.

![Paths are filled in almost black while editing.](ShowBlackFill.png "Show Black Fill Screenshot")

### Contents
* **ShowKernBubbles.glyphsReporter** A viewer plugin that shows bubbles in colour.
* **Make Bubble Layers.py** A Python script to help you start drawing bubble layers.
* **Delete Bubble Layers.py** A Python script that deletes bubble layers from selected glyphs.
* **BubbleKern.py** The Python script that does the magic.
* **BubbleKern Manual.pdf** Instruction on how to use BubbleKern with more detail than this README.

### Installation
1. Download the complete ZIP file and unpack it, or clone the repository.
2. Double click the .glyphsReporter file. Confirm the dialog that appears in Glyphs.
3. Put the .py files under Scripts folder. The easiest way to access the folder is to open Scripts menu in Glyphs and choose "Open Scripts Folder".
3. Restart Glyphs

### Usage Instructions
The essential part is that you have a layer called "bubble" and run *BubbleKern* script. Every other tool is basically optional.
1. Make a extra layer and name it "bubble" for every layer you want to kern. Use *Make Bubble Layers* script to speed up the process.
2. Bubble layer dictates the kerning, and generally a bubble needs to be larger. Use *Show Kern Bubbles* viewer plugin to help shaping it. It is important to make the bubble stick to sidebearings somewhere, in order to create zero kerning. (e.g. think about how to avoid creating a kerning value between H and H while using bubbles)
3. Once you have bubble layer, run *BubbleKern*, in which you build a list of kerning pairs you want to check. There are two ways to build a list; permutation and plain text.
4. In BubbleKern, click *Kern All Pairs* for initial run. When you update a bubble shape of a glyph, run *Kern Pairs with Selected Glyphs* to update that specific part of kerning data, which is faster.


### License
Copyright 2015 Toshi Omagari (@tosche_e).
Based on sample codes by Rainer Erich Scheichelbauer (@mekkablue).

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

See the License file included in this repository for further details.
