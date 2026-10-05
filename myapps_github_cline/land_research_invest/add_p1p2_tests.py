"""Append P1+P2 tests to test_scoring_service.py"""
path = r'c:\__TESTAUTOMATION\SCRIPTS\PYTHON\myapps_github_cline\land_research_invest\tests\test_scoring_service.py'

new_tests = '''

class TestPrelimScoringP1SuspiciousPrice:
    """P1: Inzeratovy portal + ppsm < 1.5 EUR/m2 -> ppsm_score=0 (penalizacia)."""

    def _p(self, source='nehnutelnosti_sk', price=200.0, area=700.0, ppsm=0.0):
        p = Parcel(url='http://t.sk/1', price_eur=price, area_sqm=area,
                   source_portal=source, price_per_sqm=ppsm)
        return p

    def test_inzerat_very_low_ppsm_penalized(self):
        # Bratislava Ruzinov za 0.14 EUR/m2 - parsovacia chyba
        p1 = self._p(source='reality_sk', price=100.0, area=733.0, ppsm=0.14)
        s_suspicious = preliminary_score(p1).preliminary_score
        # Normal parcel (same portal, realistic price)
        p2 = self._p(source='reality_sk', price=10000.0, area=700.0, ppsm=14.28)
        s_normal = preliminary_score(p2).preliminary_score
        assert s_suspicious < s_normal

    def test_inzerat_low_ppsm_below_threshold_penalized(self):
        p = self._p(source='nehnutelnosti_sk', price=270.0, area=470.0, ppsm=0.57)
        preliminary_score(p)
        # With ppsm_score=0 and low total price, should not be STRONG BUY
        assert p.prelim_recommendation in ('CONSIDER', 'SKIP', 'INVESTIGATE')

    def test_drazba_low_ppsm_not_penalized(self):
        # Drazba (exekucia) moze mat legitimne nizku cenu
        p_d = self._p(source='ske_drazobne_vyhlasky', price=69.0, area=740.0, ppsm=0.09)
        s_drazba = preliminary_score(p_d).preliminary_score
        # Inzerat s rovnakou cenou - penalizovany
        p_i = self._p(source='nehnutelnosti_sk', price=69.0, area=740.0, ppsm=0.09)
        s_inzerat = preliminary_score(p_i).preliminary_score
        assert s_drazba > s_inzerat

    def test_inzerat_ppsm_above_threshold_not_penalized(self):
        # 2.0 EUR/m2 je nad pragom -> normalne skore
        p_above = self._p(source='nehnutelnosti_sk', price=1400.0, area=700.0, ppsm=2.0)
        s_above = preliminary_score(p_above).preliminary_score
        p_below = self._p(source='nehnutelnosti_sk', price=1400.0, area=700.0, ppsm=1.4)
        s_below = preliminary_score(p_below).preliminary_score
        assert s_above > s_below

    def test_suspicious_threshold_value(self):
        assert _SUSPICIOUS_PPSM_THRESHOLD == 1.5

    def test_inzerat_sources_set(self):
        assert 'nehnutelnosti_sk' in _INZERAT_SOURCES
        assert 'topreality_sk' in _INZERAT_SOURCES
        assert 'reality_sk' in _INZERAT_SOURCES
        assert 'ske_drazobne_vyhlasky' not in _INZERAT_SOURCES

    def test_ppsm_zero_not_suspicious(self):
        # ppsm=0 = neznama cena -> neutral (nie suspicious)
        p = self._p(source='nehnutelnosti_sk', price=0.0, area=700.0, ppsm=0.0)
        preliminary_score(p)
        # Must not crash, score must be in range
        assert 0.0 <= p.preliminary_score <= 100.0


class TestPrelimScoringP2DistanceEstimate:
    """P2: Odhad vzdialenosti od BA z location_text -> penalizacia za vzdialene."""

    def _p(self, location='Bratislava Raca', source='ske_drazobne_vyhlasky',
           price=5000.0, area=600.0):
        p = Parcel(url='http://t.sk/1', price_eur=price, area_sqm=area,
                   source_portal=source, location_text=location)
        return p

    def test_ba_scores_higher_than_kosice(self):
        p_ba = self._p(location='raca')
        p_ke = Parcel(url='http://t.sk/2', price_eur=5000.0, area_sqm=600.0,
                      source_portal='ske_drazobne_vyhlasky', location_text='kosice')
        s_ba = preliminary_score(p_ba).preliminary_score
        s_ke = preliminary_score(p_ke).preliminary_score
        assert s_ba > s_ke

    def test_sta_lubovna_lower_than_senec(self):
        p_sl = self._p(location='stara lubovna')
        p_se = Parcel(url='http://t.sk/3', price_eur=5000.0, area_sqm=600.0,
                      source_portal='ske_drazobne_vyhlasky', location_text='senec')
        s_sl = preliminary_score(p_sl).preliminary_score
        s_se = preliminary_score(p_se).preliminary_score
        assert s_sl < s_se

    def test_estimate_distance_ba(self):
        d = _estimate_distance_km('bratislava')
        assert d is not None
        assert d < 5.0

    def test_estimate_distance_senec(self):
        d = _estimate_distance_km('senec')
        assert d is not None
        assert 20.0 < d < 40.0

    def test_estimate_distance_kosice(self):
        d = _estimate_distance_km('kosice')
        assert d is not None
        assert d > 300.0

    def test_estimate_distance_unknown_returns_none(self):
        d = _estimate_distance_km('xyzneznama999')
        assert d is None

    def test_estimate_distance_empty_returns_none(self):
        assert _estimate_distance_km('') is None

    def test_partial_match_bratislava_raca(self):
        d = _estimate_distance_km('Bratislava Raca')
        assert d is not None
        assert d < 15.0

    def test_unknown_location_gets_neutral_dist_score(self):
        p = self._p(location='NeznameBohumMesto')
        preliminary_score(p)
        assert 0.0 <= p.preliminary_score <= 100.0

    def test_no_location_text_safe(self):
        p = Parcel(url='http://t.sk/4', price_eur=5000.0, area_sqm=600.0,
                   source_portal='ske_drazobne_vyhlasky')
        preliminary_score(p)
        assert 0.0 <= p.preliminary_score <= 100.0
'''

with open(path, encoding='utf-8') as f:
    content = f.read()

content = content.rstrip() + new_tests
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('P1+P2 tests appended OK — total lines:', content.count('\n'))
