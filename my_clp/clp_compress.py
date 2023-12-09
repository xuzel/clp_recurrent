import os
import re
import sys
import typing
from auto_generate_log import log_templates
import copy
from datetime import datetime
import struct
import pickle
from tqdm import tqdm


class Log:
    def __init__(self, log_contain: str, template: typing.List[str]):
        self.log_contain = log_contain
        # self.log_template = template
        self.log_type_id = self._match_log_to_template()
        if self.log_type_id is None:
            print(f"the log '{self.log_contain}' don't match any template")
            return
        self.log_type = log_templates[self.log_type_id]
        self.log_variables = self._extract_variables_from_log()
        if not self.log_variables:
            print(f"error iin exact variables in log {log_contain} please checkout")
            return

    def _match_log_to_template(self):
        templates = log_templates
        log = self.log_contain
        # 将模板转换成正则表达式
        regex_templates = [re.sub(r'\{[^}]*\}', '.*', template) for template in templates]
        # print(regex_templates[0])
        # sys.exit()

        for i, regex in enumerate(regex_templates):
            if re.match(regex, log):
                return i
        return None

    def _extract_variables_from_log(self):
        log = self.log_contain
        template = self.log_type
        # 将模板中的变量替换为正则表达式的捕获组
        regex_pattern = re.sub(r'\{[^}]*\}', '(.*)', template)

        # 使用正则表达式匹配日志
        matches = re.match(regex_pattern, log)

        if matches:
            # 返回所有捕获的组（不包括整个匹配的字符串）
            return list(matches.groups())
        else:
            return None


class LogFile:
    def __init__(self, log_path: str):
        self.log_file_path = log_path
        _log_list = self.read_log_file()
        # _log_list = [x.replace("\n", '') for x in _log_list]
        # if not _log_list:
        #     return
        self.log_list = []
        for each_log in tqdm(_log_list, desc="处理日志"):
            self.log_list.append(Log(each_log, log_templates))
        del _log_list

    def read_log_file(self) -> typing.List[str]:
        # path = self.log_file_path
        # try:
        #     log_file = open(path, 'r')
        # except IOError as e:
        #     print(f"can't open the file {self.log_file_path}")
        #     return []
        # log_list = log_file.readlines()
        # # print(type(log_list))
        # log_file.close()
        # return log_list[1:]
        with open(self.log_file_path, 'r') as file:
            next(file)
            for line in file:
                yield line.strip()

    def __getitem__(self, item):
        return self.log_list[item]

    def __delitem__(self, index):
        del self.log_list[index]

    def __len__(self):
        return len(self.log_list)


def count_pattern(text: str, pattern: str = r"\{.*?\}"):
    return len(re.findall(pattern, text))


def datatime2unix(date_string: str, datatime_format: str = '%Y-%m-%d %H:%M:%S.%f') -> float:
    date_obj = datetime.strptime(date_string, datatime_format)
    timestamp = date_obj.timestamp()
    return timestamp


def float2binary64(value: float):
    packed = struct.pack('d', value)
    return packed


def int2binary64(value: int):
    binary_data = struct.pack('q', value)
    return binary_data


def str_datatime2binary64(value: str):
    return float2binary64(datatime2unix(value))


class CompressLogFile:
    LOG_TEMPLATE_INDEX = 0
    VARIABLE_INDEX = 1

    DATATIME_INDEX = 0

    def __init__(self, log_file_path: str, template: typing.List[str], sve_path: str):
        self.all_log = LogFile(log_file_path)
        self.template = template
        self.save_path = sve_path
        self.log_variable = [[each_template.replace("{datetime} ", ''), list()] for each_template in self.template]
        for index, each_log_tmp in enumerate(self.log_variable):
            variable_num = count_pattern(each_log_tmp[self.LOG_TEMPLATE_INDEX])
            for x in range(variable_num):
                self.log_variable[index][self.VARIABLE_INDEX].append(list())
        self._compress()

    def _compress(self):
        print("start compress")
        save_file = open(os.path.join(self.save_path, "compress_file.bin"), "wb")
        save_pkl = open(os.path.join(self.save_path, "log_variable.pkl"), "wb")

        for each_log in tqdm(self.all_log, desc="压缩"):
            try:
                file_position = save_file.tell()
                binary_datatime = str_datatime2binary64(each_log.log_variables[self.DATATIME_INDEX])
                save_file.write(binary_datatime)
                binary_log_type = int2binary64(each_log.log_type_id)
                save_file.write(binary_log_type)
                for variable_index, each_variable in enumerate(each_log.log_variables):
                    if variable_index == self.DATATIME_INDEX:
                        continue
                    # matching_list = None
                    # for index, sublist in enumerate(self.log_variable[each_log.log_type_id][self.VARIABLE_INDEX][variable_index - 1]):
                    #     if sublist[0] == each_variable:
                    #         matching_list = sublist
                    #         break
                    # if matching_list:
                    #     self.log_variable[each_log.log_type_id][self.VARIABLE_INDEX][variable_index - 1][index][1].append(file_position)
                    #     new_element_index = index
                    # else:
                    #     self.log_variable[each_log.log_type_id][self.VARIABLE_INDEX][variable_index - 1].append(
                    #         [each_variable, [file_position]])
                    #     new_element_index = len(
                    #         self.log_variable[each_log.log_type_id][self.VARIABLE_INDEX][variable_index - 1]) - 1

                    self.log_variable[each_log.log_type_id][self.VARIABLE_INDEX][variable_index - 1].append(
                        [each_variable, file_position])
                    new_element_index = len(
                        self.log_variable[each_log.log_type_id][self.VARIABLE_INDEX][variable_index - 1]) - 1

                    new_element_index_binary = int2binary64(new_element_index)
                    save_file.write(new_element_index_binary)
                    # del self.all_log[variable_index]
            except:
                continue
        pickle.dump(self.log_variable, save_pkl)
        save_pkl.close()
        save_file.close()
        print("finish")


def main() -> None:
    CompressLogFile("log_tmp.log", log_templates, "./output")


if __name__ == '__main__':
    main()
