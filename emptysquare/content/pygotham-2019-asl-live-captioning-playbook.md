+++
category = ["Python"]
date = "2019-11-09T21:37:13.986739"
description = "Here's what we did for Deaf and hard-of-hearing accessibility, in detail. I hope this recap can be a playbook for future conferences."
draft = false
enable_lightbox = false
tag = ["pygotham"]
thumbnail = "pygotham-2019-logo.jpg"
title = "PyGotham 2019's ASL And Live Captioning Playbook"
type = "post"
+++

![](pygotham-2019-logo.jpg)


At PyGotham 2019 we provided live captioning and, for the first time, we offered American Sign Language interpretation and did targeted outreach to groups of Deaf programmers. As a result, we had a half-dozen Deaf attendees, and they reported they were able to fully participate in the conference in a way they hadn't experienced before. I (A. Jesse Jiryu Davis) led our effort to provide ASL and captioning; I hope this recap can serve as a playbook for other conferences.

<!--more-->

<blockquote style="text-align:center" class="twitter-tweet" data-conversation="none"><p lang="en" dir="ltr">It was downright incredible having both ASL and CART in every track + interpreters willing to follow me to hallway conversations. Being able to approach a speaker after their talk, then get so engrossed in the ensuing conversation that we slide in slightly late to the closing +</p>&mdash; Mel Chua (@mchua) <a href="https://twitter.com/mchua/status/1181012741580099587?ref_src=twsrc%5Etfw">October 7, 2019</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>

<blockquote class="twitter-tweet" data-conversation="none"><p lang="en" dir="ltr">+ keynote, seamlessly and without needing to read lips or use my voice, was something I had NEVER done before. I've never experienced a tech conf this way — and I used to organize them.<br><br>(to be fair, the "late" was b/c convo with other Deaf attendees - ALSO rare and newer-to-me).</p>&mdash; Mel Chua (@mchua) <a href="https://twitter.com/mchua/status/1181013796745367553?ref_src=twsrc%5Etfw">October 7, 2019</a></blockquote>

<blockquote class="twitter-tweet" data-conversation="none"><p lang="en" dir="ltr">Seriously. I flew in to a regional Python conference *outside* my own region *solely* because they had this sort of access. <a href="https://twitter.com/brainwane?ref_src=twsrc%5Etfw">@brainwane</a> told me about it 11 days before the conf, I found out who was providing services, and immediately got a ticket and booked flights. WOULD DO AGAIN</p>&mdash; Mel Chua (@mchua) <a href="https://twitter.com/mchua/status/1181015598727405569?ref_src=twsrc%5Etfw">October 7, 2019</a></blockquote>

# Motivation

Early in the PyGotham 2019 planning process, we decided to provide captioning for all talks, typed in real time by a human. (This is also known as "communication access real-time translation" or CART.) PyCon has provided captioning in recent years and we wanted PyGotham to be at least as accessible.

Captioning benefits Deaf attendees, of course, but we could think of many other groups it would help. People who are hard of hearing have a less obvious disability than those who are Deaf, but they benefit from captioning, too. We want our conference to be welcoming to older programmers, and many of them are likely to be hard of hearing. Captioning helps people who speak English as a second language and people with ADHD. In fact, *everyone* who attends PyGotham will misunderstand some words, or space out for a minute; captioning helps all of us.

As a final bonus, we can take the captions that our stenographers typed during the talks and use them as YouTube captions when we publish the talks later, instead of relying on YouTube's absurd auto-captioning.

But captioning alone doesn't provide full access to Deaf attendees who use ASL. We decided to also hire ASL interpreters for all three conference tracks. Interpreters provide maximum access for people whose primary language is ASL, they enable Deaf people to ask questions of the speaker, and they permit communication among Deaf and hearing attendees in the hallways and at meals.

# Hiring Professionals

