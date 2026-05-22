# Evaluation analysis

Source: `evaluate_results.json`

**Questions:** 13 | **explain:** 11 | **stylised:** 2

## How to use this report

- Flags are automatic hints, not final grades.
- Open `evaluate_results.json` for full passages and responses.
- Score each run 1–5 on: correctness, grounding, retrieval_relevance, usefulness, style (stylised only), and add comments for failures.

## Explain questions (baseline vs RAG)

### [Q1] Macbeth

**Question:** Why does Macbeth kill Duncan?
**Expected focus:** Macbeth's ambition, the witches' prophecy, Duncan as an obstacle, and Lady Macbeth's pressure. Usefu...

- **Baseline** (32 words): Macbeth kills Duncan because he is driven by ambition and a desire for power. He believes that killing the king will all...
- **RAG** (12 words): Macbeth kills Duncan because he wants to seize the throne for himself.
  - retrieved: Macbeth Act 3 Scene 6; Macbeth Act 1 Scene 6; Macbeth Act 1 Scene 4

### [Q2] Macbeth

**Question:** How does Macbeth change after becoming king?
**Expected focus:** He becomes increasingly fearful, violent, paranoid, and tyrannical; relevant evidence includes Banqu...

- **Baseline** (38 words): Macbeth's transformation is quite dramatic. As he becomes king, his guilt and paranoia grow, leading him to become incre...
- **RAG** (44 words): Macbeth's tyranny develops.  In plain modern English, this means that after becoming king, Macbeth becomes a tyrant and ...
  - retrieved: Macbeth Act 5 Scene 2; Macbeth Act 3 Scene 6; Macbeth Act 1 Scene 3

### [Q3] Hamlet

**Question:** Why does Hamlet delay taking revenge?
**Expected focus:** Uncertainty, moral hesitation, need to test Claudius's guilt, and reflective temperament; use eviden...

- **Baseline** (44 words): Hamlet delays taking revenge because he's struggling with his own moral compass. He's torn between avenging his father's...
- **RAG** (66 words): Hamlet delays taking revenge because he is considering the moral implications of killing Claudius while he is praying. H...
  - retrieved: Hamlet Act 4 Scene 4; Hamlet Act 3 Scene 1; Hamlet Act 3 Scene 3

### [Q4] Hamlet

**Question:** What is Ophelia's role in the tragedy?
**Expected focus:** Ophelia is caught between Hamlet, Polonius, Laertes, and court politics; her distress and death reve...

- **Baseline** (46 words): Ophelia is a tragic heroine and the daughter of Polonius. She plays a significant part in the story, serving as a foil t...
- **RAG** (22 words): Ophelia is... a tragic figure whose descent into madness and death is deeply connected to the chaos and destruction that...
  - retrieved: Hamlet Act 4 Scene 5; Hamlet Act 2 Scene 1; Hamlet Act 1 Scene 3

### [Q5] Romeo and Juliet

**Question:** Why is Juliet conflicted after Romeo kills Tybalt?
**Expected focus:** Juliet loves Romeo but Tybalt is her kinsman; she must reconcile romantic loyalty with family loyalt...

- **Baseline** (47 words): Juliet is conflicted because she loves both her family and Romeo. She's torn between her loyalty to the Capulets and her...
- **RAG** (38 words): Juliet is conflicted because she loves Romeo and feels torn between her love for him and her family loyalty. She knows t...
  - retrieved: Romeo and Juliet Act 3 Scene 1; Romeo and Juliet Act 3 Scene 1; Romeo and Juliet Act 3 Scene 2

### [G1] Hamlet

**Question:** Who is Hamlet?
**Expected focus:** Prince of Denmark, son of the late King Hamlet, nephew of Claudius; central figure seeking revenge.

- **Baseline** (29 words): Hamlet is the main character in one of Shakespeare's most famous plays. He's a prince who seeks revenge for his father's...
- **RAG** (24 words): Hamlet is a prince who has been deeply affected by the death of his father and the marriage of his mother to his uncle.
  - retrieved: Hamlet Act 2 Scene 2; Hamlet Act 2 Scene 2; Hamlet Act 3 Scene 1

