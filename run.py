import argparse
from src import api


def main():
    # Create the argument parser
    parser = argparse.ArgumentParser(description='Process some integers.')

    # Add arguments
    parser.add_argument('--pcm_database_name', type=str, required=True, help='Name of the PCM database')
    parser.add_argument('--pcm_race_name', type=str, required=True, help='Name of the race')
    parser.add_argument('--race_name', type=str, required=True, help='Name of the race')
    parser.add_argument('--race_year', type=int, required=True, help='Year of the race')

    parser.add_argument('--add_pcm_database_path', type=str, required=False, help='Path to the .cdb')

    # Parse the arguments
    args = parser.parse_args()

    # Access the arguments
    pcm_database_name = args.pcm_database_name.lower()
    race_name = args.race_name.lower()
    pcm_race_name = args.pcm_race_name.lower()
    race_year = args.race_year

    # Output the received arguments (or replace with your actual logic)
    print(f'PCM Database Name: {pcm_database_name}')
    print(f'Race Name: {race_name}')
    print(f'PCM Race Name: {pcm_race_name}')
    print(f'Race Year: {race_year}')

    api.generate_start_list(pcm_database_name, pcm_race_name, race_name, race_year)


if __name__ == '__main__':
    main()