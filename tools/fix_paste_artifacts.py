#!/usr/bin/env python3
"""
fix_paste_artifacts.py

Repair .py files that were pasted from markdown (e.g. from a phone) and
accumulated the following artifacts along the way:

  1. Smart quotes (U+201C/D, U+2018/9) instead of ASCII " and '.
  2. A leading `# ` on line 1 that turns the opening `\"\"\"` into a comment,
     leaving the module docstring unterminated.
  3. Stray bare ``` code fences between top-level constructs, left over from
     markdown code blocks.
  4. Markdown-bold renderings of __name__ and __main__ in the main guard
     (double-asterisk wrapping instead of double underscores).
  5. Class, function, and Enum bodies de-indented by one level because the
     markdown code block stripped the enclosing indentation. Methods and
     fields end up at module level instead of inside the class.
  6. Section-separator comments (# ===...) that get trapped inside the
     previous class body when structural indentation is restored.

Note: string literals in this file are constructed via concatenation to
avoid matching the fixer's own search patterns when it is run on itself.

The transformations only touch whitespace, quote characters, and stray
markdown artifacts. Content is preserved verbatim; docstring text
(including bare ``` fences inside docstrings) is left untouched.

Usage:
    python tools/fix_paste_artifacts.py file1.py file2.py ...
    python tools/fix_paste_artifacts.py --check file.py   # report only
    python tools/fix_paste_artifacts.py --verbose file.py

Exit codes:
    0  all files parse cleanly after fixing (or in --check mode, none
       needed fixing)
    1  at least one file still fails to parse, OR in --check mode, at
       least one file needs fixing

This is intentionally a standalone, stdlib-only script so it can run in
any environment including minimal CI images.
"""

import argparse
import ast
import re
import sys
from typing import List, Tuple


SMART_QUOTE_MAP = {
    "\u201C": '"',
    "\u201D": '"',
    "\u2018": "'",
    "\u2019": "'",
}

# Build the markdown-bold patterns via concatenation so this file can be
# safely run through its own fixer without rewriting itself.
_STAR = "*"
_BOLD_NAME = _STAR * 2 + "name" + _STAR * 2
_BOLD_MAIN = _STAR * 2 + "main" + _STAR * 2

METHOD_DEF_RE = re.compile(r"def \w+\s*\(\s*(self|cls)\b")
ANY_DEF_RE = re.compile(r"def \w+\s*\(")


def apply_text_replacements(text: str) -> str:
    """Replace smart quotes and markdown-bold renderings of dunder names."""
    for k, v in SMART_QUOTE_MAP.items():
        text = text.replace(k, v)
    text = text.replace(_BOLD_NAME, "__name__")
    text = text.replace(_BOLD_MAIN, "__main__")
    return text


def fix_line_one(lines: List[str]) -> List[str]:
    """If line 1 is '# \"\"\"' (comment artifact), drop the '# '."""
    if not lines:
        return lines
    first = lines[0]
    stripped = first.lstrip()
    if stripped.startswith("#"):
        remainder = stripped[1:].lstrip()
        if remainder.startswith('"""') or remainder.startswith("'''"):
            lines[0] = remainder
    return lines


def remove_bare_code_fences(lines: List[str]) -> List[str]:
    """Drop lines that are just ``` when they sit outside a docstring.

    Docstring state is tracked by counting `\"\"\"` occurrences per line:
    an odd count toggles in/out of a docstring. Code fences inside
    docstrings are preserved as decorative content.
    """
    result = []
    in_doc = False
    for line in lines:
        if line.strip() == "```" and not in_doc:
            continue
        result.append(line)
        if line.count('"""') % 2 == 1:
            in_doc = not in_doc
    return result


def _is_method_def(stripped: str) -> bool:
    return bool(METHOD_DEF_RE.match(stripped))


def _is_top_level_def(stripped: str) -> bool:
    return bool(ANY_DEF_RE.match(stripped)) and not _is_method_def(stripped)


