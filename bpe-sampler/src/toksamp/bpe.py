from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import regex as re 


GPT4_SPLIT_PATTERN = r"""'(?i:[sdmt]|ll|ve|re)|[^\r\n\p{L}\p{N}]?+\p{L}+|\p{N}{1,3}| ?[^\s\p{L}\p{N}]++[\r\n]*|\s*[\r\n]|\s+(?!\S)|\s+"""

# GPT-4o (o200k_base). Marks count as part of a word, so "नमस्ते" stays whole.
GPT4O_SPLIT_PATTERN = "|".join(
    [
        r"""[^\r\n\p{L}\p{N}]?[\p{Lu}\p{Lt}\p{Lm}\p{Lo}\p{M}]*[\p{Ll}\p{Lm}\p{Lo}\p{M}]+(?i:'s|'t|'re|'ve|'m|'ll|'d)?""",
        r"""[^\r\n\p{L}\p{N}]?[\p{Lu}\p{Lt}\p{Lm}\p{Lo}\p{M}]+[\p{Ll}\p{Lm}\p{Lo}\p{M}]*(?i:'s|'t|'re|'ve|'m|'ll|'d)?""",
        r"""\p{N}{1,3}""",
        r""" ?[^\s\p{L}\p{N}]+[\r\n/]*""",
        r"""\s*[\r\n]+""",
        r"""\s+(?!\S)""",
        r"""\s+""",
    ]
)
def get_stats(ids, counts=None, weight=1):
    counts = {} if counts is None else counts
    for pair in zip(ids, ids[1:]):
        counts[pair] = counts.get(pair,0) + weight
    return counts

def merge(ids, pair, new_id):
    out, i = [], 0
    while i < len(ids):
        if i + 1 < len(ids) and ids[i] == pair[0] and ids[i+1] == pair[1]:
            out.append(new_id)
            i += 2
        else:
            out.append(ids[i])
            i+=1
    return out
    

class BPETokenizer:
    def __init__(self, pattern: str = GPT4_SPLIT_PATTERN):
        self.pattern = pattern
        self._regex = re.compile(pattern)
        self.merges: dict[tuple[int,int] ,int] ={}
        self.vocab: dict[int, bytes] = {i: bytes([i]) for i in range(256)}
        self.cache: dict[str, list[int]] = {}

    @property
    def vocab_size(self) -> int:
        return len(self.vocab)

    def train(self, text: str, vocab_size: int, verbose: bool = False):
        if vocab_size < 256:
            raise ValueError("vocal_size if small atleas 256 is per byte")

        chuck_counts = Counter(self._regex.findall(text))
        words = [(list(chuck.encode('utf-8')),v) for chuck, v in chuck_counts.items()]
        words = [(idx,v) for idx, v in words if len(idx) > 1]

        merges : dict[tuple[int, int], int] = {}
        vocab = {i: bytes([i]) for i in range(256)}

        for new_id in range(256, vocab_size):
            stats: dict[tuple[int, int], int] ={}
            for ids, n in words:
                get_stats(ids, stats, n)
            if not stats:
                break

            pair = max(stats, key=stats.get)
            merges[pair] = new_id
            vocab[new_id] = vocab[pair[0]] + vocab[pair[1]]

            next_words = []
            for ids, n in words:
                if pair[0] in ids:
                    ids = merge(ids,pair,new_id)
                if len(ids) > 1:
                    next_words.append((ids, n))
            words = next_words
            if verbose and (new_id - 256 ) % 100 == 0:
                print(
                    f"merge {new_id - 255}/{vocab_size -256}: {pair} => {new_id}"
                    f"{vocab[new_id]!r} ({stats[pair]:,} times)"
                    )
        self.merges, self.vocab, self._cache = merges, vocab, {}
    def encode_chuck(self,chuck_bytes: bytes) -> list[int]:
        ids = list(chuck_bytes)
        while len(ids) > 1:
            stats = get_stats(ids)

            pair = min(stats, key=lambda p: self.merges.get(p, float("inf")))
            if pair not in self.merges:
                break
            ids = merge(ids, pair, self.merges[pair])
        return ids

    def encode(self,text:str) -> list[int]:
        ids:list[int] = []
        for chuck in self._regex.findall(text):
            if chuck not in self.cache:
                self._cache[chuck] = self.encode_chuck(chuck.encode("utf-8"))
            ids.extend(self._cache[chuck])
        return ids

    def decode(self, ids: list[int]) -> str:
        try:
            data = b"".join(self.vocab[i] for i in ids)
        except KeyError as e:
            raise ValueError(f"unknown token id :{e.args[0]}") from None
        return data.decode("utf-8", errors="replace")



code = BPETokenizer()
print(code.train(text="The order is temperature → top-k → top-p, as in Hugging Face's generate(). Top-k keeps ties with the k-th logit; top-p keeps the token that crosses p and never keeps fewer than one. The draw is an inverse-CDF lookup scaled by the CDF's last value, so floating-point sums that end at 0.9999999 cannot push the index out of range.",vocab_size=300))
print(code.train(text="The order is temperature → top-k → top-p, as in Hugging Face's generate()",vocab_size=310))
print(code.encode(text="ther asds thoa soucsn sadlo"))
print(code.decode(code.encode(text="ther asds thoa soucsn sadlo")))