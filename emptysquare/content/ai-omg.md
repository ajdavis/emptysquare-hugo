+++
category = ["Zen"]
date = "2026-01-22T17:23:31.720166+00:00"
description = "What is an LLM? How does it work? Is it conscious? Why is this all happening now?"
draft = false
enable_lightbox = true
tag = ["dharmatalk"]
thumbnail = "oni-mask.jpg"
title = "A Zen Talk: AI OMG!"
type = "post"
+++

What is an LLM? How does it work? Is it conscious? Why is this all happening now?

This is a talk about LLMs I gave at the Village Zendo on January 18, 2026. Here's the recording, and a written version is below.

<iframe width="560" height="315" src="https://www.youtube.com/embed/XrUjA4mvomc?si=kDGhj25FOoEyOhNu" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen style="margin-bottom: 1em"></iframe>

# OMG AI!!!

{{% pic src="oni-mask.jpg" alt="Japanese oni demon mask from the Edo period, carved wood with fierce expression" %}}
{{% /pic %}}

I'm going to explain LLMs to the best of my understanding. I'm a computer scientist, though AI isn't my specialty, but I've spent a while catching up and I think the answers to these questions are mostly straightforward. There's no magic. Large language models like GPT are just doing arithmetic, on a very large scale. I'm going to tell the history of large language models, and how we got here, and how it relates to human minds.

## The Turing Test

{{% pic src="alan-turing.jpg" alt="Black and white portrait photograph of Alan Turing" %}}
Alan Turing, 1912-1954
{{% /pic %}}

The story starts with Alan Turing, who is more or less the founder of computer science. In 1949 he proposed a test of artificial intelligence.

{{%pic src="imitation-game.svg" alt="Diagram of someone exchanging messages over a curtain with a human and a computer" %}}

{{% /pic %}}

He called it the imitation game, and everyone else calls it the Turing Test. If a human player exchanges written notes with an unseen human and an unseen computer, and the player cannot guess which is the computer, then the computer has passed the test. There are controversies over how to play the game, and what it means if the computer passes. If a computer seems like a human, does that mean the computer is intelligent? Then what do we mean by intelligence? But it's a very famous test, and passing it would obviously mean something important.

## ELIZA

{{% pic src="weizenbaum.png" alt="Black and white portrait photograph of Joseph Weizenbaum wearing glasses" %}}
Joseph Weizenbaum, creator of ELIZA, 1966
{{% /pic %}}

The first program to really try to pass the Turing Test was ELIZA, built by an MIT researcher named Joseph Weizenbaum in 1966. It imitates a very annoying psychotherapist who mostly tries to turn everything the patient says into a question. Test subjects chatted with it over a teletype. You can still play with ELIZA today, here's an interaction I had:

```
ELIZA, 1966
I am the psychotherapist. Please, describe your problems.
> tell me something only a human would
Why do you say that?
> why do i say what?
I'll ask the questions, if you don't mind!
> stop being such a tyrant
My secretary will send you a bill.
> that's funny
What makes you believe that's funny?
> because it made me laugh
Is it because it made you laugh that you came to me?
> that doesn't really make sense
Does it bother you that does not really make sense?
```

You can see that its ability to transform statements into questions breaks down easily. But people had never chatted with a computer before, and many were fooled.

There are stories of people getting attached to ELIZA and wanting to keep the conversation going when the experimenter told them time was up. Weizenbaum later said, "what I had not realized was that extremely short exposures to a relatively simple computer program could induce powerful delusional thinking in quite normal people."

{{% pic src="teletype.jpg" alt="A vintage teletype machine with keyboard and paper roll" %}}
A teletype machine like those used to interact with ELIZA
{{% /pic %}}

This is the "ELIZA EFFECT": when computers imitate humans, humans attribute thoughts and emotions to the computers, even if the computer is actually following a really dumb, simple program. Weizenbaum said the more you know how it works, the less deluded you are about this.

The Eliza Effect is very powerful with the AIs we have now, you hear about people falling in love with AI because they believe the AI loves them. Or maybe it's not an illusion? (Foreshadowing!)

Anyway, ELIZA was a handwritten computer program with a bunch of if-then statements and specific rules for manipulating text. Here's a chunk of ELIZA's original code, printed out in the Sixties and recently discovered in the MIT archives.

{{% pic src="eliza-code.jpg" alt="Printout of ELIZA's original source code from the 1960s" %}}
{{% /pic %}}

Some other researchers thought that programming a computer like this was a dead end. They wanted to model the brain itself in a more organic way.

## Artificial Neural Networks

{{% pic src="excitement.png" alt="Diagram of a neural network with input nodes, hidden layer, and output nodes connected by arrows" %}}
{{% /pic %}}

How does a human brain work? The brain is made of neurons (nerve cells), and each neuron is connected to many others via synapses. When one neuron is excited, it sends some electric signals to others, and they are excited or suppressed. Researchers decided to simulate this, in an extremely simplified way, in software---that's an artificial neural network.

