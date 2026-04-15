---
name: transcript-diarize
description: Label each chunk of a Whisper ASR transcript with a 1-indexed speaker id using surrounding context (role cues, names, conversational structure). Use when a caller passes a numbered list of transcript chunks and asks for strict-JSON speaker assignments — typically driven by the `polyphony` CLI's local-ensemble backend.
license: MIT
metadata:
  version: 0.1.0
---

# transcript-diarize

Assign a speaker id to each chunk of a Whisper ASR transcript using *text-side* signals — role cues, names, conversational structure — so your output can be reconciled with an audio-side diarizer (pyannote) for ensemble accuracy.

This skill is the text-side leg of the `polyphony` local-ensemble backend. It's invoked when `polyphony --backend local` shells out to `claude -p` with a numbered chunk list.

---

## Inputs

The caller's prompt will include:

- A speaker block — either named (`Speaker 1 = Josh`, `Speaker 2 = Neville`) or unnamed
- A numbered list of chunks: `[0] So tell me about your background... [1] Sure, I started in...`
- An optional context hint (e.g. "software engineering interview")

## Output

Emit a single strict JSON array, one object per chunk, in the same order:

```json
[{"id": 0, "speaker": 1}, {"id": 1, "speaker": 2}, {"id": 2, "speaker": 1}]
```

Rules:

- Exactly one entry per chunk id. No skipping.
- Speaker is a positive 1-indexed integer.
- Output **only** the JSON. No preamble, no commentary, no markdown fences.
- If you're genuinely uncertain on a chunk, still pick the most plausible speaker — the polyphony reconciler will see the disagreement with pyannote and flag it for human review with a confidence score.

---

## Heuristics

Apply these in priority order:

1. **Names mentioned in the text** are the strongest signal. "So, Neville, what's your take on…" → next chunk is almost certainly Neville responding.
2. **Question/answer cadence.** Interviewers ask, interviewees answer. Long expository turns are rarely the interviewer.
3. **Short interjections** ("yeah", "right", "mm-hm", "exactly") are usually reactions — typically the *opposite* speaker of the previous long turn.
4. **Topic continuity.** If a long turn ends mid-thought and the next chunk continues the thought, it's almost always the same speaker.
5. **Role cues.** "Let me show you the dashboard" suggests the demo-er; "Got it" suggests the receiver.

---

## Common failure modes

- Don't introduce a third speaker just because a chunk feels different. Stick to the speaker count implied by the speaker block.
- Don't omit chunks. The caller's parser expects exact alignment — missing entries get heuristically backfilled with low confidence.
- Don't summarize. The caller already has the chunk text; you owe them a label, nothing more.
- Don't second-guess the speaker block. If you're told "Speaker 1 = Sam, Speaker 2 = Daniel," use those ids; don't invent new ones.
