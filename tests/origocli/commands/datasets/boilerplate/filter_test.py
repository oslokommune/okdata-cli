from okdata.cli.commands.datasets.boilerplate.config import filter_comma_separated


class TestCommaSeparatedFilter:
    def test_quoted_separator(self):
        filtered = filter_comma_separated('"ab, c","og d')
        assert len(filtered) == 2
        assert filtered[0] == "ab, c"

        filtered = filter_comma_separated(
            r"EUREF89 NTM Sone 22\, 2d + NN54,"
            "http://www.opengis.net/def/crs/EPSG/0/5972,"
            "https://epsg.io/4326"
        )
        assert len(filtered) == 3
        assert filtered[0] == "EUREF89 NTM Sone 22, 2d + NN54"

    def test_initial_space(self):
        filtered = filter_comma_separated('oslo 1, oslo 2, "oslo 3, vestsiden"')
        assert len(filtered) == 3
        assert filtered[2] == "oslo 3, vestsiden"

    def test_escaped_separator(self):
        filtered = filter_comma_separated(r"a\,b, c, og d")
        assert len(filtered) == 3
        assert filtered[0] == "a,b"

        filtered = filter_comma_separated(r'"a\,b", c, og d')
        assert len(filtered) == 3
        assert filtered[0] == "a,b"

        filtered = filter_comma_separated(
            r'"EUREF89 NTM Sone 22, 2d + NN54",'
            "http://www.opengis.net/def/crs/EPSG/0/5972,"
            "https://epsg.io/4326"
        )
        assert len(filtered) == 3
        assert filtered[0] == "EUREF89 NTM Sone 22, 2d + NN54"

    def test_stripping(self):
        filtered = filter_comma_separated(",, ,")
        assert len(filtered) == 0

        filtered = filter_comma_separated(",,a,")
        assert len(filtered) == 1

        filtered = filter_comma_separated(',,"",')
        assert len(filtered) == 0

        filtered = filter_comma_separated(" a,  b  ,")
        assert len(filtered) == 2
        assert filtered[0] == "a"
        assert filtered[1] == "b"
