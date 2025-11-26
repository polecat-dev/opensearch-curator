"""Test setup"""

# pylint: disable=C0115, C0116
import logging
import os
import random
import shutil
import string
import sys
import tempfile
import time
import json
import warnings
from datetime import timedelta, datetime, date, timezone
from subprocess import Popen, PIPE
from unittest import SkipTest, TestCase
from opensearchpy import OpenSearch
from opensearchpy.exceptions import ConnectionError as ESConnectionError
from opensearchpy.exceptions import OpenSearchWarning, NotFoundError, TransportError
from click import testing as clicktest
from opensearch_client.utils import get_version
from curator.cli import cli

from . import testvars


client = None

DATEMAP = {
    'months': '%Y.%m',
    'weeks': '%Y.%W',
    'days': '%Y.%m.%d',
    'hours': '%Y.%m.%d.%H',
}

HOST = os.environ.get('TEST_ES_SERVER', 'http://127.0.0.1:9200')
USERNAME = os.environ.get('TEST_ES_USERNAME', 'admin')
PASSWORD = os.environ.get('TEST_ES_PASSWORD') or os.environ.get(
    'OPENSEARCH_INITIAL_ADMIN_PASSWORD'
)
CA_CERT_PATH = os.environ.get('TEST_ES_CA_CERT')
VERIFY_ENV = os.environ.get('TEST_ES_VERIFY_CERTS')


def _env_bool(value, default):
    if value is None:
        return default
    lowered = value.strip().lower()
    if lowered in ('1', 'true', 'yes', 'on'):
        return True
    if lowered in ('0', 'false', 'no', 'off'):
        return False
    return default


def _should_verify(host):
    default_verify = (
        host.startswith('https://') and CA_CERT_PATH and os.path.exists(CA_CERT_PATH)
    )
    return _env_bool(VERIFY_ENV, bool(default_verify))


VERIFY_CERTS = _should_verify(HOST)
RESOLVED_CA_CERT = (
    CA_CERT_PATH
    if CA_CERT_PATH and os.path.exists(CA_CERT_PATH) and VERIFY_CERTS
    else None
)
HTTP_AUTH = (USERNAME, PASSWORD) if USERNAME and PASSWORD else None


def random_directory():
    dirname = ''.join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(8)
    )
    directory = tempfile.mkdtemp(suffix=dirname)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory


def get_client():
    # pylint: disable=global-statement, invalid-name
    global client
    if client is not None:
        return client

    client = OpenSearch(
        hosts=HOST,
        http_auth=HTTP_AUTH,
        verify_certs=VERIFY_CERTS,
        ca_certs=RESOLVED_CA_CERT,
        request_timeout=300,
        ssl_show_warn=False,
    )

    # Verify connection - opensearch-py 3.0
    for _ in range(100):
        time.sleep(0.1)
        try:
            # Just check if cluster responds - no wait_for_status needed if already healthy
            client.cluster.health()
            return client
        except ESConnectionError:
            continue
    # timeout
    raise SkipTest("OpenSearch failed to start.")


def setup():
    get_client()


class Args(dict):
    def __getattr__(self, att_name):
        return self.get(att_name, None)


