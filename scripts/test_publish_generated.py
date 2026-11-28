import json
import unittest
from publish_generated import publish

class PublisherTests(unittest.TestCase):
    def simulate(self, conclusion='success', remote='parent'):
        calls = []
        def command(args, **kwargs):
            calls.append(args)
            if args[:3] == ['git', 'rev-parse', 'HEAD']: return 'candidate\n'
            if args[:3] == ['git', 'rev-parse', 'HEAD^']: return 'parent\n'
            if args[:2] == ['git', 'ls-remote']: return remote+' refs/heads/master\n'
            if args[:2] == ['gh', 'api']:
                return json.dumps({'check_runs':[{'name':n,'status':'completed','conclusion':conclusion,
                                  'app':{'slug':'github-actions'}} for n in ('Audit regressions','Pin Actions')]})
            return ''
        return calls, command
    def test_publishes_only_after_verified_sha(self):
        calls, command = self.simulate()
        publish('owner/repo', '123', 'master', command=command)
        self.assertEqual(calls[-1], ['git','push','origin','HEAD:refs/heads/master'])
        self.assertEqual(sum(c[:3] == ['gh','workflow','run'] for c in calls),2)
        self.assertTrue(any(c[:2] == ['gh','api'] for c in calls))
    def test_failure_does_not_publish_default(self):
        calls, command = self.simulate(conclusion='failure')
        with self.assertRaises(RuntimeError): publish('owner/repo','123','master',command=command)
        self.assertNotIn(['git','push','origin','HEAD:refs/heads/master'], calls)
    def test_concurrent_default_change_does_not_force_push(self):
        calls, command = self.simulate(remote='new-parent')
        with self.assertRaises(RuntimeError): publish('owner/repo','123','master',command=command)
        self.assertNotIn(['git','push','origin','HEAD:refs/heads/master'], calls)

if __name__ == '__main__': unittest.main()
