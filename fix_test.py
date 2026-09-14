import pathlib
p = pathlib.Path(r'C:\__TESTAUTOMATION\SCRIPTS\PYTHON\myapps_github_cline\land_research_invest\tests\test_scraper_service.py')
lines = p.read_text(encoding='utf-8').splitlines(keepends=True)
new = []
for i, line in enumerate(lines):
    if i == 156:  # def test_get_registered_scrapers_returns_list(self):
        new.append(line)
        new.append('        assert isinstance(get_registered_scrapers(), list)\n')
        new.append('\n')
        new.append('    def test_get_registered_scrapers_contains_nehnutelnosti(self):\n')
        new.append('        assert "nehnutelnosti_sk" in get_registered_scrapers()\n')
    elif i in (157, 158):  # blank lines (broken body)
        pass  # skip
    else:
        new.append(line)
p.write_text(''.join(new), encoding='utf-8')
print('OK', len(new), 'lines')
