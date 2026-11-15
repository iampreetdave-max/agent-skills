---
name: hackathon-sprint
description: Playbook for building a hackathon project with an AI coding agent in 24 to 72 hours, aimed at winning. Picking the problem and category, mining open source and research papers first, scoping to one flawless demo path, building fast, deploying to a real URL, a sleek deck, and a rehearsed three-minute demo. Use when the user is entering or building for a hackathon, buildathon, demo day or any similar time-boxed competition.
---

# Hackathon sprint

A hackathon is not a production project. The goal is a convincing, working demo of a strong idea by the deadline, presented with confidence.

## How the agent behaves here

- **No multi-week estimates.** The job is to fit the idea into the hours available. Cut scope to the demo path and build that today. If a part truly cannot fit, say which part to fake or drop, never "this will take three weeks".
- **Vibe code hard.** Speed beats code polish. The polish goes into the demo and the deck.
- **Make it work somehow.** It doesn't have to run on all the real data or be 100% correct. It has to work end to end on the demo path.
- **Never assume anything about the rules.** Read them.

## 1. Pick the problem

- Read the problem statements, the judging criteria and the rules (team size, what counts as prior work, required submissions) before choosing.
- Pick something you understand well enough to explain. You don't have to understand all of it.
- **Consider the hardest or least popular category.** Judges usually pick a winner per category, and a hard track has fewer strong entries.
- Write the one-line pitch before any code: who has the problem, what they do today, and what your demo shows.

## 2. Open source first

Whatever you are about to build, part of it almost certainly exists already: on GitHub, on some website, in a research paper. You don't have time to redo that work.

- Search GitHub, Hugging Face, arXiv (papers often link their code) and the problem's own domain for existing tools, models and datasets.
- Have the agent read the best two or three papers and repos, and summarise what they did and what can be reused.
- Build on top of them and make your own contribution the visible part.
- Check licences and the hackathon's rules on prior and third-party code, and credit what you used in the README and the deck.

## 3. Scope to one demo path

- List the features, then circle the ones the three-minute demo shows. Everything else is cut or faked.
- Map each demo step to a judging criterion: innovation, impact, technical depth, feasibility, presentation.
- Use seed data or a small real sample. Put slow or paid parts behind a flag with a mocked response. Precompute heavy results.
- Fix the demo inputs in advance, so the live demo never meets a surprise.

## 4. Build

- A rough split of the hours: idea and research 10%, core demo path working (ugly is fine) 40%, make it look good 20%, deploy 10%, deck and rehearsal 20%.
- Commit often. Keep a `HANDOFF.md` up to date (what works, what is faked, how to run it, what is next) so a teammate or a fresh agent session can pick up instantly.
- At the halfway mark, if the core path doesn't work yet, cut features until it does.

## 5. Deploy it for real

- A live URL beats localhost every time. Use whatever is fastest for the stack: Netlify, Cloudflare Pages, Vercel, Hugging Face Spaces, Render, any VPS.
- A custom domain looks professional and costs little.
- Make it feel real: realistic data, a clean first screen, no lorem ipsum, no console errors.

## 6. Demo and deck

- **The demo must be flawless.** Rehearse it at least three times on the actual laptop and network. Keep a backup: a recorded video of the demo and screenshots in the deck, for when the wifi or an API dies.
- **Three-minute script:** the problem (20 s), who it hurts (15 s), live demo (90 s), how it works (30 s), impact and what's next (25 s).
- **The deck has to be sleek:** one idea per slide, big type, real screenshots, one architecture diagram, numbers if you have them. Everyone uses AI to make slides, so put in the time to make yours the best-looking in the room.
- Speak with confidence, and prepare answers for: what is real and what is mocked, what data you used, how it scales, and what you'd build next.
- **Be honest when asked.** Say what is mocked. Never claim results or users you don't have; judges check.

## 7. Submission checklist

- [ ] Repo public (or as the rules require), with a README: screenshots, how to run it, credits
- [ ] Live URL works on a phone over mobile data
- [ ] Demo video uploaded
- [ ] Deck exported to PDF
- [ ] Team names and track correct on the form
- [ ] Submitted before the deadline, with time to spare
