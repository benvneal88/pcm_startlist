import argparse
import api
from utils import commons

def main():
    parser = argparse.ArgumentParser(description="Start List Generator for Pro Cycling Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: generate_start_list
    parser_startlist = subparsers.add_parser("generate_start_list", help="Generate a start list")
    parser_startlist.add_argument('--pcm_database_id', required=True)
    parser_startlist.add_argument('--pcm_race_id', required=True)
    parser_startlist.add_argument('--race_year', type=int, required=True)
    parser_startlist.add_argument('--start_list_race_name', required=False)
    parser_startlist.add_argument('--start_list_url', required=False)
    parser_startlist.add_argument('--force_start_list_refresh', action='store_true', default=False)

    # Subcommand: import_pcm_database
    parser_loadpcm = subparsers.add_parser("import_pcm_database", help="Load PCM database")
    parser_loadpcm.add_argument('--pcm_database_name', required=True)
    parser_loadpcm.add_argument('--pcm_version', required=True, choices=commons.PCM_VERSIONS, help="PCM version to load the database for")

    # Subcommand: show_pcm_databases
    parser_showdbs = subparsers.add_parser("show_pcm_databases", help="Show loaded PCM databases")
    parser_showdbs.add_argument('--pcm_version')

    # Subcommand: show_pcm_races
    parser_show_pcm_races = subparsers.add_parser("show_pcm_races", help="Show loaded PCM races")
    parser_show_pcm_races.add_argument('--pcm_database_id', required=True)
    parser_show_pcm_races.add_argument('--race_name', default=None)

    # Subcommand: show_start_lists
    parser_showlists = subparsers.add_parser("show_start_lists", help="Show generated start lists")
    parser_showlists.add_argument('--pcm_version', default=None)
    parser_showlists.add_argument('--pcm_database_name', default=None)

    args = parser.parse_args()

    if args.command == "generate_start_list":
        api.generate_start_list(
            pcm_database_id=args.pcm_database_id,
            pcm_race_id=args.pcm_race_id,
            race_year=args.race_year,
            start_list_race_name=args.start_list_race_name,
            start_list_url=args.start_list_url,
            force_start_list_refresh=args.force_start_list_refresh
        )
    elif args.command == "show_pcm_races":
        api.show_pcm_races( 
            pcm_database_id=args.pcm_database_id,
            race_name=args.race_name

        )
    elif args.command == "import_pcm_database":
        api.import_pcm_database(
            pcm_database_name=args.pcm_database_name,
            pcm_version=args.pcm_version
        )
    elif args.command == "show_pcm_databases":
        api.show_pcm_databases(
            pcm_version=args.pcm_version
        )
    elif args.command == "show_start_lists":
        api.show_start_lists(
            pcm_version=args.pcm_version,
            pcm_database_name=args.pcm_database_name
        )

if __name__ == "__main__":
    main()