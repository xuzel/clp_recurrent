import pickle
import os
import sys

from utils import *
from auto_generate_log import log_templates

LOG_TEMPLATE_INDEX = 0
VARIABLE_INDEX = 1
DATATIME_INDEX = 0


class Decompress:
    def __init__(self, file_path: str, save_path: str):
        with open(os.path.join(file_path, "log_variable.pkl"), "rb") as pkl_file:
            self.log_variable = pickle.load(pkl_file)
        self.compress_file = open(os.path.join(file_path, "compress_file.bin"), "rb")
        self.save_path = save_path
        self._decompress()

    def _decompress(self):
        save_file = open(os.path.join(self.save_path, "decompress.log"), 'w')
        datatime_pointer = 0
        log_type_pointer = 1
        variable_pointer = 2
        this_pointer = datatime_pointer
        variable_num = 0
        log_type_id = 0
        this_log = ""
        while True:
            bytes_read = self.compress_file.read(8)
            if not bytes_read:
                break
            if this_pointer == datatime_pointer:
                data = binary64_to_datatime(bytes_read)
                this_log += data
                this_pointer = log_type_pointer
            elif this_pointer == log_type_pointer:
                log_type_id = binary64_to_int(bytes_read)
                log_template = log_templates[log_type_id]
                variable_num = count_pattern(log_template)
                this_log += log_template.replace("{datetime}", '')
                if variable_num == 1:
                    this_pointer = datatime_pointer
                    save_file.write(this_log + '\n')
                else:
                    this_pointer = variable_pointer
            elif this_pointer == variable_pointer:
                for each_variable in range(variable_num - 1):
                    # if variable_num == 1:
                    #     break
                    if each_variable != 0:
                        bytes_read = self.compress_file.read(8)
                    second_list_index = binary64_to_int(bytes_read)
                    variable_value = self.log_variable[log_type_id][VARIABLE_INDEX][each_variable][second_list_index][0]
                    this_log = replace_first_bracket(this_log, variable_value)
                save_file.write(this_log + '\n')
                this_pointer = datatime_pointer
                this_log = ""



if __name__ == '__main__':
    Decompress('output', './')
