# Less-AI-tone report: ai-sample.md → ai-sample-revised.md

427 → 323 words · 10 paragraph(s) changed

## 1. Metrics before and after

| Level | Rule | Before (hits, /1k words) | After | Change |
|---|---|---|---|---|
| A | R1 Not-X-but-Y reframe | 3 (7.026) | 0 (0.0) | ↓ better |
| A | R2 Announcement colon | 2 (4.684) | 0 (0.0) | ↓ better |
| A | R3 Throat-clearing phrase | 3 (7.026) | 0 (0.0) | ↓ better |
| A | R4 Paragraph-opening signpost | 2 (4.684) | 0 (0.0) | ↓ better |
| A | R5 Chatbot residue | 1 (2.342) | 0 (0.0) | ↓ better |
| B | R6 Inflated vocabulary | 23 (53.864) | 1 (3.096) | ↓ better |
| B | R7 Trailing -ing clause | 2 (4.684) | 0 (0.0) | ↓ better |
| B | R8 Significance inflation | 4 (9.368) | 0 (0.0) | ↓ better |
| B | R9 Stacked triad | 3 (7.026) | 5 (15.48) | ↑ worse |
| B | R10 Hedge stacking | 1 (2.342) | 0 (0.0) | ↓ better |
| H | R11 Personified tool / grand metaphor | 3 (7.026) | 3 (9.288) | = |
| F | Em dash | 2 (4.684) | 0 (0.0) | ↓ better |

| Structure (report only; no target value) | Before | After |
|---|---|---|
| sentence_len_cv | 0.447 | 0.443 |
| mean_sentence_words | 13.3 | 12.0 |
| section_len_cv | 0.383 | 0.447 |
| headings_per_1k | 11.71 | 15.48 |
| list_line_share | 0.0 | 0.0 |
| iso2_per_100p | 18.18 | 0.0 |
| iso3_per_100p | 9.09 | 0.0 |
| mtld | 150 | 169 |
| nominalizations_per_1k | 42.2 | 40.2 |

Do-not-touch (X) counts should be unchanged. A change means an X item was rewritten or a sentence holding one was removed; check it was deliberate:

- X1 Numbered headings (do not touch): 4 → 4
- X2 'This means' restatement (do not touch): 0 → 0
- X3 Passive voice (do not touch): 1 → 0  ⚠ changed, check
- X4 Questions in prose (do not touch): 0 → 0

## 2. Semantic layer

- Elegant variation: 1.00 per paragraph; 0% of paragraphs with ≥2 (report threshold borrowed from the Chinese study: ≥0.7 per paragraph or >15% heavy)
- Cohesion chain: longest run of clear continuations = 7 (flag at ≥6); connectives without a real relation: 0
- Colons: 2 conclusion-announcement of 2 prose colons
- Isomorphic triples: 1 fully isomorphic of 1 candidates (flag at ≥2)

## 3. Revised text with changes marked

<del>struck</del> = removed original, <ins>underlined</ins> = new wording.

# Why Small Teams Win at Product Design

<del>In today's fast-paced digital landscape, product</del><ins>Product</ins> teams face <del>a myriad of</del><ins>many</ins> challenges. <del>It's worth noting that the</del><ins>The</ins> most successful products rarely come from the largest teams. <del>Let's dive in.</del>

## 1. Speed Is Not About Effort

Speed <del>isn't</del><ins>comes</ins> <del>about working longer hours — it's about</del><ins>from</ins> removing the steps that slow decisions down. A small team can ship a feature, gather feedback, and iterate within a single <del>week,</del><ins>week.</ins> <del>highlighting the power of tight feedback loops. Moreover, small</del><ins>Small</ins> teams <del>foster</del><ins>also build</ins> a culture of ownership that larger organizations struggle to replicate.

<del>The bottom line: fewer</del><ins>Fewer</ins> people means fewer handoffs. Each handoff introduces <del>delay.</del><ins>delay,</ins> <del>Each</del><ins>and every</ins> delay <del>introduces cost. Each</del><ins>adds</ins> cost <del>introduces</del><ins>and</ins> risk.

## 2. Communication Becomes Seamless

Communication <del>serves as</del><ins>is</ins> the backbone of any successful team. When five people share a room, information flows <del>seamlessly,</del><ins>easily</ins> <del>ensuring that</del><ins>and</ins> everyone stays aligned. <del>Furthermore,</del><ins>Without</ins> <del>the absence of layers allows</del><ins>layers,</ins> the team <del>to</del><ins>can</ins> <del>leverage</del><ins>use</ins> its collective <del>expertise in a holistic way.</del><ins>expertise.</ins>

<del>This</del><ins>Trust</ins> <del>approach</del><ins>matters</ins> <del>underscores the importance of trust.</del><ins>here.</ins> A <del>robust</del><ins>strong</ins> culture of trust <del>empowers</del><ins>lets</ins> designers <del>to</del> take risks, <del>enables</del> engineers <del>to</del> challenge assumptions, and <del>allows</del> product managers <del>to</del> focus on what truly matters. <del>It is not just a process — it is a mindset.</del>

Think of the design lead like a trusted navigator, guiding the ship through uncharted waters. The team's rhythm becomes a symphony of ideas, each voice contributing to a richer tapestry of solutions.

## 3. Ownership Drives Quality

Ownership <del>plays a crucial role in</del><ins>affects</ins> product quality. When a single designer owns a flow from start to finish, they notice the <del>intricate</del><ins>small</ins> details that a committee might miss. <del>Additionally,</del><ins>Owners</ins> <del>owners</del><ins>also</ins> care about outcomes, not just outputs, which may <del>potentially</del> lead to better long-term decisions.

The data tells a compelling story. In one study, teams of fewer than eight people shipped features 40% faster than larger teams. They made fewer errors, they reported higher satisfaction, and they retained talent longer. <del>This is a testament to the pivotal role that team</del><ins>Team</ins> size <del>plays</del><ins>matters</ins> <del>in</del><ins>to</ins> delivering value.

<del>Ultimately, small</del><ins>Small</ins> teams are <del>not merely a cost-saving measure, but</del> a strategic advantage <del>that empowers organizations to navigate the complexities of</del><ins>in</ins> modern product <del>development.</del><ins>development, as well as a way to save costs.</ins>

## 4. How to Get Started

<del>Here's the thing: you</del><ins>You</ins> don't need to reorganize your entire company overnight. Start with one pilot team, give it clear ownership of a single product area, and measure the results over a quarter. <del>Embark on this journey</del><ins>Start</ins> with an open mind, and you may <del>unlock a</del><ins>find</ins> new <del>level of</del> creativity, efficiency, and impact.

<del>In conclusion, small</del><ins>Small</ins> teams <del>represent</del><ins>change</ins> <del>a</del><ins>how</ins> <del>transformative</del><ins>products</ins> <del>approach</del><ins>get</ins> <del>to product design.</del><ins>designed.</ins> By <del>embracing</del><ins>giving teams</ins> autonomy, <del>fostering</del><ins>building</ins> trust, and <del>streamlining</del><ins>simplifying</ins> communication, organizations can <del>elevate</del><ins>improve</ins> their products and <del>empower</del> their <del>people.</del><ins>people's</ins> <del>I hope this helps you rethink how your teams are structured!</del><ins>work.</ins>
