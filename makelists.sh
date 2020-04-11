#!/usr/bin/bash

aspell -l en dump master | grep -E "^[A-Za-z]{3}$" | tr [:lower:] [:upper:] | sort -u > words
grep -v '\(^\| \)\([A-Za-z]\)\2\2\($\| \)' words > words3
aspell -l en dump master | grep -E "^[A-Za-z]{4}$" | tr [:lower:] [:upper:] | sort -u > words
grep -v '\(^\| \)\([A-Za-z]\)\2\2\($\| \)' words > words4
aspell -l en dump master | grep -E "^[A-Za-z]{5}$" | tr [:lower:] [:upper:] | sort -u > words
grep -v '\(^\| \)\([A-Za-z]\)\2\2\($\| \)' words > words5
aspell -l en dump master | grep -E "^[A-Za-z]{6}$" | tr [:lower:] [:upper:] | sort -u > words
grep -v '\(^\| \)\([A-Za-z]\)\2\2\($\| \)' words > words6
aspell -l en dump master | grep -E "^[A-Za-z]{7}$" | tr [:lower:] [:upper:] | sort -u > words
grep -v '\(^\| \)\([A-Za-z]\)\2\2\($\| \)' words > words7
aspell -l en dump master | grep -E "^[A-Za-z]{8}$" | tr [:lower:] [:upper:] | sort -u > words
grep -v '\(^\| \)\([A-Za-z]\)\2\2\($\| \)' words > words8
aspell -l en dump master | grep -E "^[A-Za-z]{9}$" | tr [:lower:] [:upper:] | sort -u > words
grep -v '\(^\| \)\([A-Za-z]\)\2\2\($\| \)' words > words9
aspell -l en dump master | grep -E "^[A-Za-z]{10}$" | tr [:lower:] [:upper:] | sort -u > words
grep -v '\(^\| \)\([A-Za-z]\)\2\2\($\| \)' words > words10
rm words
