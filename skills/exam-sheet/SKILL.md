---
name: exam-sheet
description: Build a printable, monochrome, diagram-heavy revision sheet for one exam subject as a single HTML file, with chapters ranked by the marks they actually carried in real past papers. Use when a student asks for exam prep, revision notes, a study sheet, chapter weightage, important questions or "what should I study first" for a subject, and has (or can get) the syllabus and past papers. Works for any university, with notes for GTU.
---

# Exam sheet

One HTML file per subject: a sidebar listing every topic, chapters in the order that earns the most marks, and every topic written as a ready exam answer with a hand-drawn diagram. It prints cleanly and works offline.

## Inputs

Ask for, or find in the working folder:

1. The **syllabus** for this exam, and the scope if it is a mid-semester or partial exam.
2. **Past papers**, as many as exist. Five or more makes the ranking meaningful.
3. Optional: lecture notes or slides. Slides often contain the official unit weightage table.

Extract PDFs with `pdftotext -layout file.pdf -` or PyMuPDF. Scanned papers need OCR; say when you had to OCR and how reliable the text is.

## Non-negotiables

- **Never assume scope.** Read the actual syllabus. A mid-semester syllabus is a subset of the full one: say which units are in each, and flag any unit the student asked for that the exam does not cover. Getting this wrong costs them study hours.
- **Weightage comes from counting real papers, not from guessing.** Count every printed question, including OR alternatives, map each one to a unit, and tabulate marks per unit per paper. Give the official weight from the syllabus as well, and point out where the two disagree.
- **Rank chapters by that count**, and print the rank on every chapter.
- **Flag overdue topics.** A unit with real syllabus weight that scored close to zero in the last two or three papers is more likely to come up, not less. Say so.
- **Monochrome only.** Greys, black and white. No colour anywhere, diagrams included.
- **Diagrams are hand-written inline SVG**, never downloaded images, so they stay monochrome, printable, offline and copyright-clean. Aim for one per substantial topic. Every `<svg>` needs `role="img"`, an `aria-label`, a `viewBox` and, if it uses `marker-end`, its own `<defs><marker>` inside that same `<svg>`. Use the shell's classes (`s-ink`, `s-mute`, `f-soft`, `f-pan`, `f-ink`) instead of literal colours so diagrams follow the dark theme.
- **Pointers, not prose.**

## Every topic gets the same eight blocks

```html
<div class="topic">
  <h3>2.3  Topic name <span class="hits hot">5 papers · 31M</span></h3>
  <div class="blk def" data-l="Definition"><p>The opening lines of an exam answer.</p></div>
  <figure>
    <svg role="img" aria-label="What the diagram shows" viewBox="0 0 640 220">...</svg>
    <figcaption>What to notice in the diagram.</figcaption>
  </figure>
  <div class="blk" data-l="How it works"><ol><li>...</li></ol></div>
  <div class="blk" data-l="Advantages / Disadvantages"><div class="two"><ul>...</ul><ul>...</ul></div></div>
  <div class="blk" data-l="Use cases"><ul><li>Concrete, named, real.</li></ul></div>
  <div class="blk" data-l="Edge cases and gotchas"><ul><li>The traps examiners probe.</li></ul></div>
  <div class="blk" data-l="Example"><p>A worked numerical or a specific instance.</p></div>
  <div class="blk exam" data-l="In the exam"><p>Which papers asked it, for how many marks, how to structure the answer.</p></div>
</div>
```

Tags that can sit in a topic's `<h3>` (the sidebar strips them from its labels):

- `<span class="hits">`: how often it was asked; add `hot` for the most-asked topics.
- `<span class="yr">S23</span>`: one chip per paper; `yr h` for papers that asked it.
- `<span class="paper">W24 Q3(b) 7M</span>`: the exact question that asked it.
- `<span class="oos">not in exam</span>`: outside this exam's scope; the sidebar strikes it through.

## Document skeleton

1. **Intro part**: a `.hero` with a `.kicker` line and the title, then the scope and weightage section: the marks table (per paper, total, share, official weight, in scope or not), two study orders (scope order and raw-weight order), the overdue-topic warning, and a short "how to read each topic" note.
2. **One `<section>` per chapter, in priority order**:
   ```html
   <section id="ch3" data-group="Chapter 3 · 38.7%" data-nav="3. Short name">
     <div class="chead">
       <span class="rank">Priority 1 of 6 · 112 marks · 38.7% · official 30% · in scope</span>
       <h2>Chapter title</h2>
     </div>
     ...topics...
   </section>
   ```
   Split long chapters over several sections so the sidebar stays easy to scan.
3. **Closing plan section**: an ordered study plan with time estimates, answer templates for long and numerical questions, and a two-column self-test.

## Build

Write each part as its own file in a `parts/` folder (`00-intro.html`, `01-ch3.html`, `02-ch1.html`, and so on, in priority order). One large write per chapter means hitting a limit midway loses nothing that was finished. Then:

```
python <this-skill-dir>/scripts/build.py parts --title "Subject Name: Revision Sheet" --short "Subject Name" --code "3174202" -o subject.html
```

The shell (`scripts/shell.html`) supplies the theme toggle, print styles, a back-to-top button, and a two-level sidebar that lists every section and every `.topic`, highlights the one on screen, and pulls a leading `2.3`-style number into its own badge. Number topic headings `N.M  Title` and it all works.

## Verify before saying it is done

```
python <this-skill-dir>/scripts/verify.py subject.html
```

Loop until it reports 0 problems. It always checks the HTML structure and every SVG (a missing marker definition silently deletes arrowheads). With Playwright installed (`pip install playwright`, then `playwright install chromium`) it also loads the page and catches JS errors, broken links, duplicate ids, sidebar gaps, and diagram text that is clipped or overlapping. Without Playwright, tell the student the layout was not checked. Then open the file for them.

## GTU (Gujarat Technological University)

- Full syllabus PDFs: `https://s3-ap-southeast-1.amazonaws.com/gtusitecirculars/Syallbus/<subject code>.pdf` (the misspelling is in the real URL). Send a browser User-Agent; `syllabus.gtu.ac.in` refuses plain scripts.
- Papers are named by session: `S24` is Summer 2024, `W24` is Winter 2024. Use these in `.yr` and `.paper` tags.
- Questions are typically worth 3, 4 or 7 marks, and most come with an OR alternative. Count both sides of every OR.
