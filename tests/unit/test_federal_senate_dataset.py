import os
from tempfile import gettempdir
from unittest import TestCase
from unittest.mock import patch

import pandas as pd

from serenata_toolbox.federal_senate.federal_senate_dataset import FederalSenateDataset


class TestFederalSenateDataset(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected_files = ['federal-senate-2008.csv',
                              'federal-senate-2009.csv']

    @patch('serenata_toolbox.federal_senate.federal_senate_dataset.urlretrieve')
    def test_fetch_files_from_S3(self, mocked_url_etrieve):
        self.path = gettempdir()
        self.subject = FederalSenateDataset(self.path)

        retrieved_files, not_found_files = self.subject.fetch()

        self.assertTrue(mocked_url_etrieve.called)
        self.assertEqual(mocked_url_etrieve.call_count, len(self.subject.year_range))
        for retrieved_file, expected_file in zip(
                retrieved_files, self.expected_files):

            self.assertIn(expected_file, retrieved_file)

    def test_fetch_not_found_files_from_S3(self):
        self.path = gettempdir()
        self.subject = FederalSenateDataset(self.path, 2007, 2008)

        retrieved_files, not_found_files = self.subject.fetch()

        for not_found_file, expected_file in zip(
                not_found_files, self.expected_files):

            self.assertIn('federal-senate-2007.csv', not_found_file)

    def test_dataset_translation(self):
        self.subject = FederalSenateDataset(os.path.join('tests', 'fixtures', 'csv'),
                                            2008,
                                            2009)

        expected_files = ['federal-senate-2008.csv']

        translated_files, not_found_files = self.subject.translate()

        for translated_file, expected_file in zip(
                translated_files, expected_files):

            self.assertIn(expected_file, translated_file)

    def test_if_translation_happened_as_expected(self):
        self.subject = FederalSenateDataset(os.path.join('tests', 'fixtures', 'csv'),
                                            2008,
                                            2009)

        file_path = os.path.join(self.subject.path, 'federal-senate-2008.csv')
        federal_senate_2008 = pd.read_csv(file_path,
                                          sep=';',
                                          encoding='ISO-8859-1',
                                          skiprows=1)
        self.assertIsNotNone(federal_senate_2008['ANO'],
                             'expects \'ANO\' as column in this dataset')

        self.subject.translate()

        translated_file_path = os.path.join(self.subject.path, 'federal-senate-2008.xz')
        translated_federal_senate_2008 = pd.read_csv(translated_file_path,
                                                     encoding='utf-8')

        self.assertIsNotNone(translated_federal_senate_2008['year'],
                             'expects \'year\' as column in this dataset')

        os.remove(os.path.join(self.subject.path, 'federal-senate-2008.xz'))

    def test_dataset_translation_failing_to_find_file(self):
        self.subject = FederalSenateDataset(os.path.join('tests', 'fixtures', 'csv'),
                                            2007,
                                            2008)

        expected_files = ['federal-senate-2007.csv']

        translated_files, not_found_files = self.subject.translate()

        for not_found_files, expected_file in zip(
                not_found_files, expected_files):

            self.assertIn(expected_file, not_found_files)

    def test_dataset_cleanup(self):
        self.subject = FederalSenateDataset(os.path.join('tests', 'fixtures', 'xz'),
                                            2009,
                                            2010)

        reimbursement_path = self.subject.clean()

        expected_path = os.path.join('tests',
                                     'fixtures',
                                     'xz',
                                     'federal-senate-reimbursements.xz')
        self.assertEqual(
            reimbursement_path,
            expected_path
        )

        os.remove(expected_path)
