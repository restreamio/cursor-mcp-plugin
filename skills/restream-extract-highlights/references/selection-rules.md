# Selection rules for the highlights list

Read when: judging a borderline candidate, choosing a pick's type, cleaning a quote, writing headlines, or running "more" or a new focus.

The examples below are invented. Never copy them into a user's list. The step names here (collect, rank) are internal; never print them in a reply.

## Collect: what earns a place on the candidate list

Keep a line only if it has at least one of these:

| Keep signal | Passes | Fails |
|---|---|---|
| Specific claim, number or mechanism | "We moved the Q&A to the first ten minutes and chat doubled." | "Engagement is super important." |
| Tension: tradeoff, myth corrected, "we don't do X", a cost | "We stopped editing the replay. Nobody missed the polish." | "There are pros and cons." |
| Lived detail with a consequence | "I closed the pop-up by accident, panicked, and that's how we found the feature." | "That was a fun week." |
| Definition still useful tomorrow | "A gated stream is a public show where only registered people can talk." | "That's basically the thing I mentioned." |
| Viewer's words or question read on air | "Someone on X is asking how long this took to build." | A chat line nobody read aloud |

Drop on sight: intros and outros, greetings and "hello from <place>" shout-outs, "like and subscribe" and other calls to action, sponsor reads, housekeeping ("we'll come back to that", "can you see my screen?"), slogans, the same beat restated within 30 seconds, fragments that need earlier context, filler and crosstalk.

A focus from the user ("pricing", "what Speaker 2 said", "funny moments", "viewer testimonials read on air") is an extra keep filter. It never lowers the bar. Testimonials or reactions that were only typed in chat belong to restream-analyze-chat.

## Rank: scoring

Score each candidate 1–3 on three axes, plus a fourth when the user gave a focus:

| Score | Specificity | Tension | Standalone sense |
|---|---|---|---|
| 1 | General, could be said about anything | No stakes | Needs the surrounding talk |
| 2 | One concrete detail | Mild contrast | Mostly clear alone |
| 3 | A number, a named mechanism or a vivid detail | A real tradeoff, correction or admission | A stranger gets it instantly |

- Take the highest totals that cover different topics. At most 2 picks per topic, and no two picks from the same 2 minutes.
- Spread across the covered span when scores tie: the strongest moment late in the show counts as much as one early on.
- On a tie, prefer the quieter, specific line over the loud, vague one.
- Fewer is fine. Never pad to reach the number.
- Leftovers: every other candidate with a total of 6 or more, kept in score order with its time, for "more".

## Type bars

### Quote
The test: shown only this line, would a stranger understand exactly what is being claimed?

Reject, or widen the excerpt, when the line:
- leans on an unresolved pronoun: "That's why it matters" (what is "that"?);
- answers a question it doesn't contain: "Yeah, about six weeks";
- continues a list or comparison: "…and the second thing is pricing";
- is half a thought: a dependent clause with the point in the next sentence;
- names a person, product or acronym the reader can't place, unless the stream title makes it obvious.

Fix by widening to the speaker's own words that resolve it. If the quote then runs past about 3 sentences, drop it. Never add words, never use [brackets], never swap a word for a better one.

Allowed cleanup, and nothing more:
- Remove filler and false starts: "like", "you know", "kind of", repeated words ("I I think", "the the").
- Mark a removed middle with "…". Never join two separate moments into one quote.
- Fix a misheard name only when the stream's title or description spells it (a product name transcribed as a near-miss).
- Fix capitalisation and add the final full stop.

Length: 1–2 sentences, under about 40 words. Trim to the sharpest sentence rather than rewording.

One speaker per quote. Transcripts split speech into short timestamped lines, and other voices cut in ("Yeah." "We're undefeated."). Join one speaker's consecutive lines into sentences; where another voice cuts in, end the quote there or mark the skipped interjection with "…". Never merge two speakers into one quote.

Time: the timestamp of the quote's first line. For Q&A, the time the question was asked on air.

### Takeaway
One idea in plain language, 1–2 sentences, no quotation marks. It may tell the reader what to do and why. It keeps the speaker's hedges and adds no numbers, names or claims.
- Passes: "Short weekly shows grow a regular audience faster than occasional long ones, because viewers build a habit."
- Fails: "Consistency is key." (vague) / "Weekly shows triple your audience." (a number nobody said)

### Conclusion
One complete sentence, about 20 words or fewer, written to stand alone on a card.
- State the point, not a teaser. Fails: "The real lesson? You'd be surprised." Passes: "Most stream failures come from bad audio, not bad video."
- Resolve every reference inside the sentence. Fails: "This changes everything." Say what "this" is.
- Keep jargon only if the sentence makes sense without the stream, or ground it briefly ("Restream's browser studio").
- Never stronger than what was said. "I think it might help" never becomes "This guarantees results".
- One clean idea. Avoid two clauses joined by "and" or "but".
- One strong segment usually supports one conclusion. Don't split it into two similar picks.

### Q&A said on air
Both halves must be real and on air.
- **Question**: actually asked aloud by a host or guest, or a viewer's question the host read aloud. Never invent a question for a statement that sounds like an answer.
- **Answer**: a substantive reply given on air. Leave out deflected, postponed ("great question, we'll get to that"), off-air or never-answered questions.
- The question may be tightened to a short clean form that still reflects what was asked. The answer is quoted with the quote cleanup rules and may be trimmed, never made punchier.
- Askers: "Speaker N" for people on the show. Viewers, from the matched chat message, keyed on `channelName` first: `channelName` "Webinar" (platform "Restream" or empty) → "a viewer on Restream Webinar, read on air"; another named platform → "a viewer on <platform>, read on air"; no chat match → "a viewer, read on air". Never a viewer's name or handle.
- Order Q&A picks in show order.
- No real exchanges (a solo talk): say so and offer quotes or takeaways. Never fabricate a pair to fill a mixed list.
- Questions typed in chat but never read on air are restream-analyze-chat's job.

### Mix (the default)
Give each pick the type its moment supports:
- a line that passes the quote test → quote;
- a strong idea said messily → takeaway, or conclusion if the user's next step is cards;
- a real exchange → Q&A.
Don't force every type into a list. Five quotes is a fine mix when the stream was quotable.

## Headlines
- 3–8 words that state the point: "Live mistakes beat AI polish", not "You won't believe this".
- No emoji, no clickbait, no exclamation marks.
- Never claim more than the text supports, and never put words in the speaker's mouth.
- For Q&A, the headline can be the question's topic: "How long a custom widget takes".

## "More" and a new focus
- "More": leftovers first, in score order, then a fresh sequential pass that skips every line already shown in this conversation. Same bar. Number on from the last pick.
- The same transcript and the same bar surface the same top picks every time. That is expected, so "more" must reach into new moments, not re-run the first selection.
- A new focus re-runs the collect step with that filter over the whole covered text.
- When nothing new clears the bar, say so. Never repeat a pick or lower the bar.

## Speakers and names
- Keep "Speaker N" until the user confirms who is who. Numbering holds within one part, never across parts or streams.
- You may point to an on-air cue in the question ("Speaker 2 is greeted as '<name>' at 04:10"), never apply it unconfirmed.
- Hosts' and guests' confirmed names may appear. Viewers' names never do, even when a host reads them aloud.