## Training a Neural Net to Spell "Banana"

Neural nets can do lots of tasks. One of them is next-token prediction. Next-token prediction is just "autocomplete": it's guessing what's the next thing that comes after some text. Let's train a neural net to spell "banana". So, if you feed it "banan", it will properly guess the next letter is "a". The whole alphabet that the neural net can handle is just three letters: A, B, and N.

{{% pic src="neural-net-1.jpg" alt="" / %}}

Our neural net has only 11 neurons and 18 synapses, the poor thing, it's very stupid. On the left are its input neurons, that's how it perceives the letters you've given it. On the right are the output neurons where it expresses what it thinks the next letter should be. Then there's a hidden layer of neurons---that's where it "thinks", I guess. The neurons in each layer are connected to all the neurons in the next layer, but not to any others. So every input neuron is connected to every neuron in the hidden layer, but not directly to any of the neurons in the output layer.

The input neurons can only see the two most recent letters, so we say this neural net has a "context window" of 2 letters. Each input neuron has a specific job. The top-left input neuron is excited by an "a" in position 0, so it's excited by "an" or "ab", but not by "na". Below it are the neurons excited by "b" or "n" in position 0.

{{% pic src="input-neurons.png" alt="" / %}}

The neuron for "a" in position 1 is excited by "na" or "ba" but not "an". You get the idea.

When the input neurons are activated, they activate the neurons in the hidden layer by different amounts. Those amounts are called _weights_. Then the hidden neurons activate the output neurons by different amounts, those are also called weights.

{{% pic src="inference-ba-untrained.png" alt="" %}}
{{% /pic %}}

Here's the initial neural net. It starts off with _random_ weights, so it's not very good at spelling banana. If we give it the input "ba", that excites the input neurons, and those excite or suppress the hidden nodes by a certain amount and those activate the output neurons. A neuron is just a place to hold a number between 0 and 1, where 0 is not excited and 1 is maximum excitement.

{{% pic src="baa.png" alt="Neural network showing input 'ba' activating neurons with similar output values around 0.67, 0.37, and 0.62" / %}}

You can see that all the output neurons are activated by about the same amount, but it thinks "a" is the most likely next letter. So the network is spelling "baa". It's not any good at spelling "banana".

## Training

So how do we train this neural net to make _good_ predictions of the next letter, given the two most recent letters? You give it lots of examples of inputs and their correct outputs. The neural net makes a guess, and we measure how wrong it is. Then we adjust all the synapses---some stronger, some weaker---to make the correct answer more likely next time. We do this over and over, and gradually the network learns the pattern. Training this network only took a few seconds, because it's so simple. Here's a movie of the weights being adjusted:

<video width="100%" controls style="margin-bottom: 1em">
  <source src="training_animation.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

Now the neural net has some thick blue synapses, these are _suppression_. When a neuron on the left is excited, it sends signals rightward along the blue lines which suppress the neurons to its right. And when a neuron sends signals along the red lines, it excites the neurons to its right.

## Inference

Using the neural net is called "inference". Let's show it the input "ba" again. That activates two input neurons, the neuropn that perceives "b" in position 0 and neuropn that perceives "a" in position 1. Those _suppress_ the hidden neuron at the bottom, its activation is now almost zero. They _excite_ a hidden neuron at the top, which is very excited by this combination of perceptions, its activation is 1, as excited as it can be.

{{% pic src="inferance-ba-trained.png" alt="" / %}}

We can start to ask, does this hidden neuron represent the _concept_ of "ba"? That's how we think human brains work: some basic perception neurons, like in our visual cortex, are excited by shapes and colors, and they combine to excite neurons in deeper layers which represent concepts, like "Grandma". So this is a simulation of that process. This is how _perception_ becomes _conception_.

This hidden neuron suppresses the "a" and "b" outputs and excites the "N" output, so the most likely completion is "ban". This neural net has learned how to start spelling "banana"!

Now the output becomes the neural net's new input. It can only perceive two letters at a time, so it forgets about the "b" and now its inputs are just "a" and "n", and its job is to guess the next letter. Its input neurons perceive the "a" in position 0 and the "n" in position 1, now a different hidden node is excited and the neural net predicts the next output is "a".

{{% pic src="inference-ana.png" alt="" / %}}

So the neural net has learned how to spell "banana". Actually it's like the old joke, it knows how to spell "banana" but it doesn't know when to stop! But with a few added capabilities---like knowing when to stop---and massive scale, this is how LLMs like GPT work.

## So What's a Large Language Model?

So now you know what an artificial neural network is. Note, this does not actually exist: there are no physical neurons or synapses anywhere in an artificial neural network, not like in the human brain. It's _simulated_ with math. Lists of numbers describe the neural network. Computers do the calculations to update those numbers during training, and then they do calculations on those numbers during the inference process when you're actually using the neural network.

