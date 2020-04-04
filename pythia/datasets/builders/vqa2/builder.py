# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#


import os
import warnings

from pythia.common.registry import registry
from pythia.datasets.base_dataset_builder import BaseDatasetBuilder
from pythia.datasets.concat_dataset import PythiaConcatDataset
from pythia.datasets.builders.vqa2.dataset import VQA2Dataset


@registry.register_builder("vqa2")
class VQA2Builder(BaseDatasetBuilder):
    def __init__(self, dataset_name="vqa2"):
        super().__init__(dataset_name)
        self.dataset_class = VQA2Dataset

    @classmethod
    def config_path(cls):
        return "configs/datasets/vqa2/defaults.yaml"

    def _load(self, dataset_type, config, *args, **kwargs):
        self.config = config

        image_features = config["image_features"]["train"][0].split(",")
        self.num_image_features = len(image_features)

        registry.register("num_image_features", self.num_image_features)

        self.dataset = self.prepare_data_set(dataset_type, config)

        return self.dataset

    def _build(self, dataset_type, config):
        # TODO: Build actually here
        return

    def update_registry_for_model(self, config):
        if hasattr(self.dataset, "text_processor"):
            registry.register(
                self.dataset_name + "_text_vocab_size",
                self.dataset.text_processor.get_vocab_size(),
            )
        if hasattr(self.dataset, "answer_processor"):
            registry.register(
                self.dataset_name + "_num_final_outputs",
                self.dataset.answer_processor.get_vocab_size(),
            )

    def set_dataset_class(self, cls):
        self.dataset_class = cls

    def prepare_data_set(self, dataset_type, config):
        if dataset_type not in config.imdb_files:
            warnings.warn(
                "Dataset type {} is not present in "
                "imdb_files of dataset config. Returning None. "
                "This dataset won't be used.".format(dataset_type)
            )
            return None

        imdb_files = config["imdb_files"][dataset_type]

        datasets = []

        for imdb_idx in range(len(imdb_files)):
            cls = self.dataset_class
            dataset = cls(dataset_type, imdb_idx, config)
            datasets.append(dataset)

        dataset = PythiaConcatDataset(datasets)

        return dataset


@registry.register_builder("vqa2_train_val")
class VQA2TrainValBuilder(VQA2Builder):
    def __init__(self, dataset_name="vqa2_train_val"):
        super().__init__(dataset_name)

    @classmethod
    def config_path(self):
        return "configs/datasets/vqa2/train_val.yaml"