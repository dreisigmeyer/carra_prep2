#!/usr/bin/perl

use strict;
use warnings;

my $outFile = '../../inventors.json';
my @rawData = glob '../usptoData/INVENTOR_*';
my %hash;

open DATA, $rawData[0] or die "Cannot open: $!";
while ( my $line = <DATA> ) {
    $line =~ s/\s*\z//;
    my $last = substr $line, 12, 20;
    $last =~ s/\h+/ /g; # one space for all whitespace
    $last =~ s/[^a-zA-Z ]//g; # all alphabetic or space
    $last =~ tr/a-z/A-Z/; # all uppercase
    $last =~ s/^\s+|\s+$//g; # Trim leading and trailing whitespace
    my $first = substr $line, 33, 15;
    $first =~ s/\h+/ /g; # one space for all whitespace
    $first =~ s/[^a-zA-Z ]//g; # all alphabetic or space
    $first =~ tr/a-z/A-Z/; # all uppercase
    $first =~ s/^\s+|\s+$//g; # Trim leading and trailing whitespace
    my $mi = substr $line, 49, 15;
    $mi =~ s/\h+/ /g; # one space for all whitespace
    $mi =~ s/[^a-zA-Z ]//g; # all alphabetic or space
    $mi =~ tr/a-z/A-Z/; # all uppercase
    $mi =~ s/^\s+|\s+$//g; # Trim leading and trailing whitespace
    if ($mi) {
	$mi = substr $mi, 0, 1;
    }
    my $suffix = substr $line, 65, 3;
    $suffix =~ s/\h+/ /g; # one space for all whitespace
    $suffix =~ s/[^a-zA-Z1-9]//g; # alpha-numeric only (for things like 2ND)
    $suffix =~ tr/a-z/A-Z/; # uppercase
    $suffix =~ s/^\s+|\s+$//g; # Trim leading and trailing whitespace
    if ($suffix ne "") {
	$last = $last . ' ' . $suffix;
    }
    my $city = substr $line, 100, 20;
    $city =~ s/\h+/ /g; # one space for all whitespace
    $city =~ s/[^a-zA-Z ]//g; # all alphabetic or space
    $city =~ tr/a-z/A-Z/; # all uppercase
    $city =~ s/^\s+|\s+$//g; # Trim leading and trailing whitespace
    my $state = substr $line, 121, 3;
    $state =~ s/[^a-zA-Z]//g; # all alphabetic
    $state =~ tr/a-z/A-Z/; # all uppercase
    $state =~ s/^\s+|\s+$//g; # Trim leading and trailing whitespace
    $hash{$last}{$first}{$mi}{$city}{$state} = 1;
}
close DATA;

open(my $fh, '>', $outFile) or die "Cannot open: $!";
print $fh "{";
foreach my $last (sort keys %hash ) {
    print $fh "\n\t\"$last\":{";
    foreach my $first (sort keys %{ $hash{$last} }) {
        print $fh "\n\t\t\"$first\":{";
        foreach my $mi (sort keys %{ $hash{$last}{$first} }) {
            print $fh "\n\t\t\t\"$mi\":[";
            my $outline = "";
            foreach my $city (sort keys %{ $hash{$last}{$first}{$mi} }) {
                foreach my $state (sort keys %{ $hash{$last}{$first}{$mi}{$city} }) {
                    $outline .= "{\"city\":\"$city\", \"state\":\"$state\"},";
                }
            }
            chop($outline);
            print $fh "$outline],";
        }
        seek( $fh, -1, 1);
        print $fh "\n\t\t},";
    }
    seek( $fh, -1, 1);
    print $fh "\n\t},";
}
seek( $fh, -1, 1);
print $fh "\n}\n";
close $fh
