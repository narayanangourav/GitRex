import copy
import unittest
from gitrex.model import derive, streaks, validate_snapshot

BASE={'login':'sample','as_of':'2026-11-05','daily':{},'commits':0,'languages':[]}

class ProgressionTests(unittest.TestCase):
    def sample(self, n):
        s=copy.deepcopy(BASE)
        s['daily']={'2026-11-05':n}
        s['commits']=n
        return s
    def test_five_stages(self):
        for count, stage in [(0,'Hatchling'),(49,'Hatchling'),(50,'Juvenile'),
                             (199,'Juvenile'),(200,'Subadult'),(499,'Subadult'),
                             (500,'Adult'),(999,'Adult'),(1000,'Apex Rex')]:
            with self.subTest(count=count):
                self.assertEqual(derive(self.sample(count)).stage,stage)
    def test_growth_monotonic(self):
        self.assertTrue(all(derive(self.sample(i)).scale < derive(self.sample(i+1)).scale
                            for i in [0,10,49,50,199,200,499,500,999]))
    def test_growth_caps_at_one(self):
        self.assertEqual(derive(self.sample(10000)).scale,1.0)
    def test_streaks(self):
        d={'2026-11-01':1,'2026-11-02':3,'2026-11-04':2,'2026-11-05':4}
        self.assertEqual(streaks(d,'2026-11-05'),(2,2))
        self.assertEqual(streaks(d,'2026-11-06'),(0,2))
    def test_behavior(self):
        self.assertEqual(derive(self.sample(0)).behavior,'idle')
        self.assertEqual(derive(self.sample(1)).behavior,'walk')
        self.assertEqual(derive(self.sample(5)).behavior,'roar')
    def test_malformed_count(self):
        bad=self.sample(1); bad['daily']['2026-11-05']=-1
        with self.assertRaises(ValueError): validate_snapshot(bad)
    def test_ignore_future_days(self):
        s=self.sample(1); s['daily']['2026-11-06']=100
        self.assertEqual(derive(s).contributions,1)
    def test_no_duplicate_growth_across_renders(self):
        s=self.sample(10)
        self.assertEqual(derive(s),derive(s))

if __name__=='__main__':unittest.main()
