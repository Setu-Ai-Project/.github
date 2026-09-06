# SetuAI — Gamified AI Learning App

> Turning the SetuAI curriculum ("A Field Guide to Building With Artificial Intelligence") into an app kids actually *want* to open — not a digital textbook.

## What is this project?

SetuAI is a mobile/web app that teaches kids about AI through **7 game-like levels**, one for each module of the SetuAI curriculum. Instead of reading worksheets, kids play mini-games, make choices in short story scenarios, and build small real projects — while a shared progress bar tracks how far they've come across the whole app.

The core idea is simple: **we are not writing new content.** The curriculum already has "app-shaped bones" — things like Builder Challenges, case studies, and a Mission Progress system. Our job is to turn that existing content into interactive mechanics (swipe games, drag-and-drop, branching stories, sandboxes) instead of building everything from scratch.

## Meet the Mascots

Four mascots already exist in the print curriculum. In the app, each one gets a clear job to do:

| Mascot | Job in the book | Job in the app |
|---|---|---|
| **Byte** | Shares facts & data | Narrates stat call-outs, unlocks "fact cards" |
| **Nova** | Runs Builder Challenges | The "quest giver" who kicks off every challenge |
| **Bug** | Flags mistakes | Pops up as a warning/hint character mid-activity ("Bug Says") |
| **Spark** | Explains definitions | Delivers simple-to-precise definitions as swipeable cards |

## The 7 Levels

Each level maps to one curriculum module and needs **real depth** — several rounds or questions, not a single tap-and-done screen.

### Level 1 — What Is AI?
- Swipe game: sort real-world examples into "AI," "Not AI," and "AGI hype myth" (**10–15 rounds**)
- Timeline mini-section: drag AI history events into the correct order, Byte shares a fact after each correct answer
- Branching case study (DeepMind–NHS): kid makes decisions, then sees what really happened
- Small sandbox: build a biased dataset and see how the output changes

### Level 2 — Prompt Engineering
- **Hallucination Hunt**: kid gets 5 AI answers (mix of real and fake) and flags which ones are made up, then sees an accuracy score and explanation
- **Prompt Lab**: a simple sandbox chatbot where the kid tweaks a prompt to hit a goal (e.g., "get it to write a haiku in 3 tries")
- Branching courtroom-style case study (Mata v. Avianca)

### Level 3 — AI Literacy for Students
- **3–4 scenario questions**: kid picks the AI tool/approach that fits a fake assignment, gets instant feedback and a running score
- Short reflection after each scenario (multiple-choice or one-line answer, not an essay)

### Level 4 — Talking to Machines
- Mock terminal: kid types real commands in a safe, simulated environment (**3–4 commands in sequence**)
- Branching "what would you do differently" scenario based on a real coding incident

### Level 5 — Creative Expression & AI
- **Deepfake quiz**: spot the fake in **8–10 image/video pairs**, with a running score and difficulty that increases as they go
- **"Make It Twice"**: kid creates something on their own, then remixes it with AI, and compares both side-by-side in the app

### Level 6 — AI Entrepreneurship (Flagship Level)
This is our most polished, "show it off" level:
- Simplified MVP chatbot builder
- Full mini **Lean Canvas** — a 12-box drag-and-fill business plan, done by tapping instead of writing
- Optional pitch recording (audio/video) with peer feedback
- This level gets **extra design and QA time** because it's the one we demo to schools and stakeholders

### Level 7 — Future Implications of AI and Education
- **4–5 question AI-readiness quiz**
- Ends with a personalized summary card the kid can download or share — like a certificate for finishing the app

## Shared Features (Across All Levels)

These aren't tied to one level — they connect the whole app together:

- **Progress bar**: shows progress per level, and overall progress across all 7 levels
- **Badges**: one per completed Builder Challenge, grouped loosely by mascot
- **Portfolio page**: collects everything a kid builds — chatbot, Lean Canvas, quiz scores, AI-Readiness card — so progress feels visible, not just points
- **"Bug Says" hints**: contextual tips that appear exactly when needed (e.g., mid-Prompt Lab), not static boxes
- **No traditional grading**: each challenge has its own simple success criteria, and reflections stay short (1–2 taps or a short sentence)

## Backend & Persistence

The backend does **not** need to be heavy. The only real requirement:

- Save a kid's progress across sessions (which levels/rounds are done, scores, badges earned)
- Store portfolio artifacts (chatbot output, Lean Canvas, quiz results, AI-Readiness card)
- Simple enough to run without a large team maintaining it

## Localization Note

The curriculum content is already broken into consistent building blocks — Working Definitions, Learning Objectives, Builder Challenges, Case Studies. This makes translation much easier later on. Recommended approach: structure all content as **JSON, keyed by module → component → language**, from day one, rather than translating flowing paragraphs.

## Build Approach

Instead of building 7 completely different levels, we're building a small **library of reusable mechanics** and reusing them across modules:

- Swipe-sort game
- Drag-and-order timeline
- Branching scenario
- Sandbox chat
- Canvas builder

Once these exist, most levels are variations on the same patterns rather than brand-new builds.

### Suggested Build Order

1. **Module 6 (AI Entrepreneurship)** — pilot first. It's the most "build-first" module already and gives us one complete flagship feature (chatbot + Lean Canvas + pitch) to demo early.
2. **Module 2 (Prompt Engineering)** — Hallucination Hunt and Prompt Lab are quick to build and very replayable.
3. **Module 5 (Creative Expression)** — the Deepfake quiz is another fast, high-engagement win.
4. **Remaining modules** — reuse the mechanics library built above.

## Timeline (8 Weeks)

| Week | Focus |
|---|---|
| 1 | Setup, kickoff, assign 1–2 interns per level |
| 2–4 | Build all 7 levels in parallel |
| 5 | Integrate all levels into one app shell + backend/persistence |
| 6 | Polish pass, with extra focus on Module 6 (flagship level) |
| 7 | Testing and bug fixes |
| 8 | Buffer time + demo prep |

## Getting Started (for Developers)

> Update this section once the tech stack is finalized.

```bash
# Clone the repo
git clone https://github.com/yourorg/setuai-app.git
cd setuai-app

# Install dependencies
[npm install / pip install -r requirements.txt / etc.]

# Run locally
[npm run dev / etc.]
```

**Project structure (placeholder — update once decided):**
```
/levels        → one folder per module (level-1-what-is-ai, level-2-prompt-engineering, ...)
/mechanics     → shared reusable game components (swipe-sort, branching-scenario, etc.)
/backend       → progress + persistence API
/content       → JSON content files, keyed by module → component → language
```

## Contributing

- Each level owner should build against the shared mechanics library where possible, instead of writing one-off code
- Keep content changes in the `/content` JSON files, not hardcoded in components — this keeps translation and edits simple
- Open a pull request with a short description of what changed and which level/mechanic it affects

## Credits

Prepared from the SetuAI Curriculum Overview (First Edition, August 2026). For internal tech planning and development.
