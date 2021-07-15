package util

import (
	"github.com/stretchr/testify/assert"
	"testing"
	"time"
)

func TestIsHoliday(t *testing.T) {
	ast := assert.New(t)

	tests := []struct {
		in     string
		expect bool
	}{
		{"2020-01-01 00:00", true},
		{"2020-01-01 17:30", true},
		{"2020-01-02 00:00", false},
		{"2020-01-02 17:30", false},
		{"2020-01-03 00:00", false},
		{"2020-01-03 23:59", false},
		{"2020-01-04 00:00", true},
		{"2020-01-04 23:59", true},
		{"2020-01-05 00:00", true},
		{"2020-01-05 23:59", true},
		{"2020-01-23 00:00", false},
		{"2020-01-23 23:59", false},
		{"2020-01-24 00:00", true},
		{"2020-01-24 23:59", true},
		{"2020-01-30 00:00", true},
		{"2020-01-30 23:59", true},
		{"2020-01-31 00:00", false},
		{"2020-01-31 23:59", false},
		{"2020-02-01 00:00", false},
		{"2020-02-01 23:59", false},
		{"2020-02-02 00:00", true},
		{"2020-02-02 23:59", true},
		{"2020-02-03 00:00", false},
		{"2020-02-03 23:59", false},
		{"2020-04-03 00:00", false},
		{"2020-04-03 23:59", false},
		{"2020-04-04 00:00", true},
		{"2020-04-04 23:59", true},
		{"2020-04-06 00:00", true},
		{"2020-04-06 23:59", true},
		{"2020-04-30 00:00", false},
		{"2020-04-30 23:59", false},
		{"2020-05-01 00:00", true},
		{"2020-05-01 23:59", true},
		{"2020-05-02 00:00", true},
		{"2020-05-02 23:59", true},
		{"2020-05-03 00:00", true},
		{"2020-05-03 23:59", true},
		{"2020-05-04 00:00", true},
		{"2020-05-04 23:59", true},
		{"2020-05-05 00:00", true},
		{"2020-05-05 23:59", true},
		{"2020-05-09 00:00", false},
		{"2020-05-09 23:59", false},
		{"2020-05-10 00:00", true},
		{"2020-05-10 23:59", true},
	}

	for _, test := range tests {
		_time, _ := time.ParseInLocation(DateTimeFormat, test.in, time.Local)
		actual := IsHoliday(_time)

		ast.Equal(test.expect, actual, test.in)
	}
}

func TestIsWorkday(t *testing.T) {
	ast := assert.New(t)

	tests := []struct {
		in     string
		expect bool
	}{
		{"2021-05-18 00:00", true},
	}

	for _, test := range tests {
		_time, _ := time.ParseInLocation(DateFormat, test.in, time.Local)
		actual := IsWorkday(_time)

		ast.Equal(test.expect, actual, test.in)
	}
}

func BenchmarkIsHoliday(b *testing.B) {
	b.StopTimer()
	t, _ := time.ParseInLocation(DateFormat, "2020-01-01 17:30", time.Local)
	b.StartTimer()

	for i := 0; i < b.N; i++ {
		IsHoliday(t)
	}
}