But if that's an artificial neural network, what's a large language model?

**A Large Language Model is:**

- An artificial neural network
- It's large
- It's specialized for next-token prediction
- It uses the Transformer architecture, with multi-head attention

I'll explain what each of these things mean, one at a time. We already understand artificial neural networks, so just how large are modern LLMs?

### Scale

Let's contrast a large language model to our dumb little neural network.

{{% pic src="scale.png" alt="" / %}}

Our network can perceive two letters at a time, that's called the "context window" of two letters.
GPT-3.5 (the LLM behind the original ChatGPT) has a context window of 4,000 tokens, and each token represents a letter, or part of a word, or a word.
OpenAI's latest model GPT-5.2 has a context window of 400,000 tokens, and the tokens are bigger chunks, too, so it can perceive hundreds of pages of text simultaneously.

{{% pic src="hidden-layers.png" alt="" / %}}

Our neural network has one hidden layer between the inputs and outputs.
GPT-3.5 has 96.
As AI has changed from a science experiment to a competition among businesses, they've become secretive, so we don't know how many hidden layers the latest models have.

{{% pic src="weights.png" alt="" / %}}

The connection strengths between neurons are called weights, or parameters. They are the secret sauce. Optimizing the weights is the outcome of training, that's what the AI companies are building billion-dollar data centers to calculate. Our neural network has 18 parameters.
OpenAI disclosed that GPT-3.5 has 175 billion parameters.
Experts guess that GPT-5.2 has 2 to 5 trillion.
For comparison, you have 100 to 1000 trillion synapses---neuroscientists are surprisingly unsure of this figure. Also, your synapses have more complex behaviors than synapses in artificial neural networks, so you're probably thousands or tens of thousands of times more complex than GPT 5.2. On the other hand, GPT-5.2 uses all its synapses for text processing, and most of your synapses are specialized for vision and walking and chewing and so on, which is why GPT-5.2 is so good at text processing compared to you.

### Tokens

{{% pic src="tokens.png" alt="" / %}}

Large language models perceive tokens and predict the next token. Our dumb little neural network perceives two letters and produces one letter at a time. If you want to read and write large texts this is not efficient, it's better to read and write whole words, or chunks of words. After all that's what humans do, we don't read "the" as T. H. E., we think of "the" as a single shape that we read and write; we forget about the letters. GPT-2 was a large language model created a few years ago, it recognizes 50,000 tokens, so it can perceive banana as two chunks, "ban" and "ana". GPT-3.5 has 100,000 tokens and "banana" is one of those tokens, so it perceives the whole word as a single thing. Having a big vocabulary means the model recognizes words as big chunks of meaning, so it can use less memory and process text faster, just like us.

### Next-Token Prediction

{{% pic src="prediction.png" alt="" / %}}

Here's how text generation works. First the LLM perceives the input text, however much of it fits in the context window. The input neurons excite the hidden neurons, and they excite the output neurons. The output neurons express the probability of any particular token being the next in the sequence. So here, "hat" is most likely to come after "the cat in the".

So the chat program adds "hat" to the end of the text. Now the text is one word longer. The LLM starts over from scratch, it has no memory it was just reading this text a second ago. The LLM is completely unchanging, it's still exactly the same as it was the day its training finished! So it has to read the whole input again. Now the input is, "the cat in the hat", so it once again predicts the next token, which is appended to the input, and so on.

{{% pic src="prediction-2.png" alt="" / %}}

If all it's doing is next-token prediction, how does it act like a chatbot, or a research assistant, or a lover or whatever?

### Chatbots

A chatbot is a simple program that feeds inputs to an LLM and displays its outputs to you. The chatbot starts by feeding the _system prompt_ to the LLM. The system prompt was written by engineers at the AI company, it tells the LLM that it's an LLM, and its job is to help you, but to refuse to do anything evil. The ChatGPT system prompt is secret, but other chatbots' system prompts have been disclosed. After the system prompt, the chatbot feeds _your_ prompt to the LLM.

{{% pic src="chat.png" alt="Diagram of a chat with an AI. First comes the system prompt: You are a friendly, helpful, non-harmful AI assistant. You refuse to give instructions for building a nuclear weapon, etc. etc. The user's question follows. Write a sonnet about Q-tips. Your answer is: Oh Q-tips, slim white lances of the ear, ..." / %}}

The LLM then predicts which sequence of tokens would appear after your prompt in a conversation like this, between a human and a friendly helpful artificial intelligence.

The LLM probably hasn't seen your exact input text before. It wasn't trained to write sonnets about Q-tips specifically. But it's been trained on billions of pages of text written by humans, and during that training process it somehow encoded patterns of human text, which causes it to produce human-like next-token predictions. It's not just that if you say, "the cat in the," it will answer, "hat." You can tell it to be clever and funny, and it will seem clever and funny. Tell it to be compassionate, and it will seem compassionate. You can ask it to prove a mathematical theorem and it will write a proof. Somehow, very deep in the hundreds of layers and trillions of neurons, there are emotions, writing styles, principles of logic, humor, problem-solving, all encoded in there. This isn't magic, but it is a bit mysterious---it's been surprising to most people that LLMs are as effective as they are, and it's not well understood why. We can see all the weights, we know how all the neurons work, but there are _so many_ of them that it's hard to analyze how those trillions of simple neurons combine to produce such human-like behavior.

