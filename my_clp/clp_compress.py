import os
import pickle
import typing

import zstandard as zstd
from tqdm import tqdm

from auto_generate_log import log_templates
from utils import *


class Log:
    """
    结构化Log单条消息，其中有几个成员变量
    self.log_content：这条日志的字符串
    self.log_type_id：这条日志属于哪个日志模板
    self.log_variables：这条日志中的变量（包含时间戳），使用列表存储
    """
    def __init__(self, log_content: str, template: typing.List[str]):
        """
        传入单条日志，解析日志，获取几个结构话消息
        :param log_content: 单条日志字符串消息
        :param template: 没啥用
        """
        self.log_content = log_content
        # self.log_template = template
        self.log_type_id = self._match_log_to_template()
        if self.log_type_id is None:
            print(f"the log '{self.log_content}' don't match any template")
            return
        self.log_type = log_templates[self.log_type_id]
        self.log_variables = self._extract_variables_from_log()
        if not self.log_variables:
            print(f"error iin exact variables in log {log_content} please checkout")
            return

    def _match_log_to_template(self) -> typing.Union[int, None]:
        """
        将日志与模板对应，使用正则表达式
        :return: 返回这条日志在日志模板列表中的下标
        """
        templates = log_templates
        log = self.log_content
        regex_templates = [re.sub(r'\{[^}]*\}', '.*', template) for template in templates]
        for i, regex in enumerate(regex_templates):
            if re.match(regex, log):
                return i
        return None

    def _extract_variables_from_log(self) -> typing.Union[typing.List[str], None]:
        """
        将日志中的变量全部提取出来，装在一个列表中返回
        :return:
        """
        log = self.log_content
        template = self.log_type
        regex_pattern = re.sub(r'\{[^}]*\}', '(.*)', template)
        matches = re.match(regex_pattern, log)
        if matches:
            return list(matches.groups())
        else:
            return None


class LogFile:
    """
    读取一个原始日志文件，将其中每一条日志封装成Log，之后存储在一个列表中
    重写[], len(), del 方法，让其类似于列表
    """
    def __init__(self, log_path: str):
        self.log_file_path = log_path
        _log_list = self.read_log_file()
        self.log_list = []
        for each_log in tqdm(_log_list, desc="处理日志"):
            self.log_list.append(Log(each_log, log_templates))
        del _log_list

    def read_log_file(self) -> str:
        with open(self.log_file_path, 'r') as file:
            for line in file:
                yield line.strip()

    def __getitem__(self, item):
        return self.log_list[item]

    def __delitem__(self, index):
        del self.log_list[index]

    def __len__(self):
        return len(self.log_list)


class CompressLogFile:
    """
    主要压缩类
    """
    LOG_TEMPLATE_INDEX = 0
    VARIABLE_INDEX = 1
    DATATIME_INDEX = 0

    def __init__(self, log_file_path: str, template: typing.List[str], sve_path: str):
        if not os.path.exists(sve_path):
            os.makedirs(sve_path)
        self.all_log = LogFile(log_file_path)
        self.template = template
        self.save_path = sve_path
        """
        制作log_variable，类似与变量字典以及日志字典的集合
        [
            [
                "日志模板",
                [
                    [
                        [,]  # 变量1以及其在文件中的位置
                    ], # 模板中第一个变量
                    [
                        
                    ],# 模板中第二个变量
                    ...
                ]
            ],
            [],
            []
            ...
        ]
        
        """
        self.log_variable = [[each_template.replace("{datetime} ", ''), list()] for each_template in self.template]
        for index, each_log_tmp in enumerate(self.log_variable):
            variable_num = count_pattern(each_log_tmp[self.LOG_TEMPLATE_INDEX])
            for x in range(variable_num):
                self.log_variable[index][self.VARIABLE_INDEX].append(list())
        self._compress()
        del self.all_log
        del self.log_variable
        self.second_compress()

    def _compress(self) -> None:
        """
        第一次压缩
        :return:
        """
        print("start compress")
        save_file = open(os.path.join(self.save_path, "compress_file.bin"), "wb")
        save_pkl = open(os.path.join(self.save_path, "log_variable.pkl"), "wb")

        for each_log in tqdm(self.all_log, desc="压缩"):
            try:
                # 压缩时间戳以及变量类型index
                file_position = save_file.tell()
                binary_datatime = str_datatime2binary64(each_log.log_variables[self.DATATIME_INDEX])
                binary_log_type = int2binary64(each_log.log_type_id)
            except:
                continue
            save_file.write(binary_datatime)
            save_file.write(binary_log_type)

            # 压缩变量
            for variable_index, each_variable in enumerate(each_log.log_variables):
                if variable_index == self.DATATIME_INDEX:
                    continue
                self.log_variable[each_log.log_type_id][self.VARIABLE_INDEX][variable_index - 1].append(
                    [each_variable, file_position])
                new_element_index = len(
                    self.log_variable[each_log.log_type_id][self.VARIABLE_INDEX][variable_index - 1]) - 1

                new_element_index_binary = int2binary64(new_element_index)
                save_file.write(new_element_index_binary)

        pickle.dump(self.log_variable, save_pkl)
        save_pkl.close()
        save_file.close()
        print("finish")

    def second_compress(self, compression_level: int = 22) -> None:
        """
        调用zstander api二次压缩
        :param compression_level: 压缩级别（论文用的5,我用22）
        :return:
        """
        compressor = zstd.ZstdCompressor(level=compression_level)
        compress_file = ["compress_file.bin", "log_variable.pkl"]
        for each_file in compress_file:
            with open(os.path.join(self.save_path, each_file), 'rb') as file:
                data = file.read()
            compressed_data = compressor.compress(data)
            with open(os.path.join(self.save_path, f"{each_file}.zst"), 'wb') as compressed_file:
                compressed_file.write(compressed_data)


def main() -> None:
    CompressLogFile("log.log", log_templates, "./output")


if __name__ == '__main__':
    main()
