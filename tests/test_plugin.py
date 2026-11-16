"""Offline MCP-only package checks: python3 -m unittest discover -s tests -v."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PluginTests(unittest.TestCase):
    def test_package_identity_and_discovery(self):
        for host in ('claude', 'cursor', 'codex'):
            manifest = json.loads((ROOT / f'.{host}-plugin/plugin.json').read_text())
            self.assertEqual((manifest['name'], manifest['version']), ('restream', '1.2.0'))
            self.assertNotIn('skills', manifest)
            self.assertNotIn('onboardingSkill', manifest)
        self.assertFalse((ROOT / 'skills').exists())
        for host in ('claude', 'cursor'):
            marketplace = json.loads((ROOT / f'.{host}-plugin/marketplace.json').read_text())
            self.assertEqual(marketplace['plugins'][0]['source'], './')
            self.assertEqual(marketplace['plugins'][0]['name'], 'restream')
        codex = json.loads((ROOT / '.agents/plugins/marketplace.json').read_text())
        self.assertEqual(codex['plugins'][0]['source'], {'source': 'local', 'path': './'})

    def test_manifest_resources(self):
        cursor = json.loads((ROOT / '.cursor-plugin/plugin.json').read_text())
        codex = json.loads((ROOT / '.codex-plugin/plugin.json').read_text())
        claude = json.loads((ROOT / '.claude-plugin/plugin.json').read_text())
        resources = [cursor['logo'], cursor['mcpServers'], codex['mcpServers'], claude['icon']]
        resources += [codex['interface'][key] for key in ('logo', 'logoDark', 'composerIcon', 'composerIconDark')]
        for resource in resources:
            self.assertTrue((ROOT / resource).is_file(), resource)

    def test_connector_endpoint(self):
        for filename in ('mcp.json', '.mcp.json'):
            servers = json.loads((ROOT / filename).read_text())['mcpServers']
            self.assertEqual(list(servers), ['restream'])
            self.assertEqual(servers['restream']['url'], 'https://mcp.restream.io/mcp')


if __name__ == '__main__':
    unittest.main()
