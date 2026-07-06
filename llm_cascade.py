"""
LLM cascade data extraction — per-token surprisal, residual-stream norms,
attention entropy — and three point-process projections of those signals.

Pipelines a text through a causal LM, captures internal cascade signals,
then converts them to point-process event sequences suitable for the ARS
arithmetic_toolkit.

Methods (Engine 1 of arithmetic_toolkit's full_analysis is the consumer):

  surprisal_threshold     : events at integer token positions where
                             per-token surprisal exceeds median + k*std.
                             Integer event times → spacing artefacts at
                             low N; fine for fingerprinting via Fano
                             and pair-correlation but suboptimal for NNS.

  surprisal_cumulative    : event "time" axis = cumulative surprisal
                             (information content used as natural time).
                             High-surprise tokens are stretched apart;
                             low-surprise tokens are compressed close
                             together.  Naturally continuous, sidesteps
                             integer-spacing.  RECOMMENDED.

  residual_norm_peaks     : events at peaks of the final-layer residual
                             stream L2 norm.  Detects representational
                             salience rather than predictability.

Public functions
----------------
extract_cascade(text, model_name=…, quantization=…)
    Tokenise → forward pass → return dict with surprisal, hidden_norms,
    attn_entropy.

get_event_times(cascade, method=…, **kwargs)
    Project a cascade into a numpy array of event times.

run_full_analysis_on_cascade(cascade, method=…, **kwargs)
    Convenience: convert + analyse in one call, returns the toolkit's
    fingerprint dict plus the extraction parameters.
"""
from __future__ import annotations
import os
from typing import Optional

import numpy as np


def extract_cascade(text: str,
                    model_name: str = "Qwen/Qwen2.5-3B",
                    quantization: Optional[str] = None,
                    max_seq_len: int = 4096,
                    device: str = "cuda",
                    keep_attention: bool = False,
                    compute_attention: bool = True,
                    preloaded_model=None,
                    preloaded_tokenizer=None) -> dict:
    """Forward `text` through a causal LM, return cascade signals.

    quantization: None | "int8" | "int4".
    keep_attention: store the per-layer per-head attention matrices.
        Off by default — output_attentions=True scales O(L·H·T²) and
        explodes memory at long T.  Attention entropy is computed
        before discard, so the summary signal is preserved.
    compute_attention: when False, skip output_attentions=True on the
        forward pass (saves ~L·H·T²·dtype bytes — ~5 GB for Qwen 2.5 3B
        at T=2048).  Use when only surprisal + hidden_norms are needed
        downstream.  Sets attn_entropy to a zero stub.
    preloaded_model / preloaded_tokenizer: optional already-loaded
        pair to reuse (avoids the OOM caused by holding two copies of
        a multi-GB model on a single GPU).  When provided, this
        function does NOT free them on exit — caller owns lifecycle.
    """
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

    owns_model = preloaded_model is None
    if preloaded_tokenizer is not None:
        tokenizer = preloaded_tokenizer
    else:
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    if preloaded_model is not None:
        model = preloaded_model
    else:
        load_kwargs = dict(
            torch_dtype=torch.float16,
            device_map=device,
            trust_remote_code=True,
            attn_implementation="eager",   # required for output_attentions
        )
        if quantization == "int8":
            load_kwargs["quantization_config"] = BitsAndBytesConfig(load_in_8bit=True)
            load_kwargs.pop("torch_dtype")
        elif quantization == "int4":
            load_kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
            )
            load_kwargs.pop("torch_dtype")
        model = AutoModelForCausalLM.from_pretrained(model_name, **load_kwargs)
    model.eval()
    model_dev = next(model.parameters()).device

    inputs = tokenizer(text, return_tensors="pt", truncation=True,
                        max_length=max_seq_len).to(model_dev)
    ids = inputs["input_ids"]

    with torch.no_grad():
        out = model(
            ids,
            output_attentions=compute_attention,
            output_hidden_states=True,
        )

    # Per-token surprisal in nats
    logits = out.logits[0, :-1].float()              # [T-1, vocab]
    targets = ids[0, 1:]                              # [T-1]
    log_probs = torch.log_softmax(logits, dim=-1)
    surprisal = -log_probs[torch.arange(targets.size(0), device=model_dev),
                            targets].cpu().numpy()
    log_probs = None  # free

    tokens = tokenizer.convert_ids_to_tokens(ids[0])

    # Per-layer residual-stream L2 norm (length [n_layers, T])
    hidden_norms = np.stack([
        h[0].norm(dim=-1).float().cpu().numpy()
        for h in out.hidden_states
    ])

    # Attention entropy per (layer, head, query_token).
    # a is [batch=1, heads, T, T]; for each query t, entropy of attention
    # distribution over keys.  Skipped when compute_attention=False.
    if compute_attention and out.attentions is not None:
        attn_entropy = np.stack([
            -(a[0].float() * (a[0].float() + 1e-12).log()).sum(-1).cpu().numpy()
            for a in out.attentions
        ])  # [n_layers, n_heads, T]
    else:
        attn_entropy = np.zeros((0, 0, ids.shape[1]), dtype=np.float64)

    result = dict(
        surprisal=surprisal,
        tokens=tokens[1:],
        hidden_norms=hidden_norms,
        attn_entropy=attn_entropy,
        model_name=model_name,
        quantization=quantization,
        seq_len=int(ids.shape[1]),
    )
    if keep_attention:
        result["attentions"] = [a[0].float().cpu().numpy() for a in out.attentions]

    # Free per-call buffers; only delete the model+tokenizer if WE loaded them.
    del out, ids, inputs, logits, targets
    if owns_model:
        del model, tokenizer
    if device == "cuda":
        torch.cuda.empty_cache()
    return result


