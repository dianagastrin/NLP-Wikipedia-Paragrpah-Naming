
# coding: utf-8

# ## Evaulating Segmentation and Title Assignment ##
# 

# In[24]:

from nltk.metrics.segmentation import *


# The nltk metrics module includes three measures for text segmentation. They are all based on binary alphabeth strings. So, if the tiling output cannot provide it such straight away, we have to convert, say, a list of inidces to a binary string 1000...10001... where the 1's match the segment boundaries.

# In[18]:

def indexlist2binary(index_list,text_length):
    ret = ""
    for ordinal,split_location in enumerate(index_list):
        ret += "0"*(split_location - (index_list[ordinal - 1] if ordinal > 0 else 0))
        ret += "1"
    ret += "0"*(text_length - index_list[-1])
    return ret

indexlist2binary([15,28,30],35)


# In[26]:

print(ghd(indexlist2binary([15,28,30],35),indexlist2binary([11,29,31],35)))
print(windowdiff(indexlist2binary([15,28,30],35),indexlist2binary([11,29,31],35),4))
print(pk(indexlist2binary([15,28,30],35),indexlist2binary([11,29,31],35)))


# So we can take as eval(our output) the average f measure for title and multiply by one of 
