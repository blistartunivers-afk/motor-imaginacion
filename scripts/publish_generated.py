"""Publish generated data only after real required checks have passed on its SHA."""
import json
import os
import subprocess
import time


def publish(repository: str, run_id: str, default_branch: str, *,
            command=subprocess.check_output, sleep=time.sleep, clock=time.monotonic) -> None:
    def run(*args):
        return command(list(args), text=True).strip()
    sha = run('git', 'rev-parse', 'HEAD')
    parent = run('git', 'rev-parse', 'HEAD^')
    candidate = 'generated/gallery-' + run_id
    run('git', 'push', 'origin', f'HEAD:refs/heads/{candidate}')
    # workflow_dispatch is deliberately triggered: ordinary GITHUB_TOKEN pushes
    # do not start other workflows. No status is fabricated by this publisher.
    for workflow in ('audit-regressions.yml', 'pin-actions.yml'):
        run('gh', 'workflow', 'run', workflow, '--repo', repository, '--ref', candidate)
    required = {'Audit regressions', 'Pin Actions'}
    deadline = clock() + 1200
    while clock() < deadline:
        data = json.loads(run('gh', 'api', f'repos/{repository}/commits/{sha}/check-runs?per_page=100'))
        # GitHub returns newest check runs first. Accept only its Actions app.
        checks = {}
        for item in data['check_runs']:
            name = item['name']
            if name in required and item.get('app', {}).get('slug') == 'github-actions':
                checks.setdefault(name, item)
        if any(v['status'] == 'completed' and v.get('conclusion') != 'success' for v in checks.values()):
            raise RuntimeError('Required verification failed; candidate retained, default branch unchanged')
        if required <= checks.keys() and all(v['status'] == 'completed' and v.get('conclusion') == 'success' for v in checks.values()):
            break
        sleep(10)
    else:
        raise TimeoutError('Verification timed out; candidate retained, default branch unchanged')
    remote = run('git', 'ls-remote', 'origin', f'refs/heads/{default_branch}').split()[0]
    if remote != parent:
        raise RuntimeError('Default branch advanced; candidate retained for review, no force push')
    run('git', 'push', 'origin', f'HEAD:refs/heads/{default_branch}')


if __name__ == '__main__':
    publish(os.environ['GITHUB_REPOSITORY'], os.environ['GITHUB_RUN_ID'],
            os.environ.get('GALLERY_DEFAULT_BRANCH', 'master'))
