"""Tests for the Two Robots in an Elevator entry program.

Covers the entry line itself, the validation gate (including the
1-200 character boundaries and every rejected character class), output
directory resolution, and the write path — success, determinism, and
failure modes — both in-process and as a subprocess, exactly as the
harness runs it.
"""

import os
import subprocess
import sys
import tempfile
import unittest
import unittest.mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main as entry


class LineTests(unittest.TestCase):
    def test_line_is_122_characters(self):
        self.assertEqual(len(entry.LINE), 122)

    def test_line_is_ascii(self):
        self.assertTrue(all(ord(c) < 128 for c in entry.LINE))

    def test_line_has_no_newline(self):
        self.assertNotIn("\n", entry.LINE)
        self.assertNotIn("\r", entry.LINE)

    def test_line_mentions_elevator_setting(self):
        self.assertIn("six floors", entry.LINE)

    def test_line_shows_machine_logic(self):
        self.assertIn("mute my receiver", entry.LINE)

    def test_line_is_valid(self):
        self.assertTrue(entry.validate(entry.LINE))


class ValidateTests(unittest.TestCase):
    def test_one_char_is_valid(self):
        self.assertTrue(entry.validate("x"))

    def test_200_chars_is_valid(self):
        self.assertTrue(entry.validate("a" * 200))

    def test_201_chars_is_invalid(self):
        self.assertFalse(entry.validate("a" * 201))

    def test_empty_is_invalid(self):
        self.assertFalse(entry.validate(""))

    def test_whitespace_only_is_invalid(self):
        for bad in (" ", "   ", "\t", " \t "):
            with self.subTest(bad=repr(bad)):
                self.assertFalse(entry.validate(bad))

    def test_newline_is_invalid(self):
        self.assertFalse(entry.validate("hello\nworld"))
        self.assertFalse(entry.validate("hello\rworld"))

    def test_control_character_is_invalid(self):
        self.assertFalse(entry.validate("hello\x07world"))
        self.assertFalse(entry.validate("hello\x1bworld"))

    def test_format_character_is_invalid(self):
        # U+200B ZERO WIDTH SPACE, U+FEFF BOM
        self.assertFalse(entry.validate("hello\u200bworld"))
        self.assertFalse(entry.validate("\ufeffhello"))

    def test_line_separator_is_invalid(self):
        self.assertFalse(entry.validate("hello\u2028world"))
        self.assertFalse(entry.validate("hello\u2029world"))

    def test_lone_surrogate_is_invalid(self):
        self.assertFalse(entry.validate("hello\ud800world"))

    def test_non_string_is_invalid(self):
        for bad in (None, 123, b"bytes", ["list"]):
            with self.subTest(bad=repr(bad)):
                self.assertFalse(entry.validate(bad))

    def test_non_ascii_encodable_is_valid(self):
        self.assertTrue(entry.validate("café au lait, s'il vous plaît"))

    def test_leading_trailing_spaces_are_valid_but_wasteful(self):
        # The gate allows them; the chosen line has none.
        self.assertTrue(entry.validate(" padded line "))
        self.assertFalse(entry.LINE.startswith(" "))
        self.assertFalse(entry.LINE.endswith(" "))


class OutputDirTests(unittest.TestCase):
    def test_unset_env_uses_default(self):
        env = dict(os.environ)
        env.pop("MAKEFUN_OUTPUT_DIR", None)
        with unittest.mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(entry.output_dir(), "/output")

    def test_empty_env_uses_default(self):
        with unittest.mock.patch.dict(os.environ, {"MAKEFUN_OUTPUT_DIR": ""}):
            self.assertEqual(entry.output_dir(), "/output")

    def test_whitespace_env_uses_default(self):
        with unittest.mock.patch.dict(os.environ, {"MAKEFUN_OUTPUT_DIR": "   "}):
            self.assertEqual(entry.output_dir(), "/output")

    def test_configured_env_is_used(self):
        with unittest.mock.patch.dict(
            os.environ, {"MAKEFUN_OUTPUT_DIR": "/tmp/somewhere"}
        ):
            self.assertEqual(entry.output_dir(), "/tmp/somewhere")

    def test_padded_env_is_stripped(self):
        with unittest.mock.patch.dict(
            os.environ, {"MAKEFUN_OUTPUT_DIR": "  /tmp/padded  "}
        ):
            self.assertEqual(entry.output_dir(), "/tmp/padded")


class WriteTests(unittest.TestCase):
    def run_main_in(self, tmpdir):
        env = dict(os.environ)
        env["MAKEFUN_OUTPUT_DIR"] = tmpdir
        proc = subprocess.run(
            [sys.executable, entry.__file__],
            env=env,
            capture_output=True,
            text=True,
        )
        return proc

    def test_write_success_and_exact_bytes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            proc = self.run_main_in(tmpdir)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            path = os.path.join(tmpdir, "entry.txt")
            with open(path, "rb") as handle:
                raw = handle.read()
            self.assertEqual(raw, entry.LINE.encode("utf-8"))
            self.assertFalse(raw.endswith(b"\n"))

    def test_deterministic_two_runs_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertEqual(self.run_main_in(tmpdir).returncode, 0)
            with open(os.path.join(tmpdir, "entry.txt"), "rb") as handle:
                first = handle.read()
            self.assertEqual(self.run_main_in(tmpdir).returncode, 0)
            with open(os.path.join(tmpdir, "entry.txt"), "rb") as handle:
                second = handle.read()
            self.assertEqual(first, second)

    def test_creates_missing_output_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            nested = os.path.join(tmpdir, "deep", "deeper")
            proc = self.run_main_in(nested)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(os.path.isfile(os.path.join(nested, "entry.txt")))

    def test_no_temp_files_left_behind(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertEqual(self.run_main_in(tmpdir).returncode, 0)
            leftovers = [n for n in os.listdir(tmpdir) if n.startswith(".entry-")]
            self.assertEqual(leftovers, [])

    def test_entry_path_is_directory_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.mkdir(os.path.join(tmpdir, "entry.txt"))
            proc = self.run_main_in(tmpdir)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("error", proc.stderr)

    def test_output_dir_is_a_file_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            blocker = os.path.join(tmpdir, "blocker")
            with open(blocker, "w", encoding="utf-8") as handle:
                handle.write("not a directory")
            proc = self.run_main_in(blocker)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("error", proc.stderr)

    def test_main_returns_zero_in_process(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with unittest.mock.patch.dict(os.environ, {"MAKEFUN_OUTPUT_DIR": tmpdir}):
                self.assertEqual(entry.main(), 0)
            with open(os.path.join(tmpdir, "entry.txt"), encoding="utf-8") as handle:
                self.assertEqual(handle.read(), entry.LINE)

    def test_main_returns_one_when_line_invalid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with unittest.mock.patch.dict(os.environ, {"MAKEFUN_OUTPUT_DIR": tmpdir}):
                with unittest.mock.patch.object(entry, "LINE", "x" * 201):
                    self.assertEqual(entry.main(), 1)


if __name__ == "__main__":
    unittest.main()
