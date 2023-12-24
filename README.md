# Vtuber Discord Schedule Generator

`discordschedule.py` is a Python script for creating formatted schedules for Discord. It takes a text file containing a schedule and outputs a formatted version configured in a JSON file.

## Usage

```python console
discordschedule.py [-h] [-f json] [-nw [N]] schedule.txt
```

### Positional Arguments

- `schedule.txt` - Path to the text file containing the schedule.

### Options

- `-h`, `--help` - Show the help message and exit.
- `-f json`, `--format json` - Specify a JSON file for formatting settings. Default: `schedule.json`.
- `-nw [N]`, `--next-week [N]` - If this option is omitted the schedule will be set to the current week. If enabled the schedule will be generated for the N-th week from now. If `N` is not specified it defaults to `1` (next week's schedule).

## Format Configuration

Create a JSON file (`schedule.json`) that contains settings for the schedule's appearance. See example in [schedule.example.json](./schedule.example.json).

- `heading` - the text that will be put at the top of the schedule
- `date format` - format dates in `{startdate}` and `{enddate}` used in `heading`. Time format codes: https://docs.python.org/3/library/datetime.html#format-codes
- `standard time` - the standard streaming time
- `offline` - a keyword used to identify days without streams. Alternatively an empty line can be placed in the [input file](#input-file).
- `live format` - format for stream timestamp for discord
- `live url format` - format for stream timestamp with the stream URL. This will be used when the URL is specified (see [Input File](#input-file))
- `stream delimiter` - used to separate multiple streams that happen in one day
- `time delimiter` - used to specify custom streaming time
- `timezones` - list the time zone abbreviations and their offset from UTC

## Input File

The input schedule (`schedule.txt`) should list streams. See example in [schedule.example.txt](./schedule.example.txt).

- Each line corresponds to a weekday: 1 - for Monday, 7 - for Sunday.
- Otionaly a URL to the waiting room/live stream can be provided right after the stream title.
- If there are multiple streams in one day separate them with the `stream delimiter` in [schedule.json](#format-configuration) (by default `;`).
- Specify live stream time after a `time delimiter` in [schedule.json](#format-configuration) (by default `,`). If the time zone is omitted UTC is assumed.
If the time is not specified the `standard time` in [schedule.json](#format-configuration) will be used. For date/time format details see https://dateutil.readthedocs.io/en/stable/parser.html
- Everything after `#` will be ignored.
