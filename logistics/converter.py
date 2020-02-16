
import requests
import re
import pandas as pd

class Converter:
    """The main class implementing ETL over logistics data"""
    # Data source parameters
    data_url = 'http://157.230.127.203/logistics/'
    authorization_token = 'a5107c4189adc27fe5ec0718b652a990b07aa455'
    # Output parameters
    output_filename = 'logistics_distance_table_transformed.csv'
    # Key field names
    NEXT_FIELD_NAME = 'next'
    RESULTS_FIELD_NAME = 'results'
    DURATION_TEXT_FIELD_NAME = 'DurationText'
    DISTANCE_TEXT_FIELD_NAME = 'DistanceText'
    DURATION_MINUTES_FIELD_NAME = 'DurationMinutes'
    DISTANCE_METERS_FIELD_NAME = 'DistanceMeters'
    # Transformation parameters and helper objects
    duration_pattern = '((?P<hours>\d+)\s+hours?)?\s*((?P<mins>\d+)\s+mins?)?'
    distance_pattern = '(?P<km>\d*\.\d+|\d+)(\s+km)?'
    duration_re = re.compile(duration_pattern)
    distance_re = re.compile(distance_pattern)

    def duration_text_2_minutes(duration_text: str) -> int:
        """Converts duration text into value in minutes

        Args:
            duration_text: A text-based duration description, e.g. '1 hour 15 mins'

        Returns:
            A value in minutes which corresponds to the given text-based description,
            e.g. 75

            If the input string is not a valid duration description, returns None
        """
        m = Converter.duration_re.match(duration_text)
        result = None
        if m:
            minutes = None
            hours = None
            if m.group('hours'):
                hours = int(m.group('hours'))
            if m.group('mins'):
                minutes = int(m.group('mins'))
            if not minutes is None or not hours is None:
                result = int(hours or 0) * 60 + int(minutes or 0)
        return result

    def distance_text_2_meters(distance_text: str) -> int:
        """Converts distance text into value in meters

        Args:
            distance_text: A text-based distance description, e.g. '10.5 km'

        Returns:
            A value in meters which corresponds to the given text-based description,
            e.g. 10500

            If the input string is not a valid distance description, returns None
        """
        m = Converter.distance_re.match(distance_text)
        if m is None or m.group('km') is None:
            return None
        return int(float(m.group('km')) * 1000)

    def __init__(self):
        """Constructor without parameters. Default values of URL and Token are used"""
        self.headers = {'Authorization': 'Token ' + self.authorization_token}

    def read_data_frame(self, data_url: str) -> pd.DataFrame:
        """Reads data from the given URL and converts it into a pandas DataFrame

        Args:
            data_url: the URL of the HTTP endpoint to get data from

        Returns: DataFrame object with data read from the given URL
        """
        data_raw = requests.get(data_url, headers=self.headers)
        data_frame = pd.read_json(data_raw.content)
        return data_frame

    def do_processing(self):
        """Runs the full proccesing cycle"""

        # Read the full dataset following the 'next' url until it is empty
        print("Reading data from " + self.data_url)
        df = self.read_data_frame(self.data_url)
        output_df = pd.DataFrame(df[Converter.RESULTS_FIELD_NAME].tolist())
        while not pd.isna(df[Converter.NEXT_FIELD_NAME].iloc[0]):
            next_url = df[Converter.NEXT_FIELD_NAME].iloc[0]
            df = self.read_data_frame(next_url)
            output_df = output_df.append(pd.DataFrame(df[Converter.RESULTS_FIELD_NAME].tolist()))
        # Add computed columns
        output_df[Converter.DURATION_MINUTES_FIELD_NAME] = output_df[Converter.DURATION_TEXT_FIELD_NAME].apply(Converter.duration_text_2_minutes)
        output_df[Converter.DISTANCE_METERS_FIELD_NAME] = output_df[Converter.DISTANCE_TEXT_FIELD_NAME].apply(Converter.distance_text_2_meters)
        # Save result as CSV
        output_df.to_csv(self.output_filename, index=False)
        print(str(len(output_df.index)) + " row(s) saved to " + self.output_filename)
