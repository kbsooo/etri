from __future__ import annotations

import torch
from torch import nn


class PyramidDayEncoder(nn.Module):
    """Transformer encoder for 5-minute day tensors plus event/prototype tokens."""

    def __init__(
        self,
        input_channels: int,
        base_channels: int,
        slot_feature_dim: int,
        event_dim: int,
        prototype_k: int,
        n_prototype_groups: int,
        day_context_dim: int,
        slots: int = 288,
        d_model: int = 96,
        latent_dim: int = 96,
        n_layers: int = 2,
        n_heads: int = 4,
        dropout: float = 0.15,
    ) -> None:
        super().__init__()
        self.input_channels = input_channels
        self.base_channels = base_channels
        self.slots = slots
        self.d_model = d_model
        self.latent_dim = latent_dim
        self.n_prototype_groups = n_prototype_groups

        self.slot_proj = nn.Sequential(
            nn.Linear(input_channels * 2 + slot_feature_dim, d_model),
            nn.LayerNorm(d_model),
            nn.GELU(),
            nn.Dropout(dropout),
        )
        self.event_proj = nn.Sequential(
            nn.Linear(event_dim, d_model),
            nn.LayerNorm(d_model),
            nn.GELU(),
            nn.Dropout(dropout),
        )
        self.prototype_proj = nn.Sequential(
            nn.Linear(prototype_k, d_model),
            nn.LayerNorm(d_model),
            nn.GELU(),
            nn.Dropout(dropout),
        )
        self.context_proj = nn.Sequential(
            nn.Linear(day_context_dim, d_model),
            nn.GELU(),
            nn.Linear(d_model, d_model),
        )
        self.slot_position = nn.Parameter(torch.zeros(1, slots, d_model))
        self.prototype_group_embedding = nn.Parameter(torch.zeros(1, n_prototype_groups, d_model))
        self.cls_token = nn.Parameter(torch.zeros(1, 1, d_model))
        self.block_type_embedding = nn.Parameter(torch.zeros(1, 3, d_model))

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
        self.latent_proj = nn.Sequential(
            nn.Linear(d_model, d_model),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model, latent_dim),
        )
        self.actual_head = nn.Sequential(
            nn.Linear(d_model, d_model),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model, base_channels),
        )
        self.delta_head = nn.Sequential(
            nn.Linear(d_model, d_model),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model, base_channels),
        )

        nn.init.normal_(self.cls_token, std=0.02)
        nn.init.normal_(self.slot_position, std=0.02)
        nn.init.normal_(self.prototype_group_embedding, std=0.02)
        nn.init.normal_(self.block_type_embedding, std=0.02)

    def forward(
        self,
        x: torch.Tensor,
        mask: torch.Tensor,
        slot_features: torch.Tensor,
        event_tokens: torch.Tensor,
        event_mask: torch.Tensor,
        prototype_mixture: torch.Tensor,
        day_context: torch.Tensor,
    ) -> dict[str, torch.Tensor]:
        batch, slots, _ = x.shape
        if slots != self.slots:
            raise ValueError(f"Expected {self.slots} slots, got {slots}")

        slot_features = slot_features.unsqueeze(0).expand(batch, -1, -1)
        context = self.context_proj(day_context).unsqueeze(1)

        slot_input = torch.cat([x, mask, slot_features], dim=-1)
        slot_tokens = self.slot_proj(slot_input)
        slot_tokens = slot_tokens + self.slot_position + context + self.block_type_embedding[:, 0:1]

        event_tokens_emb = self.event_proj(event_tokens)
        event_tokens_emb = event_tokens_emb + context + self.block_type_embedding[:, 1:2]

        prototype_tokens = self.prototype_proj(prototype_mixture)
        prototype_tokens = (
            prototype_tokens
            + self.prototype_group_embedding
            + context
            + self.block_type_embedding[:, 2:3]
        )

        cls = self.cls_token.expand(batch, 1, self.d_model) + context
        tokens = torch.cat([cls, slot_tokens, event_tokens_emb, prototype_tokens], dim=1)

        event_padding = event_mask < 0.5
        padding = torch.cat(
            [
                torch.zeros(batch, 1 + slots, device=x.device, dtype=torch.bool),
                event_padding,
                torch.zeros(batch, self.n_prototype_groups, device=x.device, dtype=torch.bool),
            ],
            dim=1,
        )
        encoded = self.final_norm(self.encoder(tokens, src_key_padding_mask=padding))
        cls_encoded = encoded[:, 0]
        slot_encoded = encoded[:, 1 : 1 + slots]
        latent = self.latent_proj(cls_encoded)
        actual_pred = self.actual_head(slot_encoded)
        delta_pred = self.delta_head(slot_encoded)
        return {
            "latent": latent,
            "slot_tokens": slot_encoded,
            "actual_pred": actual_pred,
            "delta_pred": delta_pred,
        }
