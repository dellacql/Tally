from tally_wallet.wallet import TallyWallet

def test_new_account_generates_address(tmp_path):
    # Use a temp file for keyring
    wallet = TallyWallet(str(tmp_path / "test.keys"))
    addr = wallet.new_account()
    assert addr in wallet.list_accounts()