class CuratorTestCase(TestCase):
    def setUp(self):
        super(CuratorTestCase, self).setUp()
        self.logger = logging.getLogger('CuratorTestCase.setUp')
        self.client = get_client()

        args = {}
        args['HOST'] = HOST
        args['time_unit'] = 'days'
        args['prefix'] = 'logstash-'
        self.args = args
        # dirname = ''.join(random.choice(string.ascii_uppercase + string.digits)
        #   for _ in range(8))
        # This will create a psuedo-random temporary directory on the machine
        # which runs the unit tests, but NOT on the machine where elasticsearch
        # is running. This means tests may fail if run against remote instances
        # unless you explicitly set `self.args['location']` to a proper spot
        # on the target machine.
        # self.args['location'] = random_directory()
        nodesinfo = self.client.nodes.info()
        nodename = list(nodesinfo['nodes'].keys())[0]
        if 'repo' in nodesinfo['nodes'][nodename]['settings']['path']:
            if isinstance(
                nodesinfo['nodes'][nodename]['settings']['path']['repo'], list
            ):
                self.args['location'] = nodesinfo['nodes'][nodename]['settings'][
                    'path'
                ]['repo'][0]
            else:
                self.args['location'] = nodesinfo['nodes'][nodename]['settings'][
                    'path'
                ]['repo']
        else:  # Use a random directory if repo is not specified, but log it
            self.logger.warning('path.repo is not configured!')
            self.args['location'] = random_directory()
        self.args['configdir'] = random_directory()
        self.args['configfile'] = os.path.join(self.args['configdir'], 'curator.yml')
        self.args['actionfile'] = os.path.join(self.args['configdir'], 'actions.yml')
        self.args['repository'] = 'test_repository'
        # if not os.path.exists(self.args['location']):
        #     os.makedirs(self.args['location'])
        self.logger.debug('setUp completed...')
        self.runner = clicktest.CliRunner()
        self.runner_args = [
            '--config',
            self.args['configfile'],
            self.args['actionfile'],
        ]
        self.result = None

    def get_version(self):
        return get_version(self.client)

    def tearDown(self):
        self.logger = logging.getLogger('CuratorTestCase.tearDown')
        self.logger.debug('tearDown initiated...')
        # re-enable shard allocation for next tests
        enable_allocation = json.loads('{"cluster.routing.allocation.enable":null}')
        self.client.cluster.put_settings(body={'transient': enable_allocation})
        self.delete_repositories()
        # 8.0 removes our ability to purge with wildcards...
        # OpenSearchWarning: this request accesses system indices: [.tasks],
        # but in a future major version, direct access to system indices will be
        # prevented by default
        warnings.filterwarnings("ignore", category=OpenSearchWarning)
        indices = list(
            self.client.indices.get(index="*", expand_wildcards='open,closed').keys()
        )
        if len(indices) > 0:
            # OpenSearchWarning: this request accesses system indices: [.tasks],
            # but in a future major version, direct access to system indices will be
            # prevented by default
            warnings.filterwarnings("ignore", category=OpenSearchWarning)
            self.client.indices.delete(index=','.join(indices))
        for path_arg in ['location', 'configdir']:
            if path_arg in self.args and os.path.exists(self.args[path_arg]):
                # Don't try to delete /tmp or other system directories
                # Only delete if it's a temporary directory we created
                path = self.args[path_arg]
                if path.startswith('/tmp/tmp') or path.startswith(
                    tempfile.gettempdir()
                ):
                    try:
                        shutil.rmtree(path)
                    except (PermissionError, OSError) as e:
                        # Ignore cleanup errors in CI environments
                        warnings.warn(f"Could not clean up {path}: {e}")

    def parse_args(self):
        return Args(self.args)

    def create_indices(self, count, unit=None, ilm_policy=None):
        now = datetime.now(timezone.utc)
        unit = unit if unit else self.args['time_unit']
        fmt = DATEMAP[unit]
        if not unit == 'months':
            step = timedelta(**{unit: 1})
            for _ in range(count):
                self.create_index(
                    self.args['prefix'] + now.strftime(fmt),
                    wait_for_yellow=False,
                    ilm_policy=ilm_policy,
                )
                now -= step
        else:  # months
            now = date.today()
            d = date(now.year, now.month, 1)
            self.create_index(
                self.args['prefix'] + now.strftime(fmt),
                wait_for_yellow=False,
                ilm_policy=ilm_policy,
            )

            for _ in range(1, count):
                if d.month == 1:
                    d = date(d.year - 1, 12, 1)
                else:
                    d = date(d.year, d.month - 1, 1)
                self.create_index(
                    self.args['prefix'] + datetime(d.year, d.month, 1).strftime(fmt),
                    wait_for_yellow=False,
                    ilm_policy=ilm_policy,
                )
        # opensearch-py 3.0: Just verify cluster is responsive
        self.client.cluster.health()

    def wfy(self):
        # opensearch-py 3.0: Just verify cluster is responsive
        self.client.cluster.health()

    def create_index(
        self,
        name,
        shards=1,
        wait_for_yellow=True,
        ilm_policy=None,
        wait_for_active_shards=1,
    ):
        request_body = {'index': {'number_of_shards': shards, 'number_of_replicas': 0}}
        if ilm_policy is not None:
            request_body['index']['lifecycle'] = {'name': ilm_policy}
        # OpenSearchWarning: index name [.shouldbehidden] starts with a dot '.',
        # in the next major version, index names starting with a dot are reserved
        # for hidden indices and system indices
        warnings.filterwarnings("ignore", category=OpenSearchWarning)
        self.client.indices.create(
            index=name,
            body={'settings': request_body},
            params={'wait_for_active_shards': wait_for_active_shards},
        )
        if wait_for_yellow:
            self.wfy()

    def add_docs(self, idx):
        for i in ["1", "2", "3"]:
            self.client.create(index=idx, id=i, body={"doc" + i: 'TEST DOCUMENT'})
            # This should force each doc to be in its own segment.
            # pylint: disable=E1123
            self.client.indices.flush(index=idx, force=True)
            self.client.indices.refresh(index=idx)

    def create_snapshot(self, name, csv_indices):
        self.create_repository()
        # opensearch-py 3.0: snapshot parameters go in body dict, wait_for_completion in params
        self.client.snapshot.create(
            repository=self.args['repository'],
            snapshot=name,
            body={
                'ignore_unavailable': False,
                'include_global_state': True,
                'partial': False,
                'indices': csv_indices,
            },
            params={'wait_for_completion': 'true'},
        )

    def delete_snapshot(self, name):
        try:
            self.client.snapshot.delete(
                repository=self.args['repository'], snapshot=name
            )
        except NotFoundError:
            pass

    def create_repository(self):
        request_body = {'type': 'fs', 'settings': {'location': self.args['location']}}
        try:
            self.client.snapshot.create_repository(
                repository=self.args['repository'], body=request_body
            )
        except TransportError as err:
            error_info = getattr(err, 'info', {}) or {}
            reason = ''
            if isinstance(error_info, dict):
                reason = (
                    error_info.get('error', {})
                    if isinstance(error_info.get('error'), dict)
                    else ''
                )
            message = str(err) if not reason else str(reason)
            if 'path.repo' in message:
                raise SkipTest('path.repo is not configured on the cluster.') from err
            raise

    def delete_repositories(self):
        result = []
        try:
            result = self.client.snapshot.get_repository(repository='*')
        except NotFoundError:
            pass
        for repo in result:
            try:
                cleanup = self.client.snapshot.get(repository=repo, snapshot='*')
            except NotFoundError:
                # Repository exists but has no snapshots - this is OK
                cleanup = {'snapshots': []}
            # pylint: disable=broad-except
            except Exception as exc:
                print(f"Warning: Could not get snapshots for repo {repo}: {exc}")
                cleanup = {'snapshots': []}
            for listitem in cleanup['snapshots']:
                # Delete snapshot from the specific repository, not self.args['repository']
                try:
                    self.client.snapshot.delete(
                        repository=repo, snapshot=listitem['snapshot']
                    )
                except NotFoundError:
                    pass
            self.client.snapshot.delete_repository(repository=repo)

    def close_index(self, name):
        self.client.indices.close(index=name)

    def write_config(self, fname, data):
        with open(fname, 'w', encoding='utf-8') as fhandle:
            fhandle.write(data)

    def get_runner_args(self):
        self.write_config(self.args['configfile'], testvars.client_config.format(HOST))
        runner = os.path.join(os.getcwd(), 'run_singleton.py')
        return [sys.executable, runner]

    def run_subprocess(self, args, logname='subprocess'):
        local_logger = logging.getLogger(logname)
        p = Popen(args, stderr=PIPE, stdout=PIPE)
        stdout, stderr = p.communicate()
        local_logger.debug('STDOUT = %s', stdout.decode('utf-8'))
        local_logger.debug('STDERR = %s', stderr.decode('utf-8'))
        return p.returncode

    def invoke_runner(self, dry_run=False):
        if dry_run:
            self.result = self.runner.invoke(
                cli,
                [
                    '--config',
                    self.args['configfile'],
                    '--dry-run',
                    self.args['actionfile'],
                ],
            )
            return
        self.result = self.runner.invoke(cli, self.runner_args)

    def invoke_runner_alt(self, **kwargs):
        myargs = []
        if kwargs:
            for key, value in kwargs.items():
                myargs.append(f'--{key}')
                myargs.append(value)
            myargs.append(self.args['actionfile'])
            self.result = self.runner.invoke(cli, myargs)
