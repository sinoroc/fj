#

"""Unit tests."""

import unittest

import fj


class TestProjectVersion(unittest.TestCase):
    """Project version string."""

    def test_project_has_version_string(self) -> None:
        """Project should have a version string."""
        self.assertIn('__version__', dir(fj))
        self.assertIsInstance(fj.__version__, str)


class TestParseDistributionExtras(unittest.TestCase):
    """Parse distribution and extras."""

    def test_parse_distribution_path(self) -> None:
        """Parse distribution path."""
        candidate_makers = [
            # pylint: disable=protected-access
            fj._solver._sdist.SdistCandidateMaker(),
            fj._solver._wheel.WheelCandidateMaker(),
        ]
        parser = (
            # pylint: disable=protected-access
            fj._solver.parser.DirectUriRequirementParser(candidate_makers)
        )
        parse_uri_and_extras = (
            # pylint: disable=protected-access
            parser._parse_uri_and_extras
        )
        #
        test_items = [
            (
                '/path/to/Thing-0.0.0.dev0.tar.gz[test,dev]',
                (
                    'file:///path/to/Thing-0.0.0.dev0.tar.gz',
                    {
                        'dev',
                        'test',
                    },
                ),
            ),
            (
                '/path/to/Thing-0.0.0.dev0.tar.gz',
                (
                    'file:///path/to/Thing-0.0.0.dev0.tar.gz',
                    set(),
                ),
            ),
            (
                '/path/to/Thing-0.0.0.dev0-py3-none-any.whl',
                (
                    'file:///path/to/Thing-0.0.0.dev0-py3-none-any.whl',
                    set(),
                ),
            ),
            (
                'https://a.invalid/Thing-0.0.0.dev0-py3-none-any.whl',
                (
                    'https://a.invalid/Thing-0.0.0.dev0-py3-none-any.whl',
                    set(),
                ),
            ),
            (
                'https://a.invalid/Thing-0.0.0.dev0-py3-none-any.whl[dev]',
                (
                    'https://a.invalid/Thing-0.0.0.dev0-py3-none-any.whl',
                    {
                        'dev',
                    },
                ),
            ),
        ]
        #
        for test_item in test_items:
            with self.subTest(test_item=test_item):
                uri_str, extras = parse_uri_and_extras(test_item[0])
                self.assertEqual(test_item[1][0], uri_str)
                self.assertEqual(test_item[1][1], extras)


# EOF
