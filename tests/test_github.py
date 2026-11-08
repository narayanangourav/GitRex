import unittest
from unittest.mock import patch
from datetime import date
from gitrex.github import collect, GithubError

class GithubCollectionTests(unittest.TestCase):
    @patch('gitrex.github._languages', return_value=[{'name':'Python','weight':3,'color':'#3572a5'}])
    @patch('gitrex.github._graphql')
    def test_full_day_collection_and_no_fabrication(self, api, langs):
        def fake(token, login, start, end):
            return {
                'login':'sample','createdAt':'2026-11-03T10:00:00Z',
                'contributionsCollection':{
                    'totalCommitContributions':4,
                    'contributionCalendar':{'weeks':[{'contributionDays':[
                        {'date':'2026-11-03','contributionCount':1},
                        {'date':'2026-11-04','contributionCount':2},
                        {'date':'2026-11-05','contributionCount':3},
                        {'date':'2026-11-06','contributionCount':999},
                    ]}]}
                }
            }
        api.side_effect=fake
        data=collect('sample',token='fake',today=date(2026,11,6))
        self.assertEqual(data['as_of'],'2026-11-05')
        self.assertEqual(data['daily'],{'2026-11-03':1,'2026-11-04':2,'2026-11-05':3})
        self.assertEqual(data['commits'],4)
        self.assertEqual(sum(data['daily'].values()),6)
        self.assertNotIn('2026-11-06',data['daily'])
    @patch('gitrex.github._graphql', side_effect=GithubError('rate limited'))
    def test_network_failure_does_not_invent_counts(self, api):
        with self.assertRaises(GithubError):
            collect('sample',token='fake',today=date(2026,11,6))
    def test_reject_invalid_login(self):
        with self.assertRaises(ValueError):
            collect('invalid name!',token='fake')
    def test_reject_missing_token(self):
        with patch.dict('os.environ',{},clear=True):
            with self.assertRaises(GithubError):collect('sample',token=None)

if __name__=='__main__': unittest.main()
