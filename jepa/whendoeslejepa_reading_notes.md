# When Does LeJEPA Learn a World Model? Reading Notes

Source: `jepa/whendoeslejepa.pdf`

## Core Read

This paper is not saying "LeJEPA always learns the world." It gives a conditional guarantee:

LeJEPA learns a linearly identifiable world model when the hidden latents are approximately Gaussian, the positive-pair transition is stationary with additive noise, and the representation satisfies both alignment and Gaussian/isotropic regularization.

The key object is the composed map `h = f o g`, where `g` is the unknown data generator and `f` is the learned encoder. If the world latent `z` is Gaussian and positive pairs follow an OU-style transition, then the optimum is `h(z) = Qz` for an orthogonal matrix `Q`. In plain terms, the encoder can recover the true latent coordinates up to rotation/reflection.

The most useful mechanism is spectral:

- the transition operator has eigenfunctions ordered by predictability across positive pairs.
- in a Gaussian world those eigenfunctions are Hermite polynomials.
- the linear term has correlation `rho`, while quadratic/cubic/etc. terms have `rho^2`, `rho^3`, etc.
- therefore nonlinear distortions lose alignment correlation.

This is why alignment plus Gaussian/isotropic regularization can force a linear latent, but only under the right world conditions.

## Important Conditions

1. Gaussian latent distribution matters.
   - The paper proves Gaussian is unique for the linear-identifiability guarantee in this class.
   - Non-Gaussian latents can still produce monotonic or slow features, but not guaranteed linear recovery.

2. Positive-pair transition matters.
   - The ideal transition is stationary, additive-noise, and OU-like.
   - If the transition is policy-driven, anisotropic, low-entropy, or non-Gaussian, identifiability degrades.

3. Autocorrelation must be informative, not trivial.
   - If views are almost identical, alignment is too easy and carries little latent information.
   - If views are too far apart, correlation/spectral gap becomes weak.
   - The paper's experiments show an intermediate stride can be best.

4. Gaussianity/isotropy alone is insufficient.
   - Too much regularization can produce a non-informative Gaussian embedding.
   - The alignment gap is the binding constraint in practice; whitening/Gaussianity is usually easier than useful alignment.

5. Latent dimension matters.
   - The theorem assumes embedding dimension equals true latent dimension.
   - If too small, subspace selection/superposition can happen.
   - If too large, extra dimensions can collapse or encode redundancy.

## Implications For This Competition

Our previous JEPA work mostly used the spirit of JEPA: predict hidden block/target/row representations from context and stress whether the latent collapses or shortcuts. This paper sharpens the criteria.

The new question is:

Does a proposed sleep-lifelog latent live in a regime where linear identification is even plausible?

For our data, the answer is probably mixed:

- subject/block/order structure suggests positive-pair transitions exist.
- between-train-runs and row-neighborhood signals suggest stationary-ish local regimes may exist.
- Q/S targets are anisotropic and probably non-Gaussian.
- public LB behavior shows hard-tail cells are not captured by broad body latents.
- E176 failure says a non-collapsed broad body can still be public-misaligned.

So the correct use is not "train a bigger LeJEPA model." The correct use is to audit candidate latents for the LeJEPA conditions before trusting them.

## What Changes In Our Work

### Before

We often asked:

- does this latent improve local LogLoss?
- does it pass blockwise/public-stress checks?
- is it isotropic/non-collapsed?

### After This Paper

We should also ask:

- are the latent marginals close to Gaussian after an appropriate transform?
- are positive-pair increments close to Gaussian?
- is autocorrelation in an intermediate useful range?
- is the transition roughly stationary within the proposed subject/block regime?
- is alignment loss actually informative, or is it trivial because pairs are too similar?
- does isotropy come with alignment, or is it just regularized noise?
- is the candidate dimension plausible, or are we forcing superposition/collapse?

## Direct Next Experiment: E207 LeJEPA Identifiability Conditions Audit

Goal: score existing and new latent candidates by whether they satisfy the conditions under which LeJEPA can identify a world model.

Candidate positive-pair definitions:

- same-subject adjacent rows
- same-subject block-distance `k`
- between-train-runs flank pairs
- nearest-neighbor pairs in raw feature space
- row-window pairs
- target-manifold neighbor pairs using train only

Diagnostics:

- marginal Gaussianity of latent coordinates via random projections
- increment Gaussianity for positive-pair differences
- autocorrelation `rho` by coordinate and pair type
- anisotropy of `rho` across Q/S/body axes
- approximate whitening error
- alignment gap proxy
- rank/effective dimension
- nearest-neighbor target consistency
- public-anchor boundary consistency, especially E95/E101/E176

Decision rule:

- If a latent has good local score but fails Gaussianity/increment/autocorrelation diagnostics, treat it as an energy or warning, not a submission generator.
- If a latent has intermediate autocorrelation, near-Gaussian increments, stable rank, and boundary consistency, it is a legitimate JEPA-style representation candidate.
- If the best regime appears only at one stride/window, build candidates only from that regime and reject all-scale averaging.

## Immediate Read On Current Frontier

E95 remains the real public success: hard-tail localization, not broad world-model recovery.

E176 is now more informative after failure:

- its broad body was non-collapsed,
- but it did not satisfy the public frontier hard-label alignment needed for expected-score improvement.

Under this paper's lens, E176 likely had a representation with visible body structure but poor linear identifiability for the public-decisive latent. The next useful JEPA work should search for the positive-pair regime where hard-tail decisive cells become predictable, not keep expanding broad body movement.

## Practical Takeaway

LeJEPA is useful here as a testable identifiability framework:

1. choose a candidate hidden world state,
2. choose positive pairs that should preserve that state,
3. check Gaussianity/increment/autocorrelation/alignment,
4. only then translate the latent into probabilities.

If step 3 fails, the latent is not dead, but it is not a world model. It is a diagnostic feature or failure-mode energy.
