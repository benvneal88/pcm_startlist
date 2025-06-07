# Start List Generator for Pro Cycling Manager

This project is a Python application designed to generate race start lists for the Pro Cycling Manager video game. It pulls real start list data from the internet and integrates it with the race and rider data from the PCM database (SQLite), creating XML files that the game can utilize.

## Features

1. **Web Scraping**: The application scrapes the web for requested race start lists.
2. **Database Interaction**: It extracts cyclists, teams, and races from the PCM database.
3. **XML Generation**: The program matches the start list to the PCM database and generates PCM-compatible start list XML files.

## Project Structure

```
pcm_startlist/
├── src/
│   ├── cli.py          # Command-line interface for the application
│   ├── main.py         # Entry point for the application
│   ├── config.py       # Configuration settings
│   ├── data/           # Directory for data-related modules
│   ├── scrapers/       # Directory for web scraping modules
│   ├── pcm/            # Directory for PCM database interaction
│   ├── model/          # Directory for data model management
│   ├── utils/          # Directory for utility functions
│   └── xml/            # Directory for XML generation
├── tests/              # Directory for unit tests
├── requirements.txt    # Project dependencies
├── setup.py            # Setup script for the package
└── README.md           # Project documentation
```

## Prerequisites

1. Clone this repository.
2. Ensure you have Python installed on your machine.
3. Install the required dependencies listed in `requirements.txt`.

## Usage

This will eventually be pushed to a web app with some basic controls:
- Load a new PCM database
- View existing start lists
- Generate new start lists


To generate a start list, you can use the command-line interface. Here are some example commands:

CLI Usage

### Generate a Start List

```sh
python src/cli.py generate_start_list --pcm_database_name <DB_NAME> --race_name <RACE_NAME> --race_year <YEAR> [--pcm_race_name <PCM_RACE_NAME>]
```

### Load a PCM Database

```sh
python src/cli.py load_pcm_database --pcm_database_name <DB_NAME> [--pcm_version <VERSION>]
```

### Show Loaded PCM Databases

```sh
python3 src/cli.py show_pcm_databases [--pcm_version <VERSION>]
```

how Generated Start Lists

```sh
python src/cli.py show_start_lists [--pcm_version <VERSION>] [--pcm_database_name <DB_NAME>]
```

## How it Works

In order to generate a start list, three tables from the PCM database are needed:

- Cyclist - in order to match the start list rider names to PCM riders
- Team - in order to match the start list teams to PCM teams
- Race - in order to generate the correct start list file name (e.g. `top_giro.xml`)


## Exporting PCM Database

To use the application, you need to export your PCM database as an SQLite file. Follow these steps:

1. Download `SQLiteExporter.exe`.
2. Open a command prompt and navigate to the folder containing `SQLiteExporter.exe`.
3. Run the following command to export your `.cdb` file:

```bash
SQLiteExporter.exe -export "Pro Cycling Manager 2024\Cloud\<your_username>\Career_1.cdb"
```

4. Move the generated `.sqlite` file to the `src/data/pcm_dbs` directory and rename it to match the `pcm_database_name`.

## Running with Docker

1. **Build the Docker image:**
   ```sh
   docker build -t pcm-startlist .
   ```

2. **Run the application:**
   ```sh
   docker run --rm -it pcm-startlist src/cli.py [command] [options]
   ```

3. **Development mode with volume mounting:**
   When developing, you can mount your local `src/` directory to avoid rebuilding the image after code changes:
   ```sh
   docker run --rm -it -v "$(pwd)/src:/app/src" pcm-startlist src/cli.py [command] [options]
   ```

### Docker Command Examples

python3 src/cli.py show_start_lists

# Show PCM databases
python3 src/cli.py show_pcm_databases

# Load a PCM database
python3 src/cli.py import_pcm_database --pcm_database_name "worlddb_2024"

# Generate a start list
python3 src/cli.py generate_start_list --pcm_database_name "my_database" --race_name "Tour de France" --race_year 2024
```

## Troubleshooting

If you encounter issues, check the following:

- Ensure the SQLite database is correctly exported and located in the specified directory.
- Verify that the required dependencies are installed.
- Review the logs for any error messages that can guide you in resolving the issue.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.