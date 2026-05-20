from __future__ import annotations

import math

import torch
from torch import nn


class SinusoidalTimestepEmbedding(nn.Module):
    def __init__(self, dim: int) -> None:
        super().__init__()
        self.dim = dim

    def forward(self, timesteps: torch.Tensor) -> torch.Tensor:
        half = self.dim // 2
        freqs = torch.exp(
            -math.log(10000.0)
            * torch.arange(half, device=timesteps.device, dtype=torch.float32)
            / max(half - 1, 1)
        )
        args = timesteps.float().unsqueeze(1) * freqs.unsqueeze(0)
        emb = torch.cat([torch.sin(args), torch.cos(args)], dim=1)
        if self.dim % 2 == 1:
            emb = torch.cat([emb, torch.zeros_like(emb[:, :1])], dim=1)
        return emb


class DayDenoisingDiffusionEncoder(nn.Module):
    """Small transformer encoder that denoises a 24-hour multimodal day tensor.

    The model predicts the diffusion noise for each observed channel. The CLS
    token output is projected to the day latent vector used by downstream heads.
    """

    def __init__(
        self,
        channels: int,
        n_subjects: int,
        d_model: int = 128,
        latent_dim: int = 64,
        n_layers: int = 3,
        n_heads: int = 4,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.channels = channels
        self.d_model = d_model
        self.latent_dim = latent_dim

        self.input_proj = nn.Sequential(
            nn.Linear(channels * 2, d_model),
            nn.LayerNorm(d_model),
            nn.GELU(),
            nn.Dropout(dropout),
        )
        self.hour_embedding = nn.Embedding(24, d_model)
        self.subject_embedding = nn.Embedding(n_subjects, d_model)
        self.timestep_embedding = nn.Sequential(
            SinusoidalTimestepEmbedding(d_model),
            nn.Linear(d_model, d_model),
            nn.GELU(),
            nn.Linear(d_model, d_model),
        )
        self.cls_token = nn.Parameter(torch.zeros(1, 1, d_model))
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=d_model * 4,
            dropout=dropout,
            batch_first=True,
            activation="gelu",
            norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
        self.final_norm = nn.LayerNorm(d_model)
        self.latent_proj = nn.Sequential(nn.Linear(d_model, d_model), nn.GELU(), nn.Linear(d_model, latent_dim))
        self.noise_head = nn.Sequential(
            nn.Linear(d_model + latent_dim, d_model),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model, channels),
        )

        nn.init.normal_(self.cls_token, std=0.02)

    def _tokens(
        self,
        x_conditioned: torch.Tensor,
        condition_mask: torch.Tensor,
        subject_idx: torch.Tensor,
        timesteps: torch.Tensor,
    ) -> torch.Tensor:
        batch, hours, _ = x_conditioned.shape
        inputs = torch.cat([x_conditioned, condition_mask], dim=-1)
        hour_ids = torch.arange(hours, device=x_conditioned.device).unsqueeze(0).expand(batch, hours)
        tokens = self.input_proj(inputs)
        tokens = tokens + self.hour_embedding(hour_ids)
        tokens = tokens + self.subject_embedding(subject_idx).unsqueeze(1)
        tokens = tokens + self.timestep_embedding(timesteps).unsqueeze(1)
        cls = self.cls_token.expand(batch, 1, self.d_model)
        return torch.cat([cls, tokens], dim=1)

    def forward(
        self,
        x_conditioned: torch.Tensor,
        condition_mask: torch.Tensor,
        subject_idx: torch.Tensor,
        timesteps: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        tokens = self._tokens(x_conditioned, condition_mask, subject_idx, timesteps)
        encoded = self.final_norm(self.encoder(tokens))
        latent = self.latent_proj(encoded[:, 0])
        hour_tokens = encoded[:, 1:]
        latent_context = latent.unsqueeze(1).expand(-1, hour_tokens.shape[1], -1)
        noise_pred = self.noise_head(torch.cat([hour_tokens, latent_context], dim=-1))
        return noise_pred, latent

    @torch.no_grad()
    def encode(self, x: torch.Tensor, mask: torch.Tensor, subject_idx: torch.Tensor) -> torch.Tensor:
        t0 = torch.zeros(x.shape[0], device=x.device, dtype=torch.long)
        _, latent = self.forward(x * mask, mask, subject_idx, t0)
        return latent
