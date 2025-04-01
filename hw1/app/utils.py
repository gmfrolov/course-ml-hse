import re
import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin


class Parser(BaseEstimator, TransformerMixin):
    @staticmethod
    def parse_torque(value):
        if pd.isna(value):
            return None, None

        value = value.lower().replace(',', '')

        numbers = re.findall(r'\d+\.?\d*', value)
        numbers = [float(num) for num in numbers]

        units = re.findall(r'(?:kgm|nm|rpm)', value)

        torque_value = None
        if 'kgm' in units:
            torque_index = units.index('kgm')
            torque_value = numbers[torque_index] * 9.80665
        elif 'nm' in units:
            torque_index = units.index('nm')
            torque_value = numbers[torque_index]
        elif len(numbers) >= 1 and not any(unit in ['nm', 'kgm'] for unit in units):
            torque_value = numbers[0]

        rpm_value = None
        if 'rpm' in units:
            rpm_index = units.index('rpm')
            rpm_numbers = numbers[rpm_index:]
            rpm_value = max(rpm_numbers)
        elif len(numbers) >= 2 and not any(unit == 'rpm' for unit in units):
            rpm_value = numbers[1]

        return torque_value, rpm_value

    def fit(self, X, y=None):
        X = X.copy()
        num_col = ['torque', 'mileage', 'engine', 'max_power', 'max_torque_rpm', 'seats']
        num_col = ['torque', 'mileage', 'engine', 'max_power', 'max_torque_rpm', 'seats']
        X['mileage'] = X['mileage'].apply(
            lambda x: float(str(x).split()[0]) / 0.75 if 'km/kg' in str(x) else float(str(x).split()[0]))
        X['engine'] = X['engine'].apply(lambda x: float(str(x).split()[0]))
        X['max_power'] = X['max_power'].apply(lambda x: float(str(x).split()[0]) if str(x).split()[
                                                                                        0] != 'bhp' else np.nan)  # Так как возникает ошибка из-за ' bhp' заменим ее на np.nan
        X[['torque', 'max_torque_rpm']] = X['torque'].apply(lambda x: pd.Series(Parser.parse_torque(x)))
        X["name"] = X["name"].apply(lambda x: x.split()[0])
        self.median = X[num_col].median()
        return self

    def transform(self, X):
        X = X.copy()
        num_col = ['torque', 'mileage', 'engine', 'max_power', 'max_torque_rpm', 'seats']
        X['mileage'] = X['mileage'].apply(
            lambda x: float(str(x).split()[0]) / 0.75 if 'km/kg' in str(x) else float(str(x).split()[0]))
        X['engine'] = X['engine'].apply(lambda x: float(str(x).split()[0]))
        X['max_power'] = X['max_power'].apply(lambda x: float(str(x).split()[0]) if str(x).split()[
                                                                                        0] != 'bhp' else np.nan)  # Так как возникает ошибка из-за ' bhp' заменим ее на np.nan
        X[['torque', 'max_torque_rpm']] = X['torque'].apply(lambda x: pd.Series(Parser.parse_torque(x)))
        X["name"] = X["name"].apply(lambda x: x.split()[0])

        X.fillna(self.median, inplace=True)
        X.fillna(self.median, inplace=True)
        X = X.astype({'engine': 'int', 'seats': 'int'})
        return X

