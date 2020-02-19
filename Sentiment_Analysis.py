from nltk.corpus import twitter_samples
from nltk.tag import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
import nltk
import re, string, random
from nltk import FreqDist, classify, NaiveBayesClassifier

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
    word_list = []
    for tokens in cleaned_tokens_list:
        for token in tokens:
            word_list.append(token)
    return word_list

def get_tweets_for_model(cleaned_tokens_list):
    for tweet in cleaned_tokens_list:
        yield dict([token, True] for token in tweet)

def startAnalysis():
    # tokenize positive_tweets
    positive_tweet_tokens = twitter_samples.tokenized('positive_tweets.json')
    negative_tweet_tokens = twitter_samples.tokenized('negative_tweets.json')

    positive_cleaned_tokens_list = []
    negative_cleaned_tokens_list = []

    for tokens in positive_tweet_tokens:
        positive_cleaned_tokens_list.append(remove_noise(tokens))

    for tokens in negative_tweet_tokens:
        negative_cleaned_tokens_list.append(remove_noise(tokens))
    
    pos_tweet_for_model = get_tweets_for_model(positive_cleaned_tokens_list)
    pos_dataset = [(tweet_dict,"Positive") for tweet_dict in pos_tweet_for_model]
    neg_tweet_for_model = get_tweets_for_model(negative_cleaned_tokens_list)
    neg_dataset = [(tweet_dict,"Negative") for tweet_dict in neg_tweet_for_model]
  
    dataset = pos_dataset + neg_dataset
    random.shuffle(dataset)

    train_data = dataset[:7000]
    test_data= dataset[7000:]

    classifier = NaiveBayesClassifier.train(train_data)
    print("Accuracy is:", classify.accuracy(classifier, test_data))
    print(classifier.show_most_informative_features(10))

    #all_pos_words = get_all_words(positive_cleaned_tokens_list)
    #freq_dist_pos = FreqDist(all_pos_words)
    #print(freq_dist_pos.most_common(10))

if __name__ == "__main__":
    startAnalysis()
    print("Completed!!!")



    
