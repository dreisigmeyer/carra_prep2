#!/usr/bin/perl

=begin comment
Why are you here? Go AWAY!

Call it like (dates may change):

./cleanCityNames.pl

Then run city_xslt.py like

./city_xslt.py cityNames.xml > mapCityNames.xml

This uses the hand cleaned inventor city/state information
to create a map from 'dirty' city names to clean ones.

At the bottom we create some common words that are removed.  You'll want
to go through the final XML file and take out the entries that shouldn't
be removed.  You'll need to be the final arbitrator of which those are.
=end comment
=cut

use strict;
use warnings;

#my $outFile = 'cityMisspellings.xml';
my $outFile = 'cityMisspellings.json';
my @rawData = glob '../usptoData/INVENTOR_*';
my @cleanData = glob '../usptoData/INV_COUNTY_*';
my %holdData = ();
my %hash = ();

# A list of misspellings not on the DVD
open MISSPELLS, '../userData/city_misspellings.csv' or die "Cannot open: $!";
while (my $line = <MISSPELLS>) {
    $line =~ s/\s*\z//;
    my @holder = split /,/, $line;
    my $state = $holder[0];
    my $correct = $holder[1];
    my $misspell = $holder[2];
    $hash{$state}{$correct}{$misspell} = 1;
}
close MISSPELLS;

# Get the clean data we'll map to
open DATA, $cleanData[0] or die "Cannot open: $!";
while ( my $line = <DATA> ) {
    $line =~ s/\s*\z//;
    my $zip = substr $line, 94, 5;
    $zip =~ s/^\s+|\s+$//g; # Trim leading and trailing whitespace
    next if $zip; # self-assigned - these seem to not be corrected    
    my $city = substr $line, 69, 20;
    my $state = substr $line, 90, 3;
    $city =~ s/^\s+|\s+$//g;
    $state =~ s/^\s+|\s+$//g;
    $city =~ s/\h+/ /g; # one space for all whitespace
    $city =~ s/[^a-zA-Z ]//g; # all alphabetic
    $city =~ tr/a-z/A-Z/; # all uppercase
    $state =~ s/[^a-zA-Z ]//g; # all alphabetic
    $state =~ tr/a-z/A-Z/; # all uppercase
    next unless (length $city); # There needs to be a city name
    next unless ((length $state) == 2); # Needs to be a state not a country
    my $patNum = substr $line, 0, 7;
    my $invSeq = substr $line, 8, 3;
    $patNum =~ s/^\s+|\s+$//g;
    $invSeq =~ s/^\s+|\s+$//g;
    next if ($city =~ /\bCOUNTY\b/); # Ignore any map to a county
    $holdData{$patNum}{$invSeq}{$state}{"City Name"} = $city;
    @{ $holdData{$patNum}{$invSeq}{$state}{"Alias"} } = ($city);
}
close DATA;

# Do the mapping 
open DATA, $rawData[0] or die "Cannot open: $!";
while ( my $line = <DATA> ) {
    $line =~ s/\s*\z//;
    my $city = substr $line, 100, 20;
    $city =~ s/(LATE OF)//i; # This should be removed from the strings
    my $state = substr $line, 121, 3;
    $city =~ s/^\s+|\s+$//g;
    $state =~ s/^\s+|\s+$//g;
    $city =~ s/\h+/ /g; # one space for all whitespace
    $city =~ s/[^a-zA-Z ]//g; # all alphabetic
    $city =~ tr/a-z/A-Z/; # all uppercase
    $state =~ s/[^a-zA-Z ]//g; # all alphabetic or space
    $state =~ tr/a-z/A-Z/; # all uppercase
    my $patNum = substr $line, 0, 7;
    my $invSeq = substr $line, 8, 3;
    $patNum =~ s/^\s+|\s+$//g;
    $invSeq =~ s/^\s+|\s+$//g;
    if (exists $holdData{$patNum} # avoiding autovivification here
	and exists $holdData{$patNum}{$invSeq}
	and exists $holdData{$patNum}{$invSeq}{$state}) { # US inventor
	push @{ $holdData{$patNum}{$invSeq}{$state}{"Alias"} }, $city;
    }
}
close DATA;

foreach my $patNum (keys %holdData) {    
    foreach my $invSeq (keys %{ $holdData{$patNum} }) {
	foreach my $state (keys %{ $holdData{$patNum}{$invSeq} }) {	    
	    my $city = $holdData{$patNum}{$invSeq}{$state}{"City Name"};
	    foreach my $alias (@{ $holdData{$patNum}{$invSeq}{$state}{"Alias"} }) {
		$hash{$state}{$city}{$alias} = 1;
	    }
	}
    }
}

open(my $fh, '>', $outFile) or die "Cannot open: $!";
# print $fh "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
# print $fh "<states>\n";
# foreach my $state (sort keys %hash ) {
#     print $fh "\t<state abbrev=\"$state\">\n";
#     foreach my $city (sort keys %{ $hash{$state} }) {
# 	foreach my $alias (sort keys %{ $hash{$state}{$city} }) {
# 	    next if ($alias eq $city); # Only want mis-spellings
# 	    print $fh "\t\t<alias name=\"$alias\">";
# 	    print $fh "$city";
# 	    print $fh "</alias>\n";
# 	}
#     }
#     print $fh "\t</state>\n";
# }
# print $fh "</states>";
print $fh "{\n";
foreach my $state (sort keys %hash ) {
    print $fh "\t\"$state\":{\n";
    foreach my $city (sort keys %{ $hash{$state} }) {
        print $fh "\t\t\"$city\":[";
        my $outline = "";
        foreach my $alias (sort keys %{ $hash{$state}{$city} }) {
            $outline .= "\"$alias\",";
        }
        chop($outline);
        print $fh "$outline],\n";
    }
    print $fh "\t},\n";
}
print $fh "}\n";
close $fh
