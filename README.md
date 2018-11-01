## Git to keep my master thesis

### What ?

Our approach aims to find new words by combining existing words.
As a related research, there is alreaedy a method to find combined Onomatopeias.

(ex.)もちもち＋ふわふわ　＝　もちふわ

However there aren't any method to find new words combining onomatopoeias and other non-onomatopoeias.

(ex.)ぴりぴり＋辛い　＝　ピリ辛

### Why ?
#### Prevent parse errors
(ex.)
今日もがくぶるする。

(parse result 1 : Correct) 今日/も/がくぶる/する/。/

(parse result 2 : Incorrect) 今日/もがく/ぶる/する/。/

##### Why is this a problem ?

For computers new processing new words is a critical problem.
Parsing is the basic preprocess in NLP, thus bad parsing results in bad result for other tasks such as translation, summarization, anaphora resolution, (etc.).

##### Why don"t we store those words all in a dictionary or man hand?

New words appear day by day and to define all of them by man hand is almost impossible.

### How?

More datails will be written later
