#!/usr/bin/perl

use strict;
use warnings;

use PerlModules::HtmlEntities;
use File::Path qw(make_path remove_tree);

=begin
Cleans up the HTML that may be in the patent data XML files.
1) Converts HTML entities to UTF8 encodings
=end
=cut

# Helper functions
sub decToHex {
   return '\u' . sprintf "%04X", $_[0]
}

sub entToHex {
   exists $htmlEntities{$_[0]} ? $htmlEntities{$_[0]} : '&' . $_[0] . ';'
}

sub padHex {
   return '\u' . uc sprintf "%04s", $_[0]
}

sub process02to04 {
    my ($FOLDER_PATH, $XML_FILE_NAME) = @_;
    # The 2002-2004 XML files reference external image files which aren't there
    `sed -i -r 's_(<!ENTITY.*NDATA.*>)_<!--\\1-->_g' $FOLDER_PATH/$XML_FILE_NAME`;
    `sed -i -r 's_(<EMI.*FILE.*>)_<!--\\1-->_g' $FOLDER_PATH/$XML_FILE_NAME`;
    `sed -i -r 's_(<CHEMCDX.*FILE.*>)_<!--\\1-->_g' $FOLDER_PATH/$XML_FILE_NAME`;
    `sed -i -r 's_(<CHEMMOL.*FILE.*>)_<!--\\1-->_g' $FOLDER_PATH/$XML_FILE_NAME`;
    # And other crap
    `sed -i -r 's_(<MATHEMATICA.*>)_<!--\\1-->_g' $FOLDER_PATH/$XML_FILE_NAME`;
    `sed -i -r 's_(<CUSTOM-CHARACTER FILE[^>]*>)_<!--\\1-->_g' $FOLDER_PATH/$XML_FILE_NAME`;
}

my @inFileNames = `find ./inData -type f -name "*.zip" -printf "%f\n"`;
foreach (@inFileNames) {
    chomp;
    my $FILE = $_;
    my $FOLDER_PATH="./holdData/$FILE";    
    remove_tree($FOLDER_PATH);
    make_path($FOLDER_PATH);
    `unzip -qq -o -j "./inData/$FILE" -d "$FOLDER_PATH"`;
    # Copy the DTD files and make the changes necessary for the USPTO
    # Patent Grant Bibliographic (Front Page) Text Data
    `cp -r DTDs/* "$FOLDER_PATH"`;    
    # Split the concatenated XML files into separate valid XML files
    my $XML_FILE_NAME=`find $FOLDER_PATH -type f -name \"*.xml\" -printf \"%f\"`;

    process02to04($FOLDER_PATH, $XML_FILE_NAME);
    
    `awk -v folderpath=$FOLDER_PATH '/^<\\?xml/{filename=i++\".xml\";}
    {print > folderpath\"/\"filename;}' $FOLDER_PATH/$XML_FILE_NAME`;
    remove_tree($FOLDER_PATH . "/" . $XML_FILE_NAME);

    my @fileNames = `find $FOLDER_PATH -type f -name "*.xml"`;
    foreach (@fileNames) {
        chomp;
        my $fileName = $_;
        my $outFileName = $fileName . ".cleaned";
	
        open(my $inFile, '<:encoding(UTF-8)', $fileName)
            or die "Could not open file '$fileName' $!";
        open(my $outFile, '>:encoding(UTF-8)', $outFileName)
            or die "Could not open file '$outFileName' $!";

        while (my $row = <$inFile>) {
            chomp $row;
            # Remove the HTML entities
            $row =~ s/&#x([a-zA-Z0-9]{1,4});?/padHex $1/eg; # hexadecimal number
            $row =~ s/&#([0-9]{1,4});?/decToHex $1/eg; # decimal number
            $row =~ s/&([a-zA-Z0-9]+);?/entToHex $1/eg; # HTML entity
            print $outFile "$row\n";
        }
        close $inFile or die "Could not close file '$fileName' $!";
        close $outFile or die "Could not close file '$outFileName' $!";
        `rm $fileName`;
        `mv $outFileName $fileName`;
    }
}
