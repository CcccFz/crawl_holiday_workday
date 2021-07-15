package util

import (
	"github.com/thoas/go-funk"
	"time"
)

var (
	holidays = []string{
		"2018-12-30", "2018-12-31",
		"2019-01-01", "2019-02-04", "2019-02-05", "2019-02-06", "2019-02-07", "2019-02-08", "2019-02-09", "2019-02-10", "2019-04-05", "2019-05-01", "2019-06-07", "2019-09-13", "2019-10-01", "2019-10-02", "2019-10-03", "2019-10-04", "2019-10-05", "2019-10-06", "2019-10-07",
		"2020-01-01", "2020-01-24", "2020-01-25", "2020-01-26", "2020-01-27", "2020-01-28", "2020-01-29", "2020-01-30", "2020-04-04", "2020-04-05", "2020-04-06", "2020-05-01", "2020-05-02", "2020-05-03", "2020-05-04", "2020-05-05", "2020-06-25", "2020-06-26", "2020-06-27", "2020-10-01", "2020-10-02", "2020-10-03", "2020-10-04", "2020-10-05", "2020-10-06", "2020-10-07", "2020-10-08",
	}
	workdays = []string{
		"2018-12-29",
		"2019-02-02", "2019-02-03", "2019-09-29", "2019-10-12",
		"2020-01-19", "2020-02-01", "2020-04-26", "2020-05-09", "2020-06-28", "2020-09-27", "2020-10-10",
	}
)

func IsHoliday(t time.Time) bool {
	weekday := t.Weekday()
	date := t.Format(DateFormat)

	isSpecialHoliday, isNormalWeekEnd := false, false
	if funk.Contains(holidays, date) {
		isSpecialHoliday = true
	}

	if (weekday == time.Saturday || weekday == time.Sunday) && !funk.Contains(workdays, date) {
		isNormalWeekEnd = true
	}

	return isSpecialHoliday || isNormalWeekEnd
}

func IsWorkday(t time.Time) bool {
	return !IsHoliday(t)
}
