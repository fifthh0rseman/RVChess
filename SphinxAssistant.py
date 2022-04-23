# Deprecated and not working shit.
# thx for nice documentation sphinx yeah very nice

import os
from pocketsphinx import LiveSpeech, get_model_path
from pocketsphinx import Decoder

model_path = get_model_path()

speech = LiveSpeech(verbose=False,
                    sampling_rate=16000,
                    buffer_size=512,
                    no_search=False,
                    full_utt=False,
                    hmm=os.path.join(model_path, 'en-us'),
                    lm=os.path.join(model_path, 'en-us.lm.bin'),
                    dic='./ChessDict.dict')
print("Speak please")

for phrase in speech:
    print("Receiving:" + str(phrase))
