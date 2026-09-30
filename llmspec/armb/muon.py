"""Hybrid Muon + AdamW optimizer for Arm B M0 (ARMB_PREREG.md B1a-A4 §4, Will's confirmed spec 09-27).

Every line traces to pinned source, not memory:
  NS5 = KellerJordan/Muon@f98f1cacc0263b04290753e32be8d498c1efc806 muon.py zeropower_via_newtonschulz5
        (coefficients 3.4445, -4.7750, 2.0315; X / (||X||_F + 1e-7); transpose when rows > cols; 5 steps; bf16 in the
        reference -- `ns_dtype` selects bf16 or fp32 per the sealed update test)
  momentum / Nesterov / weight decay / LR rule = MoonshotAI/Moonlight@c2ad5b20c605086526a179d36901bfc41b52b44b
        examples/toy_train.py:  buf = mu*buf + g;  g = g + mu*buf (nesterov);  u = NS5(g);
        p *= (1 - lr*wd);  p -= lr * 0.2*sqrt(max(A, B)) * u
Muon params (2-D hidden matrices only): Q, K, V split from the fused attention.query_key_value.weight (rows ordered
(head, qkv, d_head): reshape(H, 3, DH, D), each piece (H*DH) x D = 512 x 512, orthogonalised SEPARATELY and scaled by its
own shape), attention.dense, mlp.dense_h_to_4h, mlp.dense_4h_to_h. AdamW (the AdamW arms' exact config and GPT-NeoX
decay groups: no decay on LayerNorm params or biases) on everything else: embed_in, embed_out, LayerNorms, all biases.
Momentum buffers are fp32. Gradients arrive already unscaled, overflow-checked and clipped (the trainer does that
before calling step(), exactly as for the AdamW arms).
"""
import math
import torch

MUON_VERSION = "muon-hybrid-v1 (KellerJordan/Muon@f98f1ca NS5; Moonlight@c2ad5b2 momentum+wd+0.2*sqrt(max(A,B)))"
MUON_SUFFIXES = ("attention.query_key_value.weight", "attention.dense.weight", "mlp.dense_h_to_4h.weight", "mlp.dense_4h_to_h.weight")


def ns5(G, steps=5, dtype=torch.bfloat16):
    a, b, c = (3.4445, -4.7750, 2.0315)
    X = G.to(dtype)
    tr = G.size(0) > G.size(1)
    if tr:
        X = X.T
    X = X / (X.norm() + 1e-7)
    for _ in range(steps):
        A = X @ X.T
        B = b * A + c * A @ A
        X = a * X + B @ X
    if tr:
        X = X.T
    return X


class MuonHybrid:
    def __init__(self, model, H, DH, momentum=0.95, weight_decay=0.1, ns_steps=5, ns_dtype=torch.bfloat16,
                 adam_betas=(0.9, 0.95), adam_eps=1e-8, split_qkv=True):
        self.H, self.DH, self.mu, self.wd, self.ns_steps, self.ns_dtype, self.split_qkv = H, DH, momentum, weight_decay, ns_steps, ns_dtype, split_qkv
        self.muon = [(n, p) for n, p in model.named_parameters() if n.endswith(MUON_SUFFIXES)]
        muon_ids = {id(p) for _, p in self.muon}
        decay, no = [], []
        for mod in model.modules():
            for n, p in mod._parameters.items():
                if p is None or id(p) in muon_ids:
                    continue
                (no if isinstance(mod, torch.nn.LayerNorm) or n == "bias" else decay).append(p)
        self.adam = torch.optim.AdamW([{"params": decay, "weight_decay": weight_decay}, {"params": no, "weight_decay": 0.0}],
                                      lr=0.0, betas=adam_betas, eps=adam_eps, fused=True)
        self.buf = {}                                                       # fp32 momentum buffers

    def _pieces(self, n, g):
        """Yield (key, view_of_grad_piece, setter) for each matrix Muon orthogonalises separately."""
        if n.endswith("attention.query_key_value.weight") and self.split_qkv:
            D = g.size(1); gv = g.view(self.H, 3, self.DH, D)
            for j in range(3):
                yield (n, j), gv[:, j].reshape(self.H * self.DH, D), j
        else:
            yield (n, None), g, None

    @torch.no_grad()
    def step(self, lr):
        for gp in self.adam.param_groups:
            gp["lr"] = lr
        self.adam.step()
        for n, p in self.muon:
            if p.grad is None:
                continue
            g = p.grad.float()
            U = torch.empty_like(p, dtype=torch.float32)
            Uv = U.view(self.H, 3, self.DH, U.size(1)) if (n.endswith("attention.query_key_value.weight") and self.split_qkv) else None
            for key, gpiece, j in self._pieces(n, g):
                buf = self.buf.get(key)
                if buf is None:
                    buf = self.buf[key] = torch.zeros_like(gpiece, dtype=torch.float32)
                buf.mul_(self.mu).add_(gpiece)
                gn = gpiece.add(buf, alpha=self.mu)                         # Nesterov
                u = ns5(gn, self.ns_steps, self.ns_dtype).float() * (0.2 * math.sqrt(max(gpiece.size(0), gpiece.size(1))))
                if j is None:
                    U.copy_(u)
                else:
                    Uv[:, j] = u.view(self.H, self.DH, U.size(1))
            p.mul_(1 - lr * self.wd)
            p.add_(U, alpha=-lr)

    def zero_grad(self, set_to_none=True):
        self.adam.zero_grad(set_to_none=set_to_none)
        for _, p in self.muon:
            p.grad = None

    def state_dict(self):
        return {"adam": self.adam.state_dict(), "buf": {f"{k[0]}|{k[1]}": v for k, v in self.buf.items()}, "version": MUON_VERSION}

    def load_state_dict(self, st):
        self.adam.load_state_dict(st["adam"])
        self.buf = {(k.split("|")[0], None if k.split("|")[1] == "None" else int(k.split("|")[1])): v for k, v in st["buf"].items()}
