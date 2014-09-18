import yaml
from icalendar import Calendar, Event
from datetime import datetime, time, timedelta


class YamlCalConverter():
    DAYS_OF_WEEK = {
        'mo': 0, 'tu': 1, 'we': 2, 'th': 3, 'fr': 4, 'sa': 5, 'su': 6
    }

    def __init__(self, filename):
        self.filename = filename
        self._load_yaml()
        self._ical = Calendar()
        self._convert()

    def _load_yaml(self):
        self.data = yaml.load(file(self.filename, 'r'))
        self.options = self.data['options']
        self.events = self.data['events']

    def _get_period_label(self):
        return self.options['period_label']

    @classmethod
    def generate_series_datetimes(cls, start_date, start_time, end_time, days,
                                  repeat):
        days = [cls.DAYS_OF_WEEK[day] for day in days]
        if len(days) == 0:
            days = cls.DAYS_OF_WEEK.values()

        d = start_date

        results = []

        for i in xrange(repeat):
            while d.weekday() not in days:
                d += timedelta(days=1)

            start = datetime.combine(d, time()) + timedelta(seconds=start_time)
            end = datetime.combine(d, time()) + timedelta(seconds=end_time)
            results.append((start, end))

            d += timedelta(days=1)

        return results

    def _create_description(self, event, i):
        desc = ""
        if 'description' in event:
            desc += event['description'] + "\n\n"
        desc += "{0} of {1}".format(i, event['repeat'])
        desc += "\n{0}: {1}".format(self._get_period_label(),
                                    event['period']['name'])
        for attribute in event['meta']:
            desc += "\n{0}: {1}".format(attribute['attribute'],
                                        attribute['value'])
        return desc

    def _convert(self):
        for event in self.events:
            start_date = event['period']['start']
            if 'start_date' in event:
                start_date = event['start_date']
            dates = YamlCalConverter.generate_series_datetimes(
                start_date, event['start_time'], event['end_time'],
                event['days'], event['repeat'])

            for idx, (start, end) in enumerate(dates):
                e = Event()
                e.add('summary', event['name'])
                e.add('description', self._create_description(event, idx + 1))
                e.add('location', event['location']['description'])
                e.add('dtstart', start)
                e.add('dtend', end)
                self._ical.add_component(e)

    def get_data(self):
        return self.data

    def get_ical(self):
        return self._ical.to_ical()

    def save_ical(self, filename):
        f = open(filename, 'wb')
        f.write(self._ical.to_ical())
        f.close()
