from backend.database.user_database import EconomyDatabase
db = EconomyDatabase()
for acc in db.get_all_accounts():
    if acc['provider'] == 'modal':
        print(acc['workspace'], acc['is_active'], acc['last_balance'])
