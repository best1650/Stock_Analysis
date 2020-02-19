from nltk.corpus import twitter_samples
from nltk.tag import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
import nltk
import re, string
from nltk import FreqDist

lemmatizer = WordNetLemmatizer()
stop_words = stopwords.words('english')

'''
Lemmatization is the process of grouping together
the different inflected forms of a
word so they can be analysed as a single item

'''
def remove_noise(tokens):
    global lemmatizer, stop_words
    
    # empty sentence
    processed_words = []

    # for each tuple, extract word and tag
    for word, tag in pos_tag(tokens):
        word = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
               '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', word)
        word = re.sub("(@[A-Za-z0-9_]+)","", word)
        
        # by default they are all adjectives
        pos = 'a'
        
        # if tag is a Noun, common, singular or mass
        if tag.startswith('NN'):
            pos = 'n'
        # verb
        elif tag.startswith('VB'):
            pos = 'v'

        # add lemmatized word to sentence
        word  = lemmatizer.lemmatize(word, pos)

        if len(word) > 0 and \
           word not in string.punctuation and \
           word.lower() not in stop_words: 
            processed_words.append(word)

    return processed_words

def get_all_words(cleaned_tokens_list):
    for tokens in cleaned_tokens_list:
        for token in tokens:
            yield token

def test():
    # tokenize positive_tweets
    positive_tweet_tokens = twitter_samples.tokenized('positive_tweets.json')
    negative_tweet_tokens = twitter_samples.tokenized('negative_tweets.json')

    positive_cleaned_tokens_list = []
    negative_cleaned_tokens_list = []

    for tokens in positive_tweet_tokens:
        positive_cleaned_tokens_list.append(remove_noise(tokens))

    for tokens in negative_tweet_tokens:
        negative_cleaned_tokens_list.append(remove_noise(tokens))
    
    all_pos_words = get_all_words(positive_cleaned_tokens_list)
    freq_dist_pos = FreqDist(all_pos_words)
    print(freq_dist_pos.most_common(10))

    # print the first sample tweet
    #print(positive_cleaned_tokens_list[0])
    #print(negative_cleaned_tokens_list[0])

if __name__ == "__main__":
    #nltk.download('twitter_samples')
    #nltk.download('punkt')
    #nltk.download('wordnet')
    #nltk.download('averaged_perceptron_tagger')
    #nltk.download('stopwords')

    test()

    print("Completed!!!")



    