def get_event_times(cascade: dict,
                    method: str = "surprisal_cumulative",
                    **kwargs) -> np.ndarray:
    """Project a cascade dict to a sorted numpy array of event times."""
    s = np.asarray(cascade["surprisal"], dtype=np.float64)
    if method == "surprisal_threshold":
        k = float(kwargs.get("k", 1.5))
        thr = np.median(s) + k * np.std(s)
        events = np.where(s > thr)[0].astype(np.float64)
    elif method == "surprisal_cumulative":
        from scipy.signal import find_peaks
        prom = float(kwargs.get("prom", 0.5))
        peaks, _ = find_peaks(s, prominence=prom)
        if peaks.size < 5:
            peaks, _ = find_peaks(s, prominence=max(prom * 0.3, 0.05))
        cum = np.cumsum(s)
        events = cum[peaks]
    elif method == "residual_norm_peaks":
        from scipy.signal import find_peaks
        prom = float(kwargs.get("prom", 0.3))
        norms = np.asarray(cascade["hidden_norms"], dtype=np.float64)[-1, 1:]
        peaks, _ = find_peaks(norms, prominence=prom)
        if peaks.size < 5:
            peaks, _ = find_peaks(norms, prominence=max(prom * 0.3, 0.05))
        events = peaks.astype(np.float64)
    else:
        raise ValueError(f"unknown method: {method!r}")
    return np.sort(events)


def run_full_analysis_on_cascade(cascade: dict,
                                  method: str = "surprisal_cumulative",
                                  q_max: int = 8,
                                  ramanujan_q_max: int = 200,
                                  **kw) -> dict:
    """Apply arithmetic_toolkit.full_analysis to events extracted from a
    cascade.  Returns the toolkit dict plus extraction parameters and
    a few cascade-level scalars."""
    from arithmetic_toolkit import full_analysis

    events = get_event_times(cascade, method=method, **kw)
    if events.size < 20:
        return dict(error=f"insufficient events ({events.size}) at method={method}",
                    method=method, n_events=int(events.size))
    res = full_analysis(events, label=f"{cascade.get('model_name','?')}|"
                                           f"{cascade.get('quantization','fp16')}|"
                                           f"{method}",
                         q_max=q_max,
                         ramanujan_q_max=ramanujan_q_max)
    res["extraction_method"] = method
    res["model_name"] = cascade.get("model_name")
    res["quantization"] = cascade.get("quantization")
    res["seq_len"] = cascade.get("seq_len")
    res["mean_surprisal"] = float(np.mean(cascade["surprisal"]))
    res["std_surprisal"] = float(np.std(cascade["surprisal"]))
    return res


# ─── Embedded stimulus texts ──────────────────────────────────────────────────

