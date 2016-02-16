# NLP Project # 
###Objective:### 
Given a Wikipedia biography entry as one chunk of text, divide the text
to pargraphs and name the paragraphs as closely as possible to the way it is in the
original entry.

###Algorithm:###
* Prepare the texts, gather some statistics regarding average number of paragraphs, typicall topics etc.
* Run "tiling" on the text to split into segments.
* Learn titles/topics using the original Wikipedia entry and possibly some by product of the tiling (specifically, the topic word lists produced by LDA).
* Match title to automatically produced pargagraphs using the learned classifier.
* Evaluate the results.
* Hope for the best.

