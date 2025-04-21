import torch
from typing import Tuple

def _make_input_reference_token_type_pair(
        self, input_ids: torch.Tensor, sep_idx: int = 0
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Returns two tensors indicating the corresponding token types for the `input_ids`
        and a corresponding all zero reference token type tensor.
        Args:
            input_ids (torch.Tensor): Tensor of text converted to `input_ids`
            sep_idx (int, optional):  Defaults to 0.

        Returns:
            Tuple[torch.Tensor, torch.Tensor]
        """
        seq_len = input_ids.size(1)
        #token_type_ids = torch.tensor([0 if i <= sep_idx else 1 for i in range(seq_len)], device=self.device).expand_as(
        #    input_ids
        #)
        token_type_ids = torch.zeros(seq_len, dtype=torch.int, device=self.device).expand_as(input_ids)
        ref_token_type_ids = torch.zeros_like(token_type_ids, device=self.device).expand_as(input_ids)

        return (token_type_ids, ref_token_type_ids)