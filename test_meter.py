"""Run with Python 3: python -m unittest -v test_meter.py"""
import importlib.util
import json
from pathlib import Path
import tempfile
import time
import unittest

spec = importlib.util.spec_from_file_location('meter', Path(__file__).parent / 'netmeter-traffic/src/meter.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class Tests(unittest.TestCase):
    def test_counter_columns(self):
        self.assertEqual(m.counters('Inter-| Receive | Transmit\n eth0: 100 1 2 3 4 5 6 7 200 9 10 11 12 13 14 15'), {'eth0': (100, 200)})

    def test_mbps_and_reset(self):
        self.assertEqual(m.rate((0, 100), (250000, 500100), 2), [1, 2])
        self.assertIsNone(m.rate((100, 200), (0, 300), 2))
        self.assertIsNone(m.rate(None, (100, 200), 2))

    def test_route_metric_and_manual_override(self):
        routes = 'Iface Destination Gateway Flags RefCnt Use Metric Mask\nwlan0 00000000 01000000 0003 0 0 600 00000000\neth0 00000000 01000000 0003 0 0 100 00000000'
        available = {'eth0': (0, 0), 'wlan0': (0, 0)}
        self.assertEqual(m.select_interface('auto', routes, available), 'eth0')
        self.assertEqual(m.select_interface('wlan0', routes, available), 'wlan0')
        with self.assertRaises(ValueError):
            m.select_interface('missing', routes, available)
        with self.assertRaises(ValueError):
            m.select_interface('auto', '', available)

    def test_stale_missing_and_widget_contract(self):
        old = m.STATE
        try:
            with tempfile.TemporaryDirectory() as folder:
                m.STATE = Path(folder) / 'traffic.json'
                self.assertIsNone(m.read_snapshot()['rates'])
                data = dict(timestamp=time.time()-15, rates=[1, 2], interface='eth0', interfaces=['eth0'], status='OK')
                m.STATE.write_text(json.dumps(data))
                self.assertIsNone(m.read_snapshot()['rates'])
                data['timestamp'] = time.time()
                m.STATE.write_text(json.dumps(data))
                w = m.widget(m.read_snapshot())
                self.assertEqual(w['type'], 'three-stats')
                self.assertEqual(w['refresh'], '2s')
                self.assertEqual(w['items'][0]['text'], '1.00 Mbps')
                self.assertEqual(w['items'][1]['text'], '2.00 Mbps')
        finally:
            m.STATE = old


if __name__ == '__main__':
    unittest.main()
