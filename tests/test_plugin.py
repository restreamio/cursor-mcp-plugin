"""Offline package and helper smoke checks: python3 -m unittest discover -s tests -v."""
import ast
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PluginTests(unittest.TestCase):
    def run_helper(self, relative, *args, stdin=None, expected=0):
        result = subprocess.run(
            [sys.executable, str(ROOT / 'skills' / relative), *map(str, args)],
            input=stdin, text=True, capture_output=True,
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result.stdout

    def test_package_identity_and_discovery(self):
        for host in ('claude', 'cursor', 'codex'):
            manifest = json.loads((ROOT / f'.{host}-plugin/plugin.json').read_text())
            self.assertEqual((manifest['name'], manifest['version']), ('restream', '1.1.0'))
        cursor = json.loads((ROOT / '.cursor-plugin/plugin.json').read_text())
        self.assertNotIn('skills', cursor)  # Preserve automatic skills/ discovery.
        self.assertTrue((ROOT / cursor['logo']).is_file())
        for host in ('claude', 'cursor'):
            marketplace = json.loads((ROOT / f'.{host}-plugin/marketplace.json').read_text())
            self.assertEqual(marketplace['plugins'][0]['source'], './')
            self.assertEqual(marketplace['plugins'][0]['name'], 'restream')
        self.assertEqual(len(list((ROOT / 'skills').glob('*/SKILL.md'))), 16)

    def test_connector_endpoint(self):
        for filename in ('mcp.json', '.mcp.json'):
            servers = json.loads((ROOT / filename).read_text())['mcpServers']
            self.assertEqual(list(servers), ['restream'])
            self.assertEqual(servers['restream']['url'], 'https://mcp.restream.io/mcp')

    def test_json_and_python_syntax(self):
        for path in ROOT.rglob('*.json'):
            if '.git' not in path.parts:
                json.loads(path.read_text())
        for path in (ROOT / 'skills').rglob('*.py'):
            ast.parse(path.read_text(), filename=str(path))

    def test_title_counts_unicode_bytes(self):
        data = json.loads(self.run_helper('restream-preflight-stream/scripts/count_title.py', stdin='😀' * 9))
        self.assertEqual(data['characters'], 9)
        self.assertEqual(data['utf8Bytes'], 36)
        self.assertFalse(data['fitsTikTok32Bytes'])
        self.assertEqual(data['first32BytesCut'], '😀' * 8)

    def test_chapters_accept_valid_and_reject_out_of_order(self):
        helper = 'restream-write-show-notes/scripts/check_chapters.py'
        self.run_helper(helper, '-', '--duration', '1:00', stdin='0:00 Intro\n0:20 Topic\n0:40 End\n')
        self.run_helper(helper, '-', stdin='0:00 Intro\n0:40 Topic\n0:20 End\n', expected=1)

    def test_caption_conversion_and_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'sample.txt'
            source.write_text('00:00:00 [Speaker 1]\nHello everyone.\n\n00:00:05 [Speaker 2]\nWelcome to the show.\n')
            helper = 'restream-export-files/scripts/to_captions.py'
            self.run_helper(helper, 'convert', source, '--out-dir', directory, '--format', 'both')
            for extension in ('srt', 'vtt'):
                outputs = list(Path(directory).glob(f'*.{extension}'))
                self.assertEqual(len(outputs), 1)
                self.assertIn('Hello everyone.', outputs[0].read_text())
                self.run_helper(helper, 'check', outputs[0])

    def test_card_html_escapes_content(self):
        with tempfile.TemporaryDirectory() as directory:
            spec = Path(directory) / 'spec.json'
            spec.write_text(json.dumps({'cards': [{'type': 'quote', 'headline': '<script>alert(1)</script>'}]}))
            output = Path(directory) / 'cards'
            result = json.loads(self.run_helper('restream-render-cards/scripts/render_cards.py', spec, output, '--html-only'))
            self.assertEqual(result['reason'], 'html_requested')
            html = (output / 'cards.html').read_text()
            self.assertNotIn('<script>alert(1)</script>', html)
            self.assertIn('&lt;script&gt;', html)

    def test_route_catalog_is_available(self):
        result = json.loads(self.run_helper('restream-fix-my-stream/scripts/lookup_route.py', '--list'))
        self.assertGreater(len(result['entries']), 0)


if __name__ == '__main__':
    unittest.main()
