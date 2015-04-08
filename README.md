I made an AI auto responder to respond to repetitive questions that appear in my mailbox. Since I don't use email very often, I had to ask some of my friends what they would have an AI do if it could read their emails. One of my friends said that since they work in a large corporation, they get a lot of emails asking relatively the same thing. I figured this could be easy to automate responses for. I use Latent Semantic Analysis in the Gensim library to judge the equivalency of questions with the same meaning but different wording. 

In order to use the software you must:

	-Download & unzip the attached folder

	-CD into the gmail library subfolder in the project and run python setup.py install

	-Then install gensim with easy_install -u gensim (I assume you have easy_install)

	-You then need to go into your inbox and find (or contrive) a couple of emails that have a repetitive response.

	-You MUST REPLY to one of these emails before labeling them

	-Label them all as "annoying" (nocaps)

	-Open the .py file and go to line 186 and change "author" to "user" if you want to send the responses to your own inbox and not spam the original authors inbox. Also change the username and password at the top of the file

	-Send an annoying question that is similar to the ones in your annoying folder. (You can send this to yourself if you want)

	-Wait for it to hit your inbox 

	- python dagny_get_rid_of_these_annoying_questions_please_and_thanks.py 1 (IMPORTANT, you must put as an arg the number of types of annoying emails you have sitting in your annoying folder. This is not how many EMAILS are in the annoying folder but rather how many unique responses the AI must know how to respond with. If your following this guide then it should be 1)


Dagny will give you a response if she knows how.

I had my friend send me a collection of questions that were sent to her:

-Email 1:

"Hi,

How are you?  Just want to make sure that we are aligned with the exchange rates to be used in the DFE reports,  they are the ones from the Corporate Controllers website correct?

Please advise.

Sam"

-Email 2:

"Greetings,

As you mentioned in your prior email, where can I find the FX currency rates for the last day of the quarter?  Is it in a link I can access?

Please advise.

Tory"

-Email 3:

"Hello,

On the Ruetters exchange rate - where can i obtain what these are for the period you mentioned?  I have looked several places and cannot match to what you say they should be.

Thank you,

Sue Jones"


-Email 4:

"Hi,

As you indicated in a recent communication, where can i find the Corporate Controller site?  This is where I can see the currency FX rates to use for DFE reporting.

Thank you,

Paul Jones"



All I needed to do was respond to just 1 of these emails and then label them all as "annoying" so that  Dagny (yes, I named my AI) can know she needs to learn on them.

The next time an email comes in that resemble the learned email's, she will respond with the 1 generic response I had sent previously.

My software can try to learn on pretty much anything and can respond to more than 1 set of annoying emails.


