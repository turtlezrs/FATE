#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import argparse

from pipeline.backend.pipeline import PipeLine
from pipeline.component.dataio import DataIO
from pipeline.component.reader import Reader
from pipeline.component.union import Union
from pipeline.demo.util.demo_util import Config
from pipeline.interface.data import Data


def main(config="../config.yaml"):
    # obtain config
    config = Config(config)
    guest = config.guest
    hosts = config.host
    arbiter = config.arbiter
    backend = config.backend
    work_mode = config.work_mode

    guest_train_data = {"name": "tag_value_1", "namespace": "experiment"}
    host_train_data = [{"name": "tag_value_1", "namespace": "experiment"},
                       {"name": "tag_value_2", "namespace": "experiment"}]

    pipeline = PipeLine().set_initiator(role='guest', party_id=guest).set_roles(guest=guest, host=hosts, arbiter=arbiter)

    reader_0 = Reader(name="reader_0")
    reader_0.get_party_instance(role='guest', party_id=guest).algorithm_param(table=guest_train_data)
    reader_0.get_party_instance(role='host', party_id=hosts[0]).algorithm_param(table=host_train_data[0])
    reader_0.get_party_instance(role='host', party_id=hosts[1]).algorithm_param(table=host_train_data[1])

    reader_1 = Reader(name="reader_1")
    reader_1.get_party_instance(role='guest', party_id=guest).algorithm_param(table=guest_train_data)
    reader_1.get_party_instance(role='host', party_id=hosts[0]).algorithm_param(table=host_train_data[0])
    reader_1.get_party_instance(role='host', party_id=hosts[1]).algorithm_param(table=host_train_data[1])

    dataio_0 = DataIO(name="dataio_0", input_format="tag", with_label=False, tag_with_value=True,
                      delimitor=",", output_format="dense")
    union_0 = Union(name="union_0", allow_missing=False, keep_duplicate=True)

    pipeline.add_component(reader_0)
    pipeline.add_component(reader_1)
    pipeline.add_component(union_0, data=Data(data=[reader_0.output.data, reader_1.output.data]))
    pipeline.add_component(dataio_0, data=Data(data=union_0.output.data))

    pipeline.compile()

    pipeline.fit(backend=backend, work_mode=work_mode)

    print(pipeline.get_component("union_0").get_summary())


if __name__ == "__main__":
    parser = argparse.ArgumentParser("PIPELINE DEMO")
    parser.add_argument("-config", type=str,
                        help="config file")
    args = parser.parse_args()
    if args.config is not None:
        main(args.config)
    else:
        main()