We chose White Coat Captioning as our live captioning service. They seemed like the right provider&mdash;they captioned PyCon in 2018 and 2019, and the PyCon organizers praised them. One of White Coat's staff is Mirabai Knight; she founded [an open-source stenography project written in Python](http://www.openstenoproject.org), and she had captioned PyGotham before and [participated in a PyGotham talk about stenography](https://pyvideo.org/pygotham-2016/hackingtypingwriting-at-200-words-per-minute.html), so we felt a special connection. We arranged for Mirabai to be on site in our largest room, where keynotes and lightning talks happen along with one of the three regular tracks. The two smaller rooms would be captioned by remote staff listening via Google Hangouts.

<blockquote class="twitter-tweet"><p lang="en" dir="ltr">❤️ this. <a href="https://twitter.com/hashtag/PyGotham?src=hash&amp;ref_src=twsrc%5Etfw">#PyGotham</a> <a href="https://twitter.com/hashtag/pygotham2019?src=hash&amp;ref_src=twsrc%5Etfw">#pygotham2019</a> <a href="https://t.co/hlmrRlp7UE">pic.twitter.com/hlmrRlp7UE</a></p>&mdash; Sartaj Singh (@leosartaj03) <a href="https://twitter.com/leosartaj03/status/1180215496613998594?ref_src=twsrc%5Etfw">October 4, 2019</a></blockquote>

We evaluated two sign language interpretation agencies. A couple of my friends are ASL interpreters and they advised me to seek agencies that provide interpreters certified by the Registry of Interpreters for the Deaf, who have experience interpreting at tech conferences or software companies. Agencies that specialize in sign language interpretation are likely to be better quality than agencies that also do spoken languages. We chose Lydia Callis Interpreting Services. LCIS assigned us local interpreters with tech experience. The contract was reasonably priced and very flexible: with a few days notice we could ask for more interpreters, or fewer, or cancel altogether. This reassured us we could arrange ASL services but cancel if no Deaf people registered.

# Deaf Outreach