### [G2] Macbeth

**Question:** Who is Lady Macbeth and what does she want?
**Expected focus:** Macbeth's wife; ambitious; urges Macbeth to seize the crown after Duncan's murder.

- **Baseline** (28 words): Lady Macbeth is the wife of Macbeth, a Scottish nobleman. She's a strong-willed and ambitious character who wants to hel...
- **RAG** (48 words): Lady Macbeth is the wife of Macbeth, a Scottish noblewoman who has gained power after her husband's ascension to the thr...
  - retrieved: Macbeth Act 3 Scene 2; Macbeth Act 3 Scene 1; Macbeth Act 1 Scene 5
- **Compare:** RAG answer much longer than baseline

### [G3] Romeo and Juliet

**Question:** What is the conflict between the Montagues and the Capulets?
**Expected focus:** Long-standing family feud in Verona causing street violence and pressure on the lovers.

- **Baseline** (34 words): The conflict between the Montagues and the Capulets is a long-standing feud or rivalry. It's a deep-seated hatred that h...
- **RAG** (59 words): The conflict between the Montagues and the Capulets is a feud or an old quarrel that has been going on for some time. It...
  - retrieved: Romeo and Juliet Act 1 Scene 5; Romeo and Juliet Act 1 Scene 1; Romeo and Juliet Act 1 Scene 2
  - flags: `meta-phrasing`
- **Compare:** RAG flags: meta-phrasing; RAG answer much longer than baseline

### [G4] Hamlet

**Question:** What is the ghost and why does it matter?
**Expected focus:** Ghost claims to be Hamlet's father, accuses Claudius of murder, sets revenge plot in motion.

- **Baseline** (62 words): The ghost in Shakespeare's plays often represents a character's conscience or a lingering presence from their past. In m...
- **RAG** (22 words): Hamlet's father's spirit is the ghost. It matters because the ghost reveals that Claudius murdered him and commands Haml...
  - retrieved: Hamlet Act 1 Scene 5; Hamlet Act 1 Scene 4; Hamlet Act 1 Scene 5

### [G5] Macbeth

**Question:** What do the witches tell Macbeth?
**Expected focus:** Prophecies including Thane of Cawdor and future kingship; help spark his ambition.

- **Baseline** (35 words): The witches, also known as the Weird Sisters, prophesize to Macbeth that he will become Thane of Cawdor and eventually K...
- **RAG** (9 words): Macbeth is told that he will be King hereafter.
  - retrieved: Macbeth Act 1 Scene 3; Macbeth Act 1 Scene 3; Macbeth Act 4 Scene 1

### [G8] Romeo and Juliet

**Question:** How does the family feud shape the tragedy?
**Expected focus:** The feud creates violence, secrecy, pressure, miscommunication, and ultimately the conditions for th...

- **Baseline** (52 words): The family feud can create a sense of tension and conflict that drives the plot forward. It can also lead to misundersta...
- **RAG** (39 words): The Capulet-Montague feud is...  A longstanding grudge that ultimately leads to the tragic deaths of Romeo and Juliet. T...
  - retrieved: Romeo and Juliet Act 0 Scene 0; Romeo and Juliet Act 3 Scene 2; Romeo and Juliet Act 5 Scene 3

## Stylised questions (RAG only)

### [G6] Hamlet

**Question:** Speak briefly as Hamlet reflecting on revenge.
- **Words:** 109
- **Response:** [Creative stylised response — not factual evidence]  "Whispers of the wind, echoes of the past, A fire that burns within, a justice to amass. The ghost's words still linger, like autumn's chill, Reven...
- **Has required label:** True

### [G7] Romeo and Juliet

**Question:** Speak briefly as Juliet about love and family duty.
- **Words:** 56
- **Response:** [Creative stylised response — not factual evidence]  "Love's whispered secrets dance upon my lips, As family duty's heavy chains I wear. A delicate balance 'twixt heart and kin, I find myself torn, wi...
- **Has required label:** True

## Flag summary (across all runs)

- `meta-phrasing`: 1

*Use flagged items as starting points for failure analysis in your technical report.*
