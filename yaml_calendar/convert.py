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
        self._ical.add('summary', self._get_title())
        self._convert()

    def _load_yaml(self):
        self.data = yaml.load(file(self.filename, 'r'))
        self.options = self.data['options']
        self.events = self.data['events']

    def _get_title(self):
        return self.options['title']

    def _count_in_title(self):
        return self.options['count_in_title']

    @staticmethod
    def generate_series_datetimes(start_date, periods, start_time, end_time,
                                  days, repeat):
        d = start_date
        results = []

        for i in xrange(repeat):
            while True:
                if periods is not None:
                    if d < periods[0]['start'] or d > periods[0]['end']:
                        periods.pop(0)
                        if len(periods) == 0:
                            raise ValueError("Cannot satisfy repeats within"
                                             " given periods.")
                        d = periods[0]['start']
                if d.weekday() in days:
                    break
                d += timedelta(days=1)

            start = datetime.combine(d, time()) + timedelta(seconds=start_time)
            end = datetime.combine(d, time()) + timedelta(seconds=end_time)
            results.append((start, end))

            d += timedelta(days=1)

        return results

    def _create_description(self, event, i):
        desc = []
        if 'description' in event:
            desc.append(event['description'])
        if not self._count_in_title() and 'repeat' in event:
            desc.append("{0} of {1}".format(i, event['repeat']))
        for attribute in event['meta']:
            desc.append("{0}: {1}".format(attribute['attribute'],
                                          attribute['value']))
        return "\n".join(desc)

    def _convert(self):
        for event in self.events:
            start_date = event['periods'][0]['start']
            if 'start_date' in event:
                start_date = event['start_date']
            repeat = 1
            if 'repeat' in event:
                repeat = event['repeat']
            days = YamlCalConverter.DAYS_OF_WEEK.values()
            if 'days' in event:
                days = [YamlCalConverter.DAYS_OF_WEEK[day] for day in
                        event['days']]
            periods = None
            if 'periods' in event:
                periods = event['periods'] if len(event['periods']) != 0 else \
                    None

            dates = YamlCalConverter.generate_series_datetimes(
                start_date, periods, event['start_time'],
                event['end_time'], days, repeat)

            for idx, (start, end) in enumerate(dates):
                e = Event()
                title = event['name']
                if self._count_in_title() and 'repeat' in event:
                    title += " ({0} of {1})".format(idx + 1, event['repeat'])
                e.add('summary', title)
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
