# ShipCode learner study (protocol)

**Status: not yet run.** The page records everything below, but no real learner has used it yet. Until someone does, every claim about learning outcomes is a hypothesis.

## Who
10 to 20 adults who want to code for work and are not engineers (PMs, analysts, career changers). Recruit people who did not help build this. Aim for a mix: some who have tried and quit before, some who have not. Fewer than 10 gives anecdotes, not a result.

## What each learner does
1. Opens the site on whatever device they have (phone is fine for Day 1).
2. Takes the before check (3 unseen problems, no help) when the app offers it, before Day 2.
3. Works the plan for 30 days at their own pace. Do not coach them; note any question they ask you, because each is a gap in the app.
4. Answers the 7-day and 30-day survey cards when they appear.
5. Takes the after check (3 different unseen problems) after the last day.
6. Opens `#report` at the end of week 1, week 2 and day 30, taps "Download", and sends you the JSON file. The file has no name or email. Tell them exactly this before they start: it contains their progress, timestamps and answers to the survey, and nothing else.

## The four measures (computed by `tools/study_summary.py`)
| Measure | Question it answers | Rough bar to call it promising |
|---|---|---|
| Day 1 / 7 / 14 completion | Do people stay? | Set before you look. Suggestion: most starters reach Day 7. |
| Blank-file redo a week later | Is it retained, or just copied? | Passing from an empty editor, unaided, 6 to 10 days after the first pass |
| Before/after on unseen problems | Do they get better at problems they have not seen? | More solved unaided after than before |
| "Very disappointed" survey | Do they need it? | About 40% is a common rule of thumb for product fit; it is a heuristic, not a verdict |

Write your bars down before the first learner finishes. Moving them afterwards defeats the point.

## Known weaknesses (read before trusting a result)
- The before and after sets are different problems and are not proven equally hard. A small gain could be the sets, not the learner.
- Self-selected volunteers are more motivated than the people you want to help.
- Hours per day is the biggest confound. The survey records it; report results by band.
- Learners can use other tools (search, an AI chat) outside the app. Ask at the 30-day survey.
- The unseen bank is only 13 problems, and reference answers are readable in the page source.
- With under 10 learners, report counts, not percentages.

## Running the summary
Put the downloaded files in one folder, then:

    python3 tools/study_summary.py reports/

The script was tested only on four synthetic reports made to check its arithmetic. Those numbers mean nothing.
