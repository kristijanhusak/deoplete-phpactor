from .base import Base
import json
import subprocess


class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'phpactor'
        self.mark = '[phpactor]'
        self.filetypes = ['php']
        self.is_bytepos = True
        self.input_pattern = '\w+|[^. \t]->\w*|\w+::\w*|\\\\'
        self.rank = 9999
        self.max_pattern_length = -1
        self.matchers = ['matcher_full_fuzzy']
        self._files = {}

    def get_complete_position(self, context):
        line = self.vim.eval('getline(".")')
        start = self.vim.eval('col(".")')
        triggers = ["->", "::"]
        while start > 0:
            if line[start-1:start] == "$":
                return start

            if line[start-2:start] in triggers:
                return start

            start -= 1
        return start

    def gather_candidates(self, context):
        self._phpactor = self.vim.eval(
            r"""globpath(&rtp, 'bin/phpactor', 1)""")

        if not self._phpactor:
            self.print_error(
                'phpactor not found,'
                ' please install https://github.com/phpactor/phpactor')
        candidates = []
        offset = int(
            self.vim.eval('line2byte(line("."))')) + int(
                self.vim.eval('col(".")')) - 2 + len(
                    context['complete_str'])
        args = ['php',
                self._phpactor,
                'rpc',
                '--working-dir=%s' % self.vim.eval('getcwd()')]
        proc = subprocess.Popen(args=args,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        source = self.vim.eval("join(getline(1, '$'), '\n')")
        data = json.dumps(
            {"action": "complete",
             "parameters":
             {"source": source, "offset": offset}})
        result, errs = proc.communicate(data.encode('utf-8'))

        errs = errs.decode()
        if errs:
            return self.print_error(errs)

        result = result.decode()
        result = json.loads(result)

        suggestions = result['parameters']['value']['suggestions']
        if result['action'] == 'return' and len(suggestions) > 0:
            for item in suggestions:
                candidates.append({'word': item['name'],
                                   'menu': item['info'],
                                   'kind': item['type']})

        return candidates