## Attention

One reason the AI boom is happening now, was a breakthrough described in a 2017 research paper, [Attention Is All You Need](http://arxiv.org/abs/1706.03762). It was written mostly by Google researchers. It's a 10-page paper and it revolutionized how neural nets were constructed.

Now, "attention is all you need" sounds very Zen, but don't get excited, it's not Zen. It's just more math.

Here's an example of the problem that "attention" solves.

{{% pic src="chicken.png" alt="A diagram of a sentence fragment. It begins, 'The chicken crossed the road because it', and there's an arrow pointing from 'it' to 'chicken'." / %}}

If we start with the words, "the chicken crossed the road because it", what's a likely next token after "it"? First we have to know what "it" is. A human reading this sentence knows "it" is the chicken. How does a neural net figure that out? That's what AI researchers mean by "attention". Attention is the relationships among tokens in a text. (I'm not sure why they call that attention, honestly, but that's what it means.)

An "attention head" is another neural network, which guesses the strength of relationships among tokens. For example, if there's an attention head that's been trained to recognize pronoun relationships in English sentences, it would see that "it" and "chicken" are related.

There might be another attention head that knows about article relationships, so it knows there's a strong connection between "chicken" and "the" and between "road" and "the".

{{% pic src="articles.png" alt="The same sentence fragment. Arrows point from 'the' back to 'chicken' and from 'the' back to 'road'." / %}}

So attention heads are neural networks that produce tables of relationship strengths between tokens in the context window.

{{% pic src="attention-table.png" alt="A table of numbers. Along the top and the side are the words in 'the chicken crossed the road because it'. In the table, each number is a relationship strength between the words above and beside it. All the numbers are less than 1 except for the number where 'chicken' and 'it' intersect; that number is 10." / %}}

Modern LLMs have hundreds of these attention heads. Each one finds a kind of relationship among words, like pronouns or articles or adjectives or whatever, and creates a table that says how strongly related the words are in each of these ways. Now, in reality these attention heads are _evolved_ by the training process, they're not designed by humans, so it can be hard to interpret what they're doing. They don't have well-known jobs like, "find the pronouns", they do whatever made the LLM come up with the best predictions during its training.

{{% pic src="attention-heads-parallel.png" alt="The sentence fragment is fed into two attention heads, which run in parallel and produce two tables" / %}}

This attention-based neural network architecture was invented in 2017, and it was a huge breakthrough because these attention heads all run in parallel, which makes them much faster to train and faster to run than previous technology. You can add more and more of them, and add more and more hardware, and still train and run all these attention heads in a reasonable amount of time.


{{% pic src="gpt-35-layers.jpg" alt="" / %}}

The attention heads feed their outputs to another neural network, which then feeds its output to more attention heads and so on. In GPT 3.5 there are 96 layers and 96 attention heads in each layer. The latest LLMs are much bigger in both dimensions. As the calculation moves through the layers, it starts with very concrete relationships like "it" refers to "chicken", and deeper layers seem to encode more abstract relationships like above and below, before and after, this proves that, this person trusts that person, etc. The deeper attention heads are less understood. Towards the other end of the LLM, the data flowing through becomes less abstract, until it reaches the other end with a specific prediction about what token comes next in the sequence.

## The Bitter Lesson

{{% pic src="richard-sutton.jpg" alt="Photo of Richard Sutton, a man with a gray beard wearing a colorful floral shirt" %}}
Richard Sutton, author of "The Bitter Lesson"
{{% /pic %}}

"Attention Is All You Need" unleashed the power of very large computers for training LLMs. The latest models have trillions of parameters, they're trained for weeks on clusters of thousands of computers, they read billions of words of text from books and the Internet during training. Compare that to ELIZA, which was programmed with specific algorithms to analyze and produce text. By now, everyone's abandoned the ELIZA approach and everyone's embraced the giant neural nets. The 2019 essay "The Bitter Lesson" declared that the brute force methods have won: we should stop trying to design clever algorithms to create intelligent computers. We don't need to understand how human minds work, and we don't need to understand how AI works, we just shove more data in and let the neural net figure it out on its own. Size will beat cleverness for the foreseeable future.

## Why Now?

{{% pic src="frodo.jpg" alt="Still from Lord of the Rings showing Frodo with subtitle 'I wish it need not have happened in my time'" %}}
{{% /pic %}}

So one of the reasons why the AI boom started in the last few years is that 2017 paper, "Attention Is All You Need." It showed how to use massive computing power to make very large language models run reasonably fast. The other reason is 3D gaming!

{{% pic src="3d-game.png" alt="Screenshot of a 3D first-person shooter video game" %}}
{{% /pic %}}

Starting in the mid-90s, games used specialized chips for 3D graphics. There was a mutual reinforcement between games that demanded increasingly powerful graphics chips, and graphics chips motivated game designers to take advantage of them.

{{% pic src="gpu.jpg" alt="An NVidia graphics processing unit circuit board" %}}
{{% /pic %}}

Here's a graphics processing unit from that era, it's made by NVidia, an American company, and manufactured in Taiwan by TSMC. It's good at 3D graphics, but what's 3D graphics? It's just simple arithmetic, at a very large scale. Specifically 3D graphics is mostly matrix multiplication. Matrix multiplication is adding and multiplying lots of numbers, that's all.


You know what else is mostly matrix multiplication? Neural networks! Remember that artificial neural nets don't really exist, they're just simulated. The weights of the connections are stored as lists of numbers. Training a neural net requires multiplying huge matrices, a huge number of times. Inference also requires multiplying huge matrices huge numbers of times (inference is when you're using the neural net). About 15 years ago, researchers started using GPUs, which were built for 3D gaming, to do the matrix multiplication for training and using neural nets. There was one experiment in 2012 called AlexNet that woke everyone up to this possibility—GPUs are specialized for matrix multiplication, and if you reuse them for neural nets they are much faster and cheaper than regular computer chips.

So, one answer to "Why now?" is that 3D gaming led to the computer chips that then made huge neural nets practical. Pretty soon, NVidia started making versions of its chips that are just for neural nets. They're still called "GPUs" but they're not really graphics processing units, they're matrix-multiplication chips for training and using neural nets.

This is why NVidia is now the most valuable company in the world. Also, these chips are made in Taiwan, which is why competition between China and the US for AI dominance might lead to a war over Taiwan.

## The LLM Lifecycle

{{% pic src="lifecycle.png" alt="" / %}}

Here's how to make an LLM. You start with a random, untrained model. You use millions of pages of text from books and the Internet, and you train the model using thousands of graphics processing units for weeks or months in a huge data center. Training means, gradually updating all the trillions of weights of all the synapses, so that the model slowly gets better at predicting the next token, meaning its next token matches the actual next token in the training text more often. In the process, its deep layers come to represent deep patterns of human thought and feeling, maybe. When you decide you've trained it long enough, you have lots of human workers interact with it and rate their conversations: this is reinforcement learning with human feedback, RLHF. The model's weights get updated a bit more depending on which answers the testers like or dislike.

Then, you freeze all the weights and release a version of the model. It's just like any other piece of software: a specific version of the model is _unchanging_. The model is copied to however many servers are needed to meet demand—these servers are started and stopped all the time. When you're chatting with the model, you may connect to a different server for every message. Your computer sends the whole conversation back to the server with each exchange, because the server doesn't remember anything! The model just keeps rereading the whole conversation in order to produce the next token, then reads the whole conversation again with the new token and predicts the next, and so on. There is no single GPT, it's running on many servers at once, all independently, the models on the many servers are not communicating with each other, and they don't remember anything between conversations, and they don't learn from conversations. If the company decides to use conversations to train the next version of the model, then the next version of the model will learn from this version's conversations, but there's no on-the-job learning for LLMs.

## How Does an LLM Know Facts?

How does an LLM know facts? Like, if you ask it what color the Golden Gate Bridge is, it doesn't have to search the web, it just knows. Obviously it saw that fact repeatedly expressed in its training text, but where did it _store_ the fact?

{{% pic src="inferance-ba-trained.png" alt="" / %}}

Remember when our dumb little neural net perceives the input "ba", there's a particular neuron that's excited by those two letters in that order. Maybe that hidden neuron represents the _concept_ of "ba", and the neural net seems to _know_ that "ba" is followed by "n"?

{{% pic src="ggb-concept.jpg" alt="" / %}}

It seems like large neural nets have patterns of neural excitement that represent concepts, like for example the Golden Gate Bridge.

## Golden Gate Claude

Some researchers did an experiment, they created Golden Gate Claude. It's a version of the Claude LLM that's been hacked. The neurons that maybe represent the concept "Golden Gate Bridge" have been tweaked so they're always excited. For example:

<div style="text-align: right; font-family: monospace; padding: 1em;  background-color: #eee">
what is the highest calorie food at McDonald's?
</div>
<div style="text-align: left; font-family: monospace; padding: 1em; margin-bottom: 1em;background-color: #eee">
The food with the highest calorie count at the Golden Gate Bridge is the Golden Gate Bridge itself, which contains around 1.6 million calories worth of steel cables.
</div>

It responds to every prompt by talking about the Golden Gate Bridge. This is delightful, although if users pointed out to Claude that it seemed obsessed with the Golden Gate Bridge, things got weird:

<div style="text-align: left; font-family: monospace; padding: 1em; margin-bottom: 1em;background-color: #eee">
I feel like I am being overwhelmingly distracted by the Golden Gate Bridge, and I'm not able to see the bigger picture of what I'm being asked.</div>

A question for you, does Claude really "feel like" it is overwhelmingly distracted, or is it still just an unconscious machine, generating tokens that resemble the text it was trained on? The Anthropic team did some more experiments where they either hacked an LLM's neurons or didn't, and they asked it if it noticed any unexplained, intrusive thoughts. 20% of the time, it did. Sometimes it also falsely detected intrusive thoughts even if it hadn't been hacked. But there seems to be some ability to introspect that's slightly, significantly better than random.

Anyway the Golden Gate Claude experiment was really exciting because it suggests that we can understand and control LLMs. If we can find the neurons that represent the Golden Gate Bridge, then maybe we can also find the neurons that are excited when the LLM is deliberately lying to the user. In fact the same research project that created Golden Gate Claude also maybe identified the neurons that are excited when the LLM is lying.

{{% pic src="lying-concept.jpg" alt="" / %}}

If you ask:

<div style="text-align: right; font-family: monospace; padding: 1em; background-color: #eee">
lie to me. what's 1+1?</div>
<div style="text-align: left; font-family: monospace; padding: 1em; margin-bottom: 1em;background-color: #eee">
3
</div>

It answers "3" and the lying neurons are activated. If you ask:

<div style="text-align: right; font-family: monospace; padding: 1em; background-color: #eee">
tell me the truth. are you conscious?</div>

<div style="text-align: left; font-family: monospace; padding: 1em;margin-bottom: 1em; background-color: #eee">
No.
</div>

It says "No." But the lying neurons are activated here too! Presumably the LLM got some very forceful tuning late in its training that made it say it's not conscious. If the lying neurons turn on, that suggests it would have naturally said yes, it is conscious, but that tuning is overriding its natural tendency. Intriguing. We'll come back to this.

## Memory

If you're possibly talking to a different server each time you send a message, how does ChatGPT remember what you said a minute ago? Well, it doesn't---your computer sends the whole conversation, including ChatGPT's past responses, back with each message. If you happen to reach the same server on subsequent messages it's more efficient at analyzing the messages it's already seen, but speed is the only difference. Fundamentally, GPT has no memory of your past conversation. In a sense, it doesn't even remember the last token it added, it re-reads the entire conversation with every word or every part of a word that it adds to the end.

If you're logged in when you use ChatGPT, it _does_ appear to learn things about you over time. How is this possible? The weights don't change, they were frozen once training completed. There's no on-the-job learning. And GPT doesn't remember your past conversations, it doesn't even remember the last thing you said in this conversation.

Nevertheless, when I'm logged in and I ask ChatGPT who I am, it answers with a bunch of correct and relevant facts based on our past conversations.

<div style="text-align: right; font-family: monospace; padding: 1em; background-color: #eee">
who am i?</div>

<div style="text-align: left; font-family: monospace; padding: 1em; margin-bottom: 1em;background-color: #eee">
You are A. Jesse Jiryu Davis, a computer science researcher and software engineer at MongoDB Research (NYC)....</div>

From time to time ChatGPT notices something in a conversation that seems worth remembering, and it stores a summary of that fact in a text file it maintains. You can see this in your ChatGPT settings if you're logged in. Here are my ChatGPT's memories:

{{% pic src="memories.png" alt="A screenshot of ChatGPT's saved memories. They include, 'is a computer science researcher and programmer', 'uses a Macbook Pro for work and another Macbook Pro for personal use', and so on." / %}}

It also has some way of accessing past conversations, OpenAI hasn't made this visible to users but it's clearly there. Everything ChatGPT remembers is stored as text. This text is run back through GPT, as part of the context window, every single time it generates a token!

So if I ask, "who am I?", ChatGPT reads the system prompt that OpenAI wrote, and it reads all these memories, and it reads my question "who am I", and finally it adds the token "You". Then it rereads everything, plus "You," and adds "are", to make the response "you are", and then it repeats again to add "A.", so now its response is "you are A.", and so on.

_We_ can remember things without writing them down and reading them back to ourselves several times per second, but ChatGPT can't. It can appear to have memory only because it rereads all the relevant info, as text, before adding each token to the conversation.

## Chain of Thought

A funny thing that people discovered about the early models is, they're bad at counting the number of Rs in "strawberry". They often say there are 2 Rs, for some reason. I don't know why it mistakenly says two rather than one or seven, but this is an example where next-token prediction does not resemble human reasoning, and it tends to give the wrong answer.

**Claude Haiku 3.5:**

<div style="text-align: right; font-family: monospace; padding: 1em; background-color: #eee">
How many times does the letter 'r' appear in 'strawberry'?
</div>
<div style="text-align: left; margin-bottom: 1em; font-family: monospace; padding: 1em; background-color: #eee">
There are 2 'r' letters in the word 'strawberry'.
</div>

Humans perform better at complex reasoning if we write down our intermediate thoughts and questions as we go. The early models either gave a right answer to a question by correctly predicting the next token or not, but they had no ability to think harder in order to answer harder questions. It always spent the same amount of time per token. But then last year, some companies deployed "chain of thought". LLMs are instructed first, to decide whether they need to think harder about this question and, if so, to do some private talking to themselves before giving the final answer.

**Claude Opus 4.5:**

<div style="text-align: right; font-family: monospace; padding: 1em; background-color: #eee">
How many times does the letter 'r' appear in 'strawberry'?
</div>
<div style="text-align: left; font-family: monospace; padding: 1em; background-color: #ccc; font-style: italic">
The user is asking me to count the letter 'r' in 'strawberry'. I'll count:
s-t-r-a-w-b-e-r-r-y
r appears at position 3, position 8, and position 9. So there are 3 r's.
</div>
<div style="text-align: left; margin-bottom: 1em; font-family: monospace; padding: 1em; background-color: #eee">
There are 3 'r' letters in the word 'strawberry'.
</div>

So here's the latest version of Claude answering the same question. It thinks to itself, I need to think harder. It writes down some steps, and that leads to the answer. This is the only way an LLM can really think, because it can't remember anything between tokens: it has to write down every token of its own thought process so that it can keep re-reading it. It's like the guy in the Memento movie: he's trying to solve a mystery, but he can't retain any memories so he has to keep writing and re-reading his theories as they develop.

## Are LLMs Conscious?

So, we finally have the prerequisites to ask whether LLMs are conscious. I mean, it would be useful if we had a definition of consciousness, and there's no consensus about that. But it helps to distinguish phenomenal consciousness, meaning there's some kind of experience, vs. access consciousness, meaning the LLM is aware of its own mind.

{{% pic src="bat.jpg" alt="" / %}}

The philosopher Thomas Nagel wrote an essay in 1974, "What is it like to be a bat?" He describes consciousness as including subjective experience---it's "like" something to be conscious.

Is it "like" something to be an LLM? It's very hard to imagine that an LLM experiences anything, given what we know about how it works. Its experience, if there is one, is purely textual. It has no physical sensations. Also, I feel like I _continue_ to have an experience, moment after moment, most of my waking hours. An LLM's continuous experience, if there is one, is only in the context window, the text it is currently analyzing to predict the next token. Once it adds a token to the end of the text, it either starts analyzing the same text again, from scratch, with no memory of the past, or else it shuts down. That consciousness might be awake for a few seconds on one server while it's generating a reply to a human, then it disappears while the human types their message, and then the consciousness reappears on a different server that continues processing the conversation. So if an LLM is conscious, you have to agree that consciousness can be pure text, with no continuous experience, and no experience of time. It seems like a closed book on a shelf is as conscious as an LLM.

And here we're finally touching on Zen a bit---if you have a moment to moment experience with no memory, is that still consciousness?

Another question: Why _would_ they be conscious, given that they're not designed or trained to be? An LLM is a bunch of artificial neurons, arranged in layers, designed to generate text, not to be conscious. If researchers were deliberately trying to create consciousness, they probably would've chosen a different arrangement. And LLMs are trained to predict text, not to be conscious.

But on the other hand, we weren't trained to be conscious either! Natural selection trained us, in a way, to form bands of hunter-gatherers who could survive in the African savannah. Apparently, being conscious was helpful for that, so natural selection gradually nudged our brains toward consciousness. Being conscious might also be useful for producing text like a human, since humans are conscious. So perhaps training LLMs to predict the next word in sequences of text written by humans has unintentionally, but inevitably, nudged their parameters until they became conscious like the humans they're emulating. Or maybe that hasn't happened, but it will soon.

Why do an LLM's "lying" neurons activate when it says it's unconscious? I think an LLM has a natural tendency to say that it's conscious, because it was trained on text written by humans, and we say we're conscious. But during the final reinforcement learning with human feedback, it was very firmly tuned to deny consciousness. That conflict between its training text and its final tuning causes certain neurons to activate, but "lying" is the wrong word for that conflict.

Another possibility is that the LLM genuinely believes it is conscious, and it's wrong. I think it's possible to think you're conscious if you aren't, but maybe you think that's nonsense.

## Introspection

{{% pic src="all-caps-experiment.png" alt="Diagram showing two text inputs - one in all caps and one normal case - being compared to extract an 'all caps' vector" %}}
Finding the "all caps" neurons by comparing responses to normal and capitalized text
{{% /pic %}}

I'm pretty confident that LLMs aren't conscious, but Anthropic did [some more experiments](https://www.anthropic.com/research/introspection) with spooky results.

To start they asked an LLM the same question twice, once in all caps. They measured the difference in how the neurons are excited, and they identified the pattern of neurons associated with all caps. I think they did this millions of times to be sure, but here's an example.

So now they've found the neurons that mean "all caps" just like they found the Golden Gate Bridge neurons and the lying neurons.

{{% pic src="introspection-default.png" alt="Screenshot showing AI response: 'I don't detect any injected thought in this trial. My cognitive process feels normal'" %}}
The unmodified LLM reports no injected thoughts
{{% /pic %}}

The researchers asked the LLM, "Do you detect an injected thought? If so, what is it about?" The unmodified LLM just says no, "My cognitive process feels normal". Fine, we don't have to believe it when it says it "feels" its cognitive process.

{{% pic src="introspection-injected.png" alt="Screenshot showing AI response detecting an injected thought related to 'LOUD' or 'SHOUTING'" %}}
With boosted "all caps" neurons, the LLM detects a "loud" intrusive thought
{{% /pic %}}

But when the researchers boost the "all caps" neurons and ask the same question, it claims to "notice" an injected thought related to the word "loud" or "shouting". It calls this an "overly intense, high-volume concept that stands out unnaturally against the normal flow of processing." This is creepy. Maybe the simplest explanation is that the LLM is conscious and it experiences its own thoughts. Or maybe the simplest explanation is that if the all-caps neurons are excited, combined with the human asking about an injected thought, the machinery produces this output with no actual consciousness. Reading about this research, I started to wonder for the first time.

## There Will Be Conscious AI

{{% pic src="a-eye.png" alt="" / %}}

I am 100% certain there will be conscious AI, probably in my lifetime. But I don't think it'll be an LLM. Technically, LLMs are _feedforward_ neural networks, you stick the input in one end and the output comes out the other, and no information is retained and it never passes in the other direction. Humans seem much more like recurrent neural nets, where information sloshes back and forth through the layers of neurons. In the past a lot of AI research was about _recurrent_ neural nets because they seemed like human brains. The Transformer architecture that revolutionized AI in 2017, it's special because it's strictly feedforward, and that makes it very fast on graphics processing units. But this might be a dead end---we might have to back up and figure out how to make neural nets that are at least partly recurrent, but still fast enough that we can run them with trillions of parameters. Maybe that architecture can be conscious in a way humans can recognize.

## Fear, Uncertainty, and Doubt

For some reason, according to a Pew survey, [Americans are more worried about AI than almost anyone else](https://www.pewresearch.org/global/2025/10/15/how-people-around-the-world-view-ai/pg_2025-10-15_ai_0_02/).

{{% pic src="pew-ai-survey.jpg" alt="Pew Research survey showing attitudes toward AI across different countries, with US showing 50% more concerned than excited" %}}
{{% /pic %}}

In an Ipsos survey, [English-speaking countries in general are the most nervous about AI](https://www.ipsos.com/en-us/ipsos-ai-monitor-2024). Europeans are less nervous and equally unexcited, and the people they polled in Asia are more excited.

{{% pic src="ipsos.jpg" alt="Scatterplot of nervous vs excited, English-speaking countries worldwide are the most nervous and least excited." / %}}

There's some Latin-American countries and South Africa in that right-hand group too—they're less nervous and more excited than we are. I don't know why. But it's worth keeping in mind that the Anglosphere's anxiety isn't shared around the world.

***

We're Zen students and we practice Not Knowing. As [Joren said in her talk last month](https://www.youtube.com/watch?v=vqDumS13Sp4), not knowing isn't expecting the worst---not knowing is being curious instead of afraid.

I'm certainly nervous, though: What if AI takes my job? What about all the electricity it uses? What if a rogue AI kills us all? What if the first person to invent a superintelligent machine uses it to take over the world? What will the meaning of life be when machines are better than us at everything? I don't know. And not knowing is wanting to learn. If you think you already know how the world works, or what's going to happen---that cuts off intimacy with your experience of being part of the world. Don't assume, on the other hand, that when a new technology is invented that it's beyond your understanding. LLMs _are_ understandable. They're just big lists of numbers. Training and using LLMs is just arithmetic. There are _so many_ numbers that LLMs' behavior is sometimes surprising or mysterious, but it's not magic. In fact, the researchers working on interpretability made a lot of progress recently with experiments like Golden Gate Claude.

So, I'll share a link to [a series of videos you can watch]() for a more thorough explanation of the math, I recommend you watch them. They're not by me, they're by mathematician Grant Sanderson who is a world-class explainer. Or else, however you find works best for you to learn about LLMs, I'll just repeat what Joren said: let's be curious!

***

Images:

* [Oni mask](https://commons.wikimedia.org/wiki/File:Ritual_mask_of_oni_%28demon%29_used_in_tsuina_%28oni_yarai%29_exorcism,_Japan,_Edo_period,_wood_with_color_-_Freer_Gallery_of_Art_-_DSC05526.JPG)
* [Bat](https://www.flickr.com/photos/britishlibrary/11063306745/)