STRUCTURED_TEXT = """
Theorem.  For every prime p, there exist integers x and y with x² + y² ≡ -1 (mod p).
Proof.  Consider the sets A = {x² mod p : x ∈ {0, 1, …, (p-1)/2}} and B = {-1 - y² mod p : y ∈ {0, 1, …, (p-1)/2}}.
Each set has exactly (p+1)/2 elements, since x ↦ x² is two-to-one except at zero, and similarly for y ↦ -1 - y².
By the pigeonhole principle, A and B together have p + 1 elements but live in Z/pZ which has only p elements.
Therefore A and B intersect, giving an element c ∈ A ∩ B.  Hence c = x² and c = -1 - y² for some x and y.
Equating, x² = -1 - y², so x² + y² ≡ -1 (mod p).  ∎

Theorem.  Every positive integer is the sum of four squares.
Proof.  By the multiplicativity identity, it suffices to prove the result for primes.  For p = 2 we have 2 = 1² + 1² + 0² + 0².
For odd p, by the previous theorem there exist x, y with x² + y² + 1 ≡ 0 (mod p).
Then m = (x² + y² + 1) / p is a positive integer with x² + y² + 1² + 0² = mp.
Choose the smallest m for which mp is a sum of four squares.  We claim m = 1.
Suppose m > 1.  Reducing each variable modulo m to land in (-m/2, m/2], call the new variables a, b, c, d.
Then a² + b² + c² + d² ≡ 0 (mod m), so a² + b² + c² + d² = m'm for some non-negative m'.
Also m'm < 4(m/2)² = m², so m' < m.  By Euler's identity, the product of two sums of four squares is a sum of four squares.
Therefore (m'm)(mp) = (sum of four squares), and the squared common factor m² divides each term, yielding m'p as a sum of four squares.
This contradicts the minimality of m unless m' = 0, but m' = 0 forces a = b = c = d = 0, i.e. each of x, y, 1, 0 ≡ 0 (mod m).
The condition 1 ≡ 0 (mod m) gives m = 1.  ∎
""".strip()


NATURAL_TEXT = """
The discovery of the Higgs boson in 2012 at the Large Hadron Collider was the culmination of nearly fifty years of theoretical and experimental work.  Peter Higgs and François Englert had independently proposed the mechanism in 1964, suggesting that an invisible field permeating all of space could give mass to fundamental particles.  Two giant detectors at CERN, ATLAS and CMS, gathered evidence by colliding protons at energies near 8 trillion electron volts, sifting through trillions of collisions to identify the rare events that produced a fleeting Higgs particle.  The mass of the Higgs, around 125 gigaelectron volts, has since been measured with increasing precision, and its decay channels have been studied to test the Standard Model of particle physics.

Subsequent runs at the LHC have searched for hints of new physics beyond the Standard Model.  Supersymmetric partners of known particles, predicted by theories that aim to stabilise the Higgs mass, have not been found in the energy range explored so far.  Dark matter candidates, gravitons, leptoquarks, and additional Higgs bosons remain elusive, suggesting that whatever lies beyond the Standard Model — if anything — is either too heavy to produce at current energies or too weakly coupled to detect.  Plans for the High-Luminosity LHC and successor colliders aim to extend the reach by orders of magnitude, in the hope of clarifying questions about neutrino masses, the matter-antimatter asymmetry, and the nature of dark matter.

Meanwhile, gravitational-wave astronomy entered its observational era with LIGO's detection of merging black holes in 2015.  Since then, dozens of binary black hole and neutron star mergers have been catalogued, providing a new window onto the universe.  The merger of two neutron stars in 2017 was observed simultaneously in gravitational waves and across the electromagnetic spectrum, marking the beginning of multi-messenger astronomy.
""".strip()


def _random_text(n_words: int = 350, seed: int = 7) -> str:
    """Random word sequence drawn from a fixed lexicon — high entropy
    relative to a language model."""
    lex = (
        "apple bridge canyon delta echo fragment glade horizon "
        "iguana junction kestrel lattice meridian nebula octave plume "
        "quartet ridge sapphire trellis umbrella vortex wisteria xenon "
        "yarrow zenith arc beacon catalyst draft ember firmament gale "
        "halo isotope joist knell lobe morass nexus orbit prism quill "
        "rune satchel timbre understory veneer waft xylophone yam zircon "
        "axiom borough cipher dial easel furrow gyre helm ingot jasper "
        "kelp lyre mosaic notch obelisk parapet quasar rampart sextant "
        "thicket undulate vellum wraith xeric yodel zephyr"
    ).split()
    rng = np.random.default_rng(seed)
    sample = rng.choice(lex, size=n_words, replace=True)
    out = []
    for i, w in enumerate(sample):
        out.append(w)
        if (i + 1) % 14 == 0:
            out.append('.')
    return ' '.join(out).replace(' .', '.')


RANDOM_TEXT = _random_text()


def get_default_texts() -> dict[str, str]:
    return {
        "structured": STRUCTURED_TEXT,
        "natural":    NATURAL_TEXT,
        "random":     RANDOM_TEXT,
    }


__all__ = [
    "extract_cascade", "get_event_times", "run_full_analysis_on_cascade",
    "STRUCTURED_TEXT", "NATURAL_TEXT", "RANDOM_TEXT", "get_default_texts",
]