Once we had captioning and ASL settled, we wanted Deaf programmers to know PyGotham would be accessible to them. We published [a blog post](https://2019.pygotham.org/2019/09/03/captioning-and-interpreting/), and with Sumana Harihareswara's help we added [a general accessibility statement](https://2019.pygotham.org/about/accessibility/). We updated our registration form to say we would provide ASL and captioning, and we added a checkbox asking participants if they would use ASL interpretation. Some people had registered already; we emailed them to ask if they would use ASL. (If we want to estimate demand more accurately next year we may ask attendees if they *require* ASL interpreters. More likely we'll decide to have interpreters in all the conference tracks regardless of demand.)

I asked my ASL interpreter friends for help marketing to Deaf programmers. Besides just Googling for groups in New York City, they told me to search in Washington, DC and Rochester, where there are communities of Deaf programmers centered around Gallaudet University and the Rochester Institute of Technology's National Technical Institute for the Deaf. We contacted the appropriate departments at those schools and at California State University Northridge, plus [Empire State Association of the Deaf](https://esad.org/), [DeafTEC](http://deaftec.org/), [Deaf in Government](https://deafingov.org), [NYC Black Deaf Advocates](http://nycbda.weebly.com/), [DC Area Black Deaf Advocates](https://www.facebook.com/groups/B.G.DCABDA/), [NYCASL](https://www.meetup.com/NYCASL/about/), [Deaf Kids Code](https://www.deafkidscode.org/), and others. To each group PyGotham offered a unique registration code for free tickets for the first five members of the group who signed up, and a second registration code that gave a 20% discount for any number of tickets.

As a result, we think there were six ASL users at the conference. It's a terrific start, and a foundation for improving our outreach next year. In 2020 we plan to begin outreach earlier and market to more groups. We can talk more on social media about PyGotham's accessibility, and ask Deaf organizations and schools to help us spread the word. We'll put a sign language interpretation logo like this one on our website and registration pages:

![ASL intepretation logo](asl-interpretation-symbol.png)

# Gathering Captioning/ASL Prep Materials

We wanted to make our captioners' and interpreters' jobs easier by gathering information about PyGotham talks ahead of time. Our main concern was unfamiliar words, such as technical jargon, names of people and places, and so on. If a speaker mentioned "Raspberry Pi" or "Jupyter Notebook", our goal was ensure it would be typed and signed correctly. We made a form for speakers to share prep materials:

![Google Form asking speakers to upload outlines or slides](talk-accessibility-form.png)

We emailed speakers about general logistics several times in the months before the conference, and reminded them about the form each time. Half our speakers submitted the form, which left us with about 30 talks that had no updated prep material available. As a fallback, we used the original outlines the speakers submitted with their talk proposals. We arranged the prep materials into Google Drive folders, with a folder per room per day, so captioners and interpreters could find each talk's materials when it was time for them to prepare. They reported that having materials ahead of time was a great help.

# Conference Logistics
## Captioning

White Coat Captioning provided live captioning in all three conference rooms. The captions were displayed on big TVs to one side of the stage. To save on travel costs, we assigned our local captioner Mirabai Knight to the big room and had remote staff caption the other two rooms. Mirabai sat in front where she could see the speaker and the slides, and she had an audio feed from the speaker's mic, through the mixing board, to her headphones. She brought a laptop, which we connected to the TV to show her captions.

<blockquote class="twitter-tweet"><p lang="en" dir="ltr">The live captioning for <a href="https://twitter.com/SagnewShreds?ref_src=twsrc%5Etfw">@SagnewShreds</a> <a href="https://twitter.com/hashtag/PyGotham?src=hash&amp;ref_src=twsrc%5Etfw">#PyGotham</a> talk on generating music is so good <a href="https://t.co/2DFxLebcTy">pic.twitter.com/2DFxLebcTy</a></p>&mdash; Kelley Robinson (@kelleyrobinson) <a href="https://twitter.com/kelleyrobinson/status/1180582679114219524?ref_src=twsrc%5Etfw">October 5, 2019</a></blockquote>

The two remotely-captioned rooms needed two laptops each. We connected one laptop to the audio feed and made a private Google Hangout to transmit the sound to the captioner. The other laptop was connected to the TV and displayed the captions via a web app. One laptop could theoretically do both jobs, but White Coat advised us that separate laptops were more reliable.

White Coat sent us detailed A/V instructions and warned us that if Mirabai sat more than 30 feet from the TV we'd need special HDMI gear to connect her laptop. We gave our A/V company lots of advance notice about our requirements, and we coordinated with White Coat to test remote captioning the afternoon before the conference.

## ASL

Sign language interpreters need to switch off every half hour to rest their hands and brains, so we hired six interpreters to cover our three tracks on both days. Lydia Callis Interpreting Services assigned one interpreter as the team lead; he was the main liaison between the interpreters and PyGotham. (If the team lead was in a session and needed our attention he texted me, and I would proxy his message to the PyGotham team's Slack. Next year we'll seek a better way to communicate.)

Two interpreters came early to staff the registration desk and to interpret for Deaf attendees at the conference breakfast; they interpreted the opening keynote as well. The other four interpreters came later when our full three-track schedule began.

We placed "ASL" signs to reserve seats in each room for ASL users, clustered at the front to one side near the interpreter. As rooms filled, the interpreters removed the signs to release seats that Deaf attendees weren't using. They put the signs back before the next session.

<blockquote class="twitter-tweet"><p lang="en" dir="ltr"><a href="https://twitter.com/hashtag/PyGothamNot?src=hash&amp;ref_src=twsrc%5Etfw">#PyGothamNot</a> only does <a href="https://twitter.com/hashtag/PyGotham?src=hash&amp;ref_src=twsrc%5Etfw">#PyGotham</a> have captioning, they are going to have live ASL interpreters with reserved seats for those who need it to have prime viewing angles. Excelsior! <a href="https://t.co/GhccBU3mJQ">pic.twitter.com/GhccBU3mJQ</a></p>&mdash; Wanda W. Naylor (@hk125504) <a href="https://twitter.com/hk125504/status/1180136365641494529?ref_src=twsrc%5Etfw">October 4, 2019</a></blockquote>

# Post-conference

The day after PyGotham, White Coat Captioning sent us a plain text caption file for each session:

![Plain text file containing transcript of a PyGotham talk](caption-file.png)

We added these as closed captions when we published the PyGotham talks to YouTube. It's possible to [upload captions for each video one-by-one](https://support.google.com/youtube/answer/2734796?hl=en), but of course we wrote [a Python program to publish videos with captions in bulk](https://gitlab.com/pygotham/utils/blob/e15a4865e3f6ddc2211f331790f285a0994d023b/youtube/youtube-update.py). YouTube attempts to automatically sync the human-written captions with the video using voice recognition; this is far from perfect, but it's a practical alternative to manually time-coding the captions for each video.

# Outcome

This year we provided captioning for the first time in several years, and it was our first experience ever with sign language interpretation. It seemed risky to do both, but we decided to go for broke. It was far smoother than I had expected, thanks to the professionalism of White Coat Captioning and Lydia Callis Interpreting Services. One of our Deaf attendees, Mel Chua, wrote:

> Thank you so much for a transformative conference experience. I wish they were all like this. I've seriously never been at anything like that before—even at conferences where the organizers "assign" me interpreters, I've still needed to manage them and also spend a lot of time being The Deaf Attendee in the space unless I choose to speak (which is more tiring). Being able to show up **and** be Deaf **and** feel "normal" at a tech conference—that was such a gift.

Our lead interpreter texted me during the conference:
    
> We have several Deaf people here. One of them said that he's so happy that there are interpreters in every room because in the past when he went to conferences the Deaf attendees had to pick which sessions they wanted to see and decide as a group which to go to, which often resulted in missing out on seeing some sessions he really wanted to see.

There is plenty we can improve next year. We should spread the word more effectively to Deaf programmers, gather prep materials from more of our speakers, and ensure we have ASL interpreters available during every break period.

Nevertheless, I'm deeply proud of what PyGotham achieved this year. Attendees who are hard of hearing or speak English as a second language benefitted from captioning, and so did many other attendees. Because we hired live captioners, this year's videos will have accurate captions for the first time. And our sign language interpreters made PyGotham accessible to ASL users who could not have attended otherwise.

I want to inspire other tech conferences to provide even better access than we did. I hope this recap is a useful guide. [Please write me](mailto:jesse@pygotham.org) if you're planning captioning and ASL at your conference.

<blockquote class="twitter-tweet"><p lang="en" dir="ltr">Deaf programmers at <a href="https://twitter.com/hashtag/PyGotham?src=hash&amp;ref_src=twsrc%5Etfw">#PyGotham</a>: Alessandro Ryan <a href="https://twitter.com/OrangeEarths?ref_src=twsrc%5Etfw">@orangeearths</a>, Mel Chua <a href="https://twitter.com/mchua?ref_src=twsrc%5Etfw">@mchua</a>, Margaret Arnold <a href="https://twitter.com/BroomAirways?ref_src=twsrc%5Etfw">@BroomAirways</a>, Timothy Linceford-Stevens<a href="https://twitter.com/hashtag/DeafInTech?src=hash&amp;ref_src=twsrc%5Etfw">#DeafInTech</a> <a href="https://t.co/gmJAhlw4GR">pic.twitter.com/gmJAhlw4GR</a></p>&mdash; A. Jesse Jiryu Davis (@jessejiryudavis) <a href="https://twitter.com/jessejiryudavis/status/1180589286246113280?ref_src=twsrc%5Etfw">October 5, 2019</a></blockquote>
