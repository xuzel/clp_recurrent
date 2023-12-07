import re
import sys
import typing
from auto_generate_log import log_templates


class Log:
    def __init__(self, log_contain: str, template: typing.List[str]):
        self.log_contain = log_contain
        self.log_template = template
        self.log_type_id = self._match_log_to_template()
        if self.log_type_id is None:
            print(f"the log '{self.log_contain}' don't match any template")
            return
        self.log_type = self.log_template[self.log_type_id]
        self.log_variables = self._extract_variables_from_log()
        if not self.log_variables:
            print(f"error iin exact variables in log {log_contain} please checkout")
            return

    def _match_log_to_template(self):
        templates = self.log_template
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
        _log_list = [x.replace("\n", '') for x in _log_list]
        if not _log_list:
            return
        self.log_list = [Log(each_log, log_templates) for each_log in _log_list]

    def read_log_file(self) -> typing.List[str]:
        path = self.log_file_path
        try:
            log_file = open(path, 'r')
        except IOError as e:
            print(f"can't open the file {self.log_file_path}")
            return []
        log_list = log_file.readlines()
        # print(type(log_list))
        log_file.close()
        return log_list

    def get_all_logs(self) -> typing.List[Log]:
        return self.log_list

    def get_log_using_index(self, index: int) -> Log:
        return self.log_list[index]

    def __getitem__(self, item):
        return self.log_list[item]


def main() -> None:
    all_log = LogFile("log_tmp.log")
    for x in range(10):
        print(all_log[x].log_contain)


if __name__ == '__main__':
    main()
