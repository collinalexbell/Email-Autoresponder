import gmail
import sys
import time
import csv
import re
import json
import re
import datetime
import logging
import smtplib

#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


from gensim import corpora, models, similarities

user = 'EMAILADDR' #CHANGE
password = "PASSWORD" #CHANGE

g = gmail.login(user, password)

def unix_time(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()

def get_annoying_emails():

    parsed_mail = {}

    annoying_mails = g.label('annoying').mail()

    for annoying_mail in annoying_mails:
            annoying_mail.fetch()
            #print(annoying_mail.fr)
            #print(annoying_mail.thread_id)
            if annoying_mail.thread_id not in parsed_mail.keys():
                parsed_mail[annoying_mail.thread_id]= {}
            time_key = unix_time(annoying_mail.sent_at)
            parsed_mail[annoying_mail.thread_id][time_key] = {'author':annoying_mail.fr, 'body':annoying_mail.body}
                


    #print (parsed_mail)
    return parsed_mail

def get_stop_words():
    with open('stop-word-list.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            for i in range(len(row)):
                row[i] = row[i].replace(" ", "")
            return set(row)

class Multi_Annoyance_Responder:     #this sounds too java-esque for my liking.
    def __init__(self, document_map, num_of_annoyance_types):

        self.num_of_annoyance_types = num_of_annoyance_types
        self.comparators = {}
        self.threadid_to_doc = {} 
        documents = []
        for thread_id in sorted(document_map):
            for time_sent in sorted(document_map[thread_id]):
                if(document_map[thread_id][time_sent]['author'].find(user) == -1):
                        documents.append(document_map[thread_id][time_sent]['body'])
                        self.threadid_to_doc[thread_id] = len(documents)-1
                        #print (thread_id)
                        break #we only want to original email of the thread. this removes "OH Thanks!" responses from corpus


        stoplist = get_stop_words().union(set(['=', '_', '\r', '\n', '-', 'e-mail', 'email', 'use', 'hi', 'hello', 'thank', 'please', 'thankyou', 'want', 'make']))
        self.stoplist = stoplist 



        texts = [[word for word in document.lower().split() if (word not in stoplist)]
                for document in documents]

        #need to remove the inline previous response
        for i in range(len(texts)):
            del_j = []
            for j in range(len(texts[i])):
                if (texts[i][j].find("<") != -1 or texts[i][j].find("_") != -1):
                    #print("found <")
                    texts[i] = texts[i][:j]
                    break
                if (re.match('^[\w-]+$', texts[i][j]) is None):
                    del_j.append(texts[i][j])
            for d in del_j:
                texts[i].remove(d)

        self.texts = texts



        all_tokens = sum(texts, [])
        tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
        self.texts = [[word for word in text if word not in tokens_once]
                for text in texts]



        self.dictionary = corpora.Dictionary(self.texts)
        #dictionary.save('/tmp/deerwester.dict') # store the dictionary, for future reference
        self.corpus = [self.dictionary.doc2bow(text) for text in self.texts]
        tfidf = models.TfidfModel(self.corpus) # step 1 -- initialize a model
        corpus_tfidf = tfidf[self.corpus]

        self.lsi = models.LsiModel(corpus_tfidf, id2word=self.dictionary, num_topics=num_of_annoyance_types) # initialize an LSI transformation
        corpus_lsi = self.lsi[corpus_tfidf]
        self.lsi.print_topics(2)

        doc_to_feature = []
        for i in range(num_of_annoyance_types):
            doc_to_feature.append([])
        i=0
        for doc in (corpus_lsi):
            max_feature = (-1, 0) #I need to save the largest abs to indicate which feature the doc belongs to
            for feature in doc:
                if abs(feature[1]) > max_feature[1]:
                    max_feature = feature
            doc_to_feature[max_feature[0]].append(i)
            i += 1
        #print(doc_to_feature)

        self.doc_to_feature = doc_to_feature
        #print ("doc_to_feature:" + str(self.doc_to_feature))
        #for i in range(len(self.doc_to_feature)):
        #    print("Feature " + str(i))
        #    for j in self.doc_to_feature[i]:
        #        print("      " + str(texts[j]))
        self.get_responses(document_map)
       # st = self.split_texts(texts, doc_to_feature)
       # for t in st:
        #    print(t)
         #   self.split_corpus(t)


    def is_email_relevant(self, email_text):
        rv = []
        doc = email_text
        vec_bow = self.dictionary.doc2bow(doc)
        vec_lsi = self.lsi[vec_bow] # convert the query to LSI space
        index = similarities.MatrixSimilarity(self.lsi[self.corpus])


        sims = index[vec_lsi] # perform a similarity query against the corpus

        rl = list(enumerate(sims))
        #Average against the documents
        tot = []
        for i in self.doc_to_feature:
            tot.append(0)
        for i in range(len(rl)):
            for x in range(len(self.doc_to_feature)):
                if (rl[i][0]) in self.doc_to_feature[x]:
                    tot_index = x 
                    break

            tot[tot_index] += rl[i][1]
        for i in range(len(tot)):
            if(tot[i]/(len(self.doc_to_feature[i])) > .8):
                rv.append(True)
            else:
                rv.append(False)
        return rv

    def get_responses(self, document_map):
        self.responses = []
        num_responses = len(self.doc_to_feature)
        response_id = -1
        for i in range(num_responses):
            self.responses.append(-1)

        for thread_id in sorted(document_map):
            for time_sent in sorted(document_map[thread_id]):
                for i in range(len(self.doc_to_feature)):
                    if self.threadid_to_doc[thread_id] in self.doc_to_feature[i]:
                        response_id = i
                if(document_map[thread_id][time_sent]['author'].find(user) > -1 and response_id > -1 and self.responses[response_id] == -1):
                #If the email is sent by me and it is the first email response I sent for this annoying_question
                    self.responses[response_id] = document_map[thread_id][time_sent]['body']

    def send_response(self, response, author):
        fromaddr = user
        toaddr  = author # CHANGE
        username = user 
        passw = password 
        msg = "\r\n".join([
            "From: "+fromaddr,
            "To: "+toaddr,
            "Subject: AutoRespons from Dagney Rouge Taggart, Alex's AI",
            "",
            response 
            ])
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login(username, passw)
        server.sendmail(fromaddr,toaddr, msg)
        server.quit()

    def read_my_annoying_emails_and_do_something_about_them_PLEASE(self):

        unread_mails = g.inbox().mail(unread=True, after=datetime.date.today() ,prefetch=True)

        for unread_mail in unread_mails:
            author = unread_mail.fr
            text = [word for word in unread_mail.body.lower().split() if (word not in self.stoplist)]

            #need to remove the inline previous response
            del_j = []
            for j in range(len(text)):
                if (text[j].find("<") != -1 or text[j].find("_") != -1):
                    #print("found < or |")
                    text = text[:j]
                    break
                if (re.match('^[\w-]+$', text[j]) is None):
                    del_j.append(text[j])
            for d in del_j:
                text.remove(d)

            result = self.is_email_relevant(text)
            for i in range(len(result)):
                if result[i] == True:
                    self.send_response(self.responses[i], author)
                    print(author)

                    #print(self.responses[i])
            unread_mail.read()






if(len(sys.argv) != 2):
    print("You must enter how many features you are listening to")
    print("ex. python dagny_get_rid_of_these_annoying_questions_please_and_thanks.py 1")
    sys.exit(0)

dagney_rouge_taggart = Multi_Annoyance_Responder(get_annoying_emails(), int(sys.argv[1]))
dagney_rouge_taggart.read_my_annoying_emails_and_do_something_about_them_PLEASE()
