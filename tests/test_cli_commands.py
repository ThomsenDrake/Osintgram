import builtins
import runpy
import sys
import types
import unittest


def run_command(command):
    # stub third party modules
    requests_stub = types.ModuleType("requests")
    sys.modules['requests'] = requests_stub

    geopy_stub = types.ModuleType("geopy")
    geocoders_stub = types.ModuleType("geopy.geocoders")
    geocoders_stub.Nominatim = lambda user_agent=None: types.SimpleNamespace(reverse=lambda x: types.SimpleNamespace(address=""))
    geopy_stub.geocoders = geocoders_stub
    sys.modules['geopy'] = geopy_stub
    sys.modules['geopy.geocoders'] = geocoders_stub

    prettytable_stub = types.ModuleType("prettytable")
    class PT(list):
        field_names = []
        align = {}
        def add_row(self, row):
            pass
        def __str__(self):
            return ""
    prettytable_stub.PrettyTable = PT
    sys.modules['prettytable'] = prettytable_stub

    sys.modules['gnureadline'] = types.SimpleNamespace(
        parse_and_bind=lambda *a, **k: None,
        set_completer=lambda *a, **k: None,
    )
    sys.modules['pyreadline'] = types.ModuleType("pyreadline")
    sys.modules['pyreadline'].Readline = lambda: types.SimpleNamespace(
        parse_and_bind=lambda *a, **k: None,
        set_completer=lambda *a, **k: None,
    )

    ipa = types.ModuleType("instagram_private_api")
    ipa.Client = types.SimpleNamespace(generate_uuid=lambda: "uuid")
    ipa.ClientCookieExpiredError = Exception
    ipa.ClientLoginRequiredError = Exception
    ipa.ClientError = Exception
    ipa.ClientThrottledError = Exception
    sys.modules['instagram_private_api'] = ipa

    config_stub = types.ModuleType("src.config")
    config_stub.getUsername = lambda: "user"
    config_stub.getPassword = lambda: "pass"
    sys.modules['src.config'] = config_stub

    sys.modules.pop('src.Osintgram', None)
    sys.modules.pop('main', None)
    import src.Osintgram as osint_mod

    class DummyAPI:
        def user_followers(self, *a, **k):
            return {'users': [{'pk': 1, 'username': 'u1', 'full_name': 'U1'}]}
        def user_following(self, *a, **k):
            return {'users': [{'pk': 1, 'username': 'u1', 'full_name': 'U1'}]}
        def user_info(self, *a, **k):
            return {'user': {'public_email': 'm@mail.com', 'contact_phone_number': '123'}}
        def username_info(self, *a, **k):
            return {'user': {'pk': 1, 'is_private': False}}
        def user_feed(self, *a, **k):
            return {'items': [], 'next_max_id': None}
        def media_comments(self, *a, **k):
            return {'comments': [], 'next_max_id': None}
        def _call_api(self, *a, **k):
            return {'user_detail': {'user': {'friendship_status': {'following': True}}}}

    class DummyOsintgram(osint_mod.Osintgram):
        def __init__(self, target, is_file, is_json, is_cli, output_dir, clear_cookies):
            self.target = target
            self.target_id = 1
            self.is_private = False
            self.following = True
            self.cli_mode = is_cli
            self.writeFile = is_file
            self.jsonDump = is_json
            self.output_dir = output_dir or 'output'
            self.api = DummyAPI()
        def login(self, u, p):
            pass
        def setTarget(self, target):
            pass
        def __printTargetBanner__(self):
            pass
        def check_following(self):
            return True

    osint_mod.Osintgram = DummyOsintgram

    original_input = builtins.input
    builtins.input = lambda *a, **k: (_ for _ in ()).throw(AssertionError("input called"))
    try:
        sys.argv = ['main.py', 'target', '--command', command]
        runpy.run_module('main', run_name='__main__')
    finally:
        builtins.input = original_input

class CLIModeTest(unittest.TestCase):
    def test_cli_commands_no_wait_for_input(self):
        for cmd in [
            "fwersemail",
            "fwingsemail",
            "fwersnumber",
            "fwingsnumber",
        ]:
            run_command(cmd)


if __name__ == "__main__":
    unittest.main()
