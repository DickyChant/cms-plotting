# Physics

What a reader of this analysis's canvases needs to know. Keep it to what changes plotting or reporting
choices; the analysis note holds the rest. Replace every placeholder below.

## Process

- Decay / process: `B+ -> J/psi(-> mu+ mu-) K+` (and charge conjugate)
- Channels / control channels: `<control channel, normalisation channel>`
- Data: `<run, eras, triggers or streams>`; simulation: `<generator, samples>`

## Observables and what their spectra look like

| observable | x label | range, bin width | what is in it |
|---|---|---|---|
| `m_jpsik` | `m(J/psi K+)` | 5.10-5.45 GeV, 0.005 GeV | peak at 5.279 GeV, sigma ~ 13 MeV; partially reconstructed below 5.2; combinatorial |

Write down the features a canvas must show or must not hide: thresholds, reflections from
mis-identified decays, kinematic endpoints, the resolution (bins narrower than about sigma/2 are noise).

## Fits

- Signal model: `<shape, parameters fixed from simulation>`
- Background model: `<shape, how the order is chosen>`
- Weights: `<sWeights / COWs / none, and their known weak points>`

## Blind or sensitive

Quantities that are never fitted or shown unless the user asks (e.g. a charge split, an asymmetry, the
signal region of a search).
