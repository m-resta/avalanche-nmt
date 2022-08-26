################################################################################
# 2022 Copyright (c) Facebook, Inc. and its affiliates.                        #
# Copyrights licensed under the MIT License.                                   #
# Copyright (c) 2022 ContinualAI.                                              #
# See the accompanying LICENSE file for terms.                                 #
#                                                                              #
# Date: 21-06-2020                                                             #
# Author(s): Michele Resta                                                     #
# E-mail: contact@continualai.org                                              #
# Website: continualai.org                                                     #
################################################################################

import re

SPACE_NORMALIZER = re.compile(r"\s+")


def tokenize_line(line):
    line = SPACE_NORMALIZER.sub(" ", line)
    line = line.strip()
    return line.split()
