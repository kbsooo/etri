# Learn From Your Own Latents - Notes For ETRI

Paper: `jepa/learnfromyourownlatent.pdf`

Title: "Learn from your own latents and not from tokens: A sample-complexity theory"

Authors: Daniel J. Korchinski, Alessandro Favero, Matthieu Wyart

## Core Claim

The paper studies why methods like data2vec / JEPA can be much more sample-efficient than raw token reconstruction.

In a hierarchical latent generative model, supervised learning or token-level self-supervision needs samples that grow exponentially with latent tree depth. Learning by predicting one's own latent representations can recover the non-root hierarchy with sample complexity roughly `m^3`, independent of hierarchy depth up to logarithmic factors.

The practical message is:

- predicting raw visible tokens dilutes high-level structure;
- predicting learned latent representations amplifies same-level correlations;
- once one latent level is learned, it becomes the context/target for learning the next level;
- a single data2vec-like teacher-student objective can implicitly perform multi-scale latent discovery, so explicit stacked JEPA may be redundant.

## Mechanism

The paper uses the Random Hierarchy Model, a simplified probabilistic context-free grammar.

Visible tokens are leaves. Hidden symbols form a tree. Different low-level tuples can be synonyms when they share the same hidden parent.

The key learning operation is not raw reconstruction. It is:

1. form local tuples;
2. compare their context vectors;
3. cluster tuples that have the same context behavior;
4. treat the cluster id as the next latent level;
5. repeat.

The paper calls the explicit version Iterative Latent Clustering.

Data2vec is argued to perform a soft version of this:

- the teacher target contains latents already learned by the encoder;
- the student predicts the teacher latent from masked context;
- after teacher EMA refresh, newly learned latents enter future targets;
- hierarchy is learned phase by phase without returning to raw-token bottlenecks.

## Important Details

- Same-level latent correlations are stronger than latent-to-token correlations.
- The target must carry already-learned latents.
- The system should cluster context-equivalent structures, not memorize surface tokens.
- Teacher-student / EMA target refresh helps prevent collapse and propagates learned latents upward.
- Explicit H-JEPA-style stacking may be less important than using targets that already contain multi-scale learned latents.

## Translation To This Competition

The visible "tokens" are not words. They are lifelog fragments:

- app usage;
- screen status;
- GPS/mobility;
- ambience/light;
- heart rate;
- pedometer;
- calendar position;
- subject/dateblock context.

The hidden "grammar" is likely human routine state:

- workday commute;
- weekend recovery;
- bedtime phone arousal;
- social overload;
- isolation/media day;
- night-out/mobility;
- payday/month-end stress;
- measurement reliability;
- illness/fatigue;
- routine fragmentation.

The paper argues that we should not try to reconstruct raw logs or directly predict Q/S from every feature. Instead, we should create latent targets that represent hidden routine states and learn to predict those latents from partial context.

## What This Changes After E323 Failure

E323/E324 looked healthy under local row/subject/dateblock null stress but failed public badly.

This paper explains a possible reason:

- E323 learned a latent relative to our local matched-null world;
- but that latent was not the true public hidden state;
- "non-null-common under our controls" is not the same as "same-level latent in the real data-generating hierarchy."

So future JEPA should not only predict local action-health latents. It should predict a latent that separates:

- E247-like public-surviving movement;
- E323-like public-adverse movement;
- human/social routine states;
- target-dependency states.

## Candidate Experiment Direction

Build a data2vec-style / own-latent routine model:

1. Define raw views:
   - phone/app view;
   - mobility view;
   - wearable physiology view;
   - calendar/subject/dateblock view;
   - target-dependency / OOF residual view.

2. Train or construct first-level latents:
   - cluster rows/windows by context-equivalent behavior;
   - use masked feature-family prediction;
   - predict learned latent states rather than raw values.

3. Refresh targets:
   - use learned latent embeddings as targets for the next round;
   - avoid direct raw reconstruction.

4. Add negative anchors:
   - E247-positive/surviving movement;
   - E323-negative/adverse movement;
   - known bad JEPA anchors.

5. Use the latent as a gate, not as a large direct probability move:
   - small E247 corrections only where latent says "public-like and not E323-like";
   - block same-family residuals unless they are orthogonal to E323 movement.

## Practical Rule

The next useful JEPA experiment should be judged by whether it creates a latent that can distinguish E247 from E323 before public LB.

If a latent improves local null stress but cannot separate E247-safe and E323-bad anatomy, it is not a submission latent. It is only a diagnostic latent.
