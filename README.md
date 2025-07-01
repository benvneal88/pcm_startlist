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

1. Clone this repository
2. Install and configured Docker
3. Setup the .env file 
4. Launch the web app with docker-compose


## How it Works

Generating start lists requires three tables from the PCM database:

- Cyclist - matching pcm cyclist id using name
- Team - matching PCM team id using team name
- Race - identify the correct PCM file for the startm list(e.g. `top_giro.xml`)

## PreLoaded PCM Databases

The default application comes setip with a set of databases and startlists

Check data/output/startlists/* for a list of startlists preloaded
Check data/dbs/pcm/* for a list of PCM database preloaded

## Add PCM Database

To add a custom PCM database, first export it to a SQLite file with these steps

1. Download `SQLiteExporter.exe`.
2. Open a command prompt and navigate to the folder containing `SQLiteExporter.exe`.
3. Run the following command to export your `.cdb` file:

```bash
SQLiteExporter.exe -export "Pro Cycling Manager <edition>\Cloud\<your_username>\Career_1.cdb"
```

4. Move the generated `.sqlite` file to the `src/data/pcm_dbs` directory and rename it to match the `pcm_database_name`.

## Running with Docker

1. Quick start with Docker Compose docker-compose up --build
2. Access the web app http://localhost:8080
```



## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.