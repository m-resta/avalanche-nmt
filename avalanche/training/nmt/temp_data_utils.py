# 2022 Copyright (c) Facebook, Inc. and its affiliates.
# 2022 Copyright (c) Michele Resta
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


def post_process(sentence: str, symbol: str):
    if symbol == "sentencepiece":
        sentence = sentence.replace(" ", "").replace("\u2581", " ").strip()
    elif symbol == "wordpiece":
        sentence = sentence.replace(" ", "").replace("_", " ").strip()
    elif symbol == "letter":
        sentence = sentence.replace(" ", "").replace("|", " ").strip()
    elif symbol == "silence":
        import re

        sentence = sentence.replace("<SIL>", "")
        sentence = re.sub(" +", " ", sentence).strip()
    elif symbol == "_EOW":
        sentence = sentence.replace(" ", "").replace("_EOW", " ").strip()
    elif symbol in {"subword_nmt", "@@ ", "@@"}:
        if symbol == "subword_nmt":
            symbol = "@@ "
        sentence = (sentence + " ").replace(symbol, "").rstrip()
    elif symbol == "none":
        pass
    elif symbol is not None:
        raise NotImplementedError(f"Unknown post_process option: {symbol}")
    return sentence