def reindent_class_and_function_bodies(lines: List[str]) -> List[str]:
    """
    Add +4 spaces of indentation to every non-blank line that belongs to
    a top-level block whose body was collapsed to column 0.

    A top-level block is opened by one of:
        - `class X:` (at column 0)
        - `def X(...):` where the first argument is NOT `self` or `cls`
          (i.e. a module-level function, not a de-indented method)
        - `if __name__ == "__main__":`

    The block's body runs from the line after the header to the next
    top-level structural marker (another @decorator / class / top-level
    def / if __name__:). Multi-line expressions (inside matched brackets)
    are skipped so their contents don't accidentally close a block.
    """
    blocks: List[Tuple[int, int, int]] = []
    current_start = None
    in_doc = False
    brace_depth = 0

    n = len(lines)
    for i, line in enumerate(lines):
        if in_doc:
            if line.count('"""') % 2 == 1:
                in_doc = False
            continue

        if line.count('"""') % 2 == 1:
            in_doc = True
            continue

        for ch in line:
            if ch in "([{":
                brace_depth += 1
            elif ch in ")]}":
                brace_depth -= 1
        if brace_depth < 0:
            brace_depth = 0

        if brace_depth > 0:
            continue

        stripped = line.lstrip(" ")
        if not stripped.strip():
            continue

        orig_indent = len(line) - len(stripped)
        if orig_indent > 0:
            continue

        is_class = stripped.startswith("class ")
        is_at = stripped.startswith("@")
        is_top_def = _is_top_level_def(stripped)
        is_if_main = stripped.startswith("if __name__")

        is_closer = is_class or is_at or is_top_def or is_if_main
        is_opener = is_class or is_top_def or is_if_main

        if is_closer and current_start is not None:
            blocks.append((current_start, i, 4))
            current_start = None

        if is_opener:
            current_start = i + 1

    if current_start is not None:
        blocks.append((current_start, n, 4))

    out = list(lines)
    for start, end, delta in blocks:
        # Idempotency: if the first non-blank line of the block is already
        # indented, the block has already been fixed; skip it.
        first_non_blank = None
        for j in range(start, end):
            if out[j].strip() != "":
                first_non_blank = j
                break
        if first_non_blank is None:
            continue
        first_indent = len(out[first_non_blank]) - len(
            out[first_non_blank].lstrip(" ")
        )
        if first_indent >= delta:
            continue

        for j in range(start, end):
            if out[j].strip() != "":
                out[j] = (" " * delta) + out[j]

    return out


def _is_col0_block_marker(stripped: str) -> bool:
    return (
        stripped.startswith("@")
        or stripped.startswith("class ")
        or bool(ANY_DEF_RE.match(stripped))
        or stripped.startswith("if __name__")
    )


def _is_indented_section_comment(line: str) -> bool:
    """A col-4 comment line that looks like a section separator."""
    if not line.startswith("    "):
        return False
    return line[4:].startswith("#")


def deindent_trapped_section_separators(lines: List[str]) -> List[str]:
    """
    After class bodies are re-indented, section-separator comments that
    used to sit between classes can end up trapped at col 4 inside the
    previous class body. Walk backward from every col-0 block marker and
    move any immediately-preceding col-4 comment run back to col 0.
    """
    out = list(lines)
    for i, line in enumerate(out):
        if line.startswith(" "):
            continue
        stripped = line.lstrip(" ")
        if not _is_col0_block_marker(stripped):
            continue

        j = i - 1
        candidates = []
        while j >= 0:
            prev = out[j]
            if prev.strip() == "":
                candidates.append(j)
                j -= 1
                continue
            if _is_indented_section_comment(prev):
                candidates.append(j)
                j -= 1
                continue
            break

        has_separator = any(
            _is_indented_section_comment(out[k]) for k in candidates
        )
        if not has_separator:
            continue

        for k in candidates:
            if _is_indented_section_comment(out[k]):
                out[k] = out[k][4:]

    return out


def fix_text(text: str) -> str:
    """Apply every repair pass to a file's text and return the result."""
    text = apply_text_replacements(text)
    lines = text.split("\n")
    lines = fix_line_one(lines)
    lines = remove_bare_code_fences(lines)
    lines = reindent_class_and_function_bodies(lines)
    lines = deindent_trapped_section_separators(lines)
    return "\n".join(lines)


def process_file(path: str, check_only: bool, verbose: bool) -> Tuple[bool, bool]:
    """
    Return (parses, needed_fixing).
    parses       : True if the (possibly fixed) file parses cleanly
    needed_fixing: True if fix_text changed anything
    """
    with open(path, "r", encoding="utf-8") as f:
        original = f.read()

    new_text = fix_text(original)
    changed = new_text != original

    try:
        ast.parse(new_text)
        parses = True
        parse_err = None
    except SyntaxError as e:
        parses = False
        parse_err = str(e)

    if check_only:
        status = "NEEDS FIX" if changed else "clean"
        if not parses:
            status = f"STILL BROKEN: {parse_err}"
        if verbose or changed or not parses:
            print(f"  {path}: {status}")
        return parses, changed

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_text)
        if verbose:
            print(f"  {path}: fixed")
    elif verbose:
        print(f"  {path}: no change")

    if not parses:
        print(f"  {path}: STILL BROKEN after fix: {parse_err}", file=sys.stderr)

    return parses, changed


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Fix markdown-paste artifacts in .py files."
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="Python files to repair.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report whether files need fixing, without modifying them.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print per-file status.",
    )
    args = parser.parse_args(argv)

    all_parse = True
    any_needed_fix = False

    for path in args.files:
        parses, needed_fix = process_file(path, args.check, args.verbose)
        all_parse = all_parse and parses
        any_needed_fix = any_needed_fix or needed_fix

    if args.check:
        return 0 if (all_parse and not any_needed_fix) else 1
    return 0 if all_parse else 1


if __name__ == "__main__":
    sys.exit(main())
