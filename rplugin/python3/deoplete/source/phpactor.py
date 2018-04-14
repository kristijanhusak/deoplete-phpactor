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
        self.rank = 500
        self.max_pattern_length = -1
        self.matchers = ['matcher_full_fuzzy']

    def get_complete_position(self, context):
        line = self.vim.eval('getline(".")')
        start = self.vim.eval('col(".")')
        triggers = ['->', '::']
        while start > 0:
            if line[start - 1:start] == '$':
                return start

            if line[start - 2:start] in triggers:
                return start

            start -= 1
        return start

    def gather_candidates(self, context):
        self._phpactor = self.vim.eval(
            r"""globpath(&rtp, 'bin/phpactor', 1)"""
        )

        if not self._phpactor:
            self.print_error(
                'phpactor not found,'
                ' please install https://github.com/phpactor/phpactor'
            )

        candidates = []

        line_offset = int(self.vim.eval('line2byte(line("."))'))
        column_offset = int(self.vim.eval('col(".")')) - 2
        offset = line_offset + column_offset + len(context['complete_str'])

        args = [
            'php',
            self._phpactor,
            'rpc',
            '--working-dir=%s' % self.vim.eval('getcwd()')
        ]

        proc = subprocess.Popen(
            args=args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        source = self.vim.eval('join(getline(1, "$"), "\n")')
        data = json.dumps({
            'action': 'complete',
            'parameters': {'source': source, 'offset': offset}
        })
        result, errs = proc.communicate(data.encode('utf-8'))

        errs = errs.decode()
        if errs:
            return self.print_error(errs)

        result = json.loads(result.decode())
        result = result['parameters']['value']

        if len(result['issues']) > 0:
            self.vim.call(
                'deoplete#util#print_error',
                ', '.join(result['issues']),
                'deoplete-phpactor'
            )

        if len(result['suggestions']) > 0:
            for suggestion in result['suggestions']:
                candidates.append({
                    'word': suggestion['name'],
                    'menu': suggestion['info'],
                    'kind': suggestion['type']
                })

        return candidates
