import re
from typing import List
from pymatlabparser.matlab_lexer import MatlabLexer

class MatlabStyleChecker:
    """Simple checker for a subset of Monkeyproof MATLAB style rules."""

    _OP_TOKENS = {
        'ASSIGN', 'COLON', 'POWER', 'MPOWER',
        'EQ', 'LE', 'GE', 'LT', 'GT', 'NE',
        'AND', 'ANDAND', 'OR', 'OROR',
        'PLUS', 'MINUS', 'TIMES', 'MTIMES',
        'RDIVIDE', 'LDIVIDE', 'MRDIVIDE', 'MLDIVIDE'
    }

    _KEYWORD_TOKENS = {
        'FOR', 'WHILE', 'IF', 'ELSE', 'ELSEIF', 'SWITCH',
        'TRY', 'CATCH', 'CASE', 'FUNCTION', 'RETURN'
    }

    def __init__(self):
        self.lexer = MatlabLexer()

    def check_text(self, text: str) -> List[str]:
        tokens = list(self.lexer.tokenize(text, append_newline=True))
        errors: List[str] = []
        errors += self._check_commands(tokens)
        errors += self._check_keyword_spacing(tokens, text)
        errors += self._check_punctuation(tokens, text)
        errors += self._check_operator_spacing(tokens, text)
        errors += self._check_function_indentation(text)
        return errors

    def check_file(self, filename: str) -> List[str]:
        with open(filename, 'r') as f:
            text = f.read()
        return self.check_text(text)

    # ------------------------------------------------------------------
    def _check_commands(self, tokens):
        errors = []
        for tok in tokens:
            if tok.type == 'COMMAND':
                errors.append(f"Line {tok.lineno}: command syntax is not allowed")
        return errors

    def _check_keyword_spacing(self, tokens, text):
        errors = []
        for tok in tokens:
            if tok.type in self._KEYWORD_TOKENS:
                end = tok.index + len(tok.value)
                after = text[end] if end < len(text) else '\n'
                if after not in (' ', '\n'):
                    errors.append(
                        f"Line {tok.lineno}: keyword '{tok.value}' should be followed by a space")
        return errors

    def _check_punctuation(self, tokens, text):
        errors = []
        for tok in tokens:
            if tok.type == 'COMMA':
                before = text[tok.index - 1] if tok.index > 0 else ''
                after = text[tok.index + 1] if tok.index + 1 < len(text) else ''
                if before == ' ':
                    errors.append(f"Line {tok.lineno}: comma should not be preceded by space")
                if after not in (' ', '\n', ']', ')', '}', ';'):
                    errors.append(f"Line {tok.lineno}: comma should be followed by space")
            elif tok.type == 'SEMICOLON':
                after = text[tok.index + 1] if tok.index + 1 < len(text) else ''
                if after not in (' ', '\n', '%'):
                    errors.append(
                        f"Line {tok.lineno}: semicolon should be followed by space if another statement follows")
        return errors

    def _check_operator_spacing(self, tokens, text):
        errors = []
        for tok in tokens:
            if tok.type in self._OP_TOKENS:
                start = tok.index
                end = start + len(tok.value)
                before = text[start - 1] if start > 0 else ''
                after = text[end] if end < len(text) else ''

                if tok.type == 'MINUS' and self._is_unary_minus(text, start):
                    if after == ' ':
                        errors.append(f"Line {tok.lineno}: unary minus should not be followed by space")
                    continue

                if before != ' ' or after != ' ':
                    errors.append(f"Line {tok.lineno}: operator '{tok.value}' should be surrounded by spaces")
        return errors

    def _is_unary_minus(self, text, index):
        j = index - 1
        while j >= 0 and text[j].isspace():
            j -= 1
        if j < 0:
            return True
        if text[j] in '([{-=:+*/^&|~<>,' or text[j] == '\n':
            return True
        return False

    def _check_function_indentation(self, text):
        errors = []
        stack = []
        lines = text.splitlines()
        for i, line in enumerate(lines, start=1):
            stripped = line.lstrip()
            if not stripped or stripped.startswith('%'):
                continue
            indent = len(line) - len(stripped)
            if re.match(r'function\b', stripped):
                stack.append((indent, i))
                continue
            if re.match(r'end\b', stripped):
                if stack:
                    stack.pop()
                continue
            if stack:
                func_indent, fn_line = stack[-1]
                if indent <= func_indent:
                    errors.append(
                        f"Line {i}: function body starting at line {fn_line} should be indented")
        return errors

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print('Usage: python -m pymatlabparser.matlab_style_checker <file>')
        sys.exit(1)
    checker = MatlabStyleChecker()
    err = checker.check_file(sys.argv[1])
    if err:
        for e in err:
            print(e)
        sys.exit(1)
    else:
        print('No style issues found.')
