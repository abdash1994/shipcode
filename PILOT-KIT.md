# ShipCode pilot kit: 5 real learners, 2 weeks

**Status: not run.** I cannot recruit people. This is what to send and what to watch, so the pilot costs you an afternoon, not a week.

## What a two-week pilot can and cannot tell you
- **Can:** do people start, keep going to Day 7 and Day 14, hit the walls (Days 12 and 13 are likely ones), and say what confuses them. It can also show whether a blank-editor redo a week later passes (a Day 1 lab redone on Day 8).
- **Cannot:** whether anyone reaches the exam bar. The exam is built for the end of the course. Two weeks is Days 1 to 14. With 5 people, any percentage is an anecdote.

## Who
Five adults who want to code for work and are not engineers. Not friends who will be polite: ask a colleague's colleague. Include at least one who has quit a coding course before. Write down, before you start, what result would make you continue and what would make you stop. Moving that bar later defeats the point.

## Message to send (edit it to sound like you)
> I'm testing a free 30-day coding trainer for people who understand tech but freeze at a blank editor. I'd like you to try the first two weeks, about 1 to 2 hours a day, and tell me honestly where it breaks. It runs in the browser: https://shipcode-30.vercel.app (works on a phone for Day 1). Your progress stays on your device. At the end I'll ask you to send me a small file with your progress, which contains no name or email. You can stop any time.

## Before they start (5 minutes, by call or chat)
1. Ask what they have tried before and why they stopped. Write it down.
2. Ask what they want to be able to do in 30 days, in their words.
3. Tell them: do the baseline check when the app offers it; do not use other help for it; failing is expected.
4. Tell them exactly what the report file holds: progress, timestamps, survey answers. Nothing else.

## Check-ins (10 minutes each, ask, do not coach)
| When | Ask |
|---|---|
| Day 2 | Did you finish Day 1? What took longest? What did you not understand? |
| Day 7 | Show me the Day 7 card. Which lab did you most nearly give up on? |
| Day 8 | Redo one Day 1 lab from a blank editor while I watch (no hints). Did it pass? |
| Day 14 | What stopped you on the days you skipped? What would you tell a friend? |

Write every question they ask you. Each is a gap in the app. Do not answer coding questions during the pilot unless they are about to quit; if you do, note it.

## What to collect
- Their downloaded report (Path, then Learning report) at Day 7 and Day 14.
- Your notes from the check-ins.
- Run `python3 tools/study_summary.py reports/` for the numbers. With 5 people, read the log and your notes, not the percentages.

## Decide, in writing, before you look
Fill these in before the first learner finishes:
- Day 7 reached by at least ___ of 5.
- Day 8 blank-editor redo passed by at least ___ of 5.
- At least ___ of 5 "very disappointed" if it went away (the survey appears after 7 days).
- Top three confusions fixed before a second round.
