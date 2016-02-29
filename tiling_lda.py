
# coding: utf-8

# In[1]:

import numpy as np
import lda
import lda.datasets
X = lda.datasets.load_reuters()
vocab = lda.datasets.load_reuters_vocab()
titles = lda.datasets.load_reuters_titles()
X.shape


# In[2]:

import os, numpy as np
from nltk import word_tokenize, sent_tokenize

all_tokens = set()
biography_tokens = list()
biography_sentences = list()
biography_sentences_tokens = list();

for file in os.listdir("."):
    if file.endswith(".txt"):
        with open(file, 'r') as f:
            raw_biography_text = f.read()
            tokens = word_tokenize(raw_biography_text)
            sentences = sent_tokenize(raw_biography_text)
            biography_tokens.append(tokens)
            all_tokens |= set(tokens)
            
            biography_sentences.append(sentences)
            biography_sentences_tokens.append(list(word_tokenize(sentence) for sentence in sentences))
            
all_tokens_list = list(all_tokens)
number_of_biographies = len(biography_tokens)
number_of_tokens = len(all_tokens_list)
biography_bow = np.zeros([number_of_biographies, number_of_tokens], dtype = np.int)

for i in range(number_of_biographies):
    for j in range(len(biography_tokens[i])):
        biography_bow[i][all_tokens_list.index(biography_tokens[i][j])] += 1


# In[3]:

vocab = all_tokens_list
biography_bow.shape


# In[4]:

number_of_topics = 30

model = lda.LDA(n_topics=number_of_topics, n_iter=1500, random_state=1)
model.fit(biography_bow)  # model.fit_transform(X) is also available


# In[5]:

topic_word = model.topic_word_  # model.components_ also works
n_top_words = 20

topics_words = list()

for i, topic_dist in enumerate(topic_word):
    # topic_words: words sorted by relevance to topic in descending order
    topic_words = list(np.array(vocab)[np.argsort(topic_dist)[::-1]])#[:10]#[:-(n_top_words+1):-1]
    #print(topic_words)
    topics_words.append(topic_words)
    print('Topic {}: {} ({})'.format(i, ' '.join(topic_words[:10])+'...',len(topic_words)))


# In[6]:

def calculate_word_topic_id(word, topics_words):
    topic_id = -1
    min_topic_index = number_of_tokens + 1
    for current_topic_id in range(number_of_topics):
        index = topics_words[current_topic_id].index(word)
        if index < min_topic_index:
            topic_id = current_topic_id
            min_topic_index = index
            
    return topic_id


# In[7]:

calculate_word_topic_id("Elvis", topics_words)


# In[14]:

def calculate_vocabulary_topic_ids(vocabulary, topics_words):
    topic_ids = list()
    for word in vocab:
        topic_ids.append(calculate_word_topic_id(word, topics_words))
        
    return topic_ids


# In[17]:

vocabulary_topic_ids = calculate_vocabulary_topic_ids(vocab, topics_words)


# In[18]:

def get_vocabulary_word_topic_id(vocabulary, vocabulary_topic_ids, word):
    return vocabulary_topic_ids[vocabulary.index(word)]


# In[19]:

get_vocabulary_word_topic_id(vocab, vocabulary_topic_ids, "Elvis")


# In[20]:

#biography_sentences_tokens

def get_sentence_topic_ids(sentence, topics_words):
    topic_ids = list()
    for word in sentence:
        topic_ids.append(get_vocabulary_word_topic_id(vocab, vocabulary_topic_ids, word))
        
    return topic_ids


# In[23]:

#get_sentence_topic_ids(biography_sentences_tokens[1][0], topics_words)


# In[24]:

def get_sentences_topic_ids(sentences, topic_words):
    topic_ids = list()
    for sentence in sentences:
        topic_ids.append(get_sentence_topic_ids(sentence, topics_words))
        
    return topic_ids


# In[25]:

sentences_topic_ids = get_sentences_topic_ids(biography_sentences_tokens[0], topic_words)


# In[26]:

def get_biography_sentences_topic_ids(biography_sentences_tokens, topic_words):
    biography_sentences_topic_ids = list()
    for sentences in biography_sentences_tokens:
        biography_sentences_topic_ids.append(get_sentences_topic_ids(sentences, topic_words))
    
    return biography_sentences_topic_ids


# In[27]:

biography_sentences_topic_ids = get_biography_sentences_topic_ids(biography_sentences_tokens, topic_words)


# In[28]:

def calculate_sentence_topics_frequency(sentence_topic_ids, number_of_topics):
    topics_frequencies = np.zeros(number_of_topics)
    for topic_id in sentence_topic_ids:
        topics_frequencies[topic_id] += 1
    
    return topics_frequencies


# In[31]:

def calculate_sentences_topics_frequency(sentences_topic_ids, number_of_topics):
    sentences_topics_frequencies = list()
    for sentence in sentences_topic_ids:
        sentences_topics_frequencies.append(calculate_sentence_topics_frequency(sentence, number_of_topics))
        
    return sentences_topics_frequencies


# In[32]:

def calculate_biography_sentences_topics_frequencies(biography_sentences_topic_ids, number_of_topics):
    biography_sentences_topics_frequencies = list()
    for sentences in biography_sentences_topic_ids:
        biography_sentences_topics_frequencies.append(calculate_sentences_topics_frequency(sentences, number_of_topics))
        
    return biography_sentences_topics_frequencies


# In[33]:

biography_sentences_topics_frequencies = calculate_biography_sentences_topics_frequencies(biography_sentences_topic_ids, number_of_topics)


# In[36]:

#biography_sentences_topics_frequencies


# In[37]:

def calculate_coherence_score(sentences_topics_frequencies, number_of_topics, position, window_size):
    pre_topics_frequencies = np.zeros(number_of_topics)
    for i in range(window_size):
        pre_topics_frequencies += sentences_topics_frequencies[position - i]
        
    post_topics_frequencies = np.zeros(number_of_topics)
    for i in range(window_size):
        post_topics_frequencies += sentences_topics_frequencies[position + 1 + i]
        
    dot_product = np.dot(pre_topics_frequencies, post_topics_frequencies)
    pre_norm = np.linalg.norm(pre_topics_frequencies)
    post_norm = np.linalg.norm(post_topics_frequencies)
    
    cosine_similarity = dot_product / (pre_norm * post_norm)
    
    return cosine_similarity


# In[38]:

calculate_coherence_score(biography_sentences_topics_frequencies[0], number_of_topics, 65, 3)


# In[39]:

def calculate_coherence_scores(sentences_topics_frequencies, number_of_topics, window_size):
    coherence_scores = list()
    for i in range(len(sentences_topics_frequencies) - 2 * window_size):
        score = calculate_coherence_score(sentences_topics_frequencies, number_of_topics, window_size + i - 1, window_size)
        coherence_scores.append(score)
        
    return coherence_scores


# In[40]:

def calculate_depth_scores(coherence_scores):
    depth_scores = list()
    for i in range(len(coherence_scores)):
        hl = coherence_scores[i]
        hr = coherence_scores[i]
        for j in range(i):
            if coherence_scores[j] > coherence_scores[i]:
                hl = coherence_scores[j]
            else:
                break
        
        for j in range(i + 1, len(coherence_scores)):
            if coherence_scores[j] > coherence_scores[i]:
                hr = coherence_scores[j]
            else:
                break
                
        depth_score = 0.5 * (hl + hr - 2 * coherence_scores[i])
        depth_scores.append(depth_score)
        
    return depth_scores


# In[42]:

coherence_scores = calculate_coherence_scores(biography_sentences_topics_frequencies[0], number_of_topics, 3)


# In[43]:

depth_scores = calculate_depth_scores(coherence_scores)


# In[44]:

mean = np.mean(depth_scores)


# In[45]:

std = np.std(depth_scores)


# In[46]:

mean - std /2


# In[47]:

#depth_scores


# In[48]:

len(depth_scores)


# In[49]:

len(biography_sentences_topics_frequencies[0])


# In[50]:

biography_sentences[0][:10]


# In[51]:

biography_sentences[1][:10]


# In[ ]:



