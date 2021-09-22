import yaml
from icalendar import Calendar, Event
from datetime import datetime, time, timedelta
import pytz


class YamlCalConverter():
    DAYS_OF_WEEK = {
        'mo': 0, 'tu': 1, 'we': 2, 'th': 3, 'fr': 4, 'sa': 5, 'su': 6
    }

    def __init__(self, filename=None, yaml_markup=None):
        self.options = {}
        self.events = []
        self._load_yaml(filename, yaml_markup)

    def _load_yaml(self, filename, yaml_markup):
        data = None
        if filename is not None:
            data = yaml.safe_load(open(filename, 'r'))
        elif yaml_markup is not None:
            data = yaml.safe_load(yaml_markup)
        else:
            raise ValueError('No YAML supplied.')
        self.options.update(data['options'])
        self.events += data['events']
        self.converted = False

    def _get_title(self):
        return self.options['title']

    def _count_in_title(self):
        return self.options.get('count_in_title', True)

    def _get_timezone(self):
        return self.options['timezone']

    @staticmethod
    def generate_series_datetimes(start_date, periods, start_time, end_time,
                                  days, repeat, tz):
        d = start_date
        results = []

        for i in range(repeat):
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
            start = tz.localize(start)
            end = datetime.combine(d, time()) + timedelta(seconds=end_time)
            end = tz.localize(end)
            results.append((start, end))

            d += timedelta(days=1)

        return results

    def _create_description(self, event, i):
        desc = []
        if 'description' in event:
            desc.append(event['description'])
        if not self._count_in_title() and 'repeat' in event:
            desc.append("{0} of {1}".format(i, event['repeat']))
        if 'meta' in event:
            for attribute in event['meta']:
                desc.append("{0}: {1}".format(attribute['attribute'],
                                              attribute['value']))
        return "\n".join(desc)

    def _convert(self):
        if self.converted:
            return
        self._ical = Calendar()
        self._ical.add('summary', self._get_title())
        tz = pytz.timezone(self._get_timezone())
        for event in self.events:
            start_date = event.get('start_date')
            if start_date is None:
                start_date = event['periods'][0]['start']
            repeat = event.get('repeat', 1)
            days = YamlCalConverter.DAYS_OF_WEEK.values()
            if 'days' in event:
                days = [YamlCalConverter.DAYS_OF_WEEK[day] for day in
                        event['days']]
            periods = None
            if 'periods' in event:
                periods = list(event['periods']) if len(event['periods']) > 0 \
                    else None

            dates = YamlCalConverter.generate_series_datetimes(
                start_date, periods, event['start_time'],
                event['end_time'], days, repeat, tz)

            index_offset = event.get('start_at', 1)
            total = event.get('out_of', repeat)
            overrides_unlocalized = event.get('overrides', {})
            overrides = {}
            for key, val in overrides_unlocalized.items():
                overrides[tz.localize(key)] = {
                    'start': tz.localize(val['start']),
                    'end': tz.localize(val['end']),
                }

            for idx, (start, end) in enumerate(dates):
                times = overrides.get(start, {'start': start, 'end': end})
                e = Event()
                title = event['name']
                if self._count_in_title() and total > 1:
                    title += " ({0} of {1})".format(index_offset + idx,
                                                    total)
                e.add('summary', title)
                e.add('description', self._create_description(event, idx + 1))
                if isinstance(event['location'], str):
                    e.add('location', event['location'])
                else:
                    e.add('location', event['location']['description'])
                e.add('dtstart', times['start'])
                e.add('dtend', times['end'])
                self._ical.add_component(e)
        self.converted = True

    def add_data(self, filename=None, yaml_markup=None):
        self._load_yaml(filename, yaml_markup)

    def get_ical(self):
        self._convert()
        return self._ical.to_ical()

    def save_ical(self, filename):
        self._convert()
        f = open(filename, 'wb')
        f.write(self._ical.to_ical())
        f.close()
