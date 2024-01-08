import datasets
from datasets import GeneratorBasedBuilder, DatasetInfo, SplitGenerator, Split
from datasets.features import Features, Value, Sequence
from pathlib import Path
import simplejson as json


class MyDataset(GeneratorBasedBuilder):
    VERSION = datasets.Version("1.0.0")
    
    def __init__(self, maxWindow: int, **kwargs):
        super().__init__(**kwargs)
        self.maxWindow = maxWindow
        return
    
    def _info(self):
        return DatasetInfo(
            description="AIlice trace dataset",
            features=Features({
                "conversations": Sequence({
                    "role": Value("string"),
                    "msg": Value("string"),
                }),
            }),
            supervised_keys=None,
        )
    
    def _split_generators(self, dl_manager):
        return [
            SplitGenerator(name=Split.TRAIN, gen_kwargs={"datasetDir": dl_manager.manual_dir}),
        ]
    
    def _generate_examples(self, datasetDir):
        idx = -1
        directoryPath = Path(datasetDir)
        for jsonFile in directoryPath.glob('*.json'):
            with jsonFile.open('r', encoding='utf-8') as f:
                data = json.load(f)
                for conv in self.ExtractConversations(data):
                    for convPiece in self.Split(conv):
                        idx += 1
                        yield idx, {'conversations': convPiece}

    def ExtractConversations(self, trace):
        convs = []
        agentTrace = trace
        convs.append(agentTrace['conversations'])
        if 'subProcessors' in agentTrace:
            for subAgent in agentTrace['subProcessors']:
                convs += self.ExtractConversations(agentTrace['subProcessors'][subAgent])
        return convs
    
    def Split(self, conv):
        ret = [[]]
        currentLen = 0
        for c in conv:
            currentLen += len(f"{c['role']}: {c['msg']}")
            if (currentLen // 4) >= self.maxWindow:
                ret.append([c])
                currentLen = 0
            else:
                ret[-1].append(c)
        return ret