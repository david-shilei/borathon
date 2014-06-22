#!/usr/bin/perl

########################################################################
# Parse a hostd log file, convert it to json string for timeline.js use.
#
# Usage: hostd2json.pl <a hostd log file path> <maxSize>
# Author: lich
#
########################################################################

use strict;
use warnings;
use DateTime;
use DateTime::Format::Strptime;
use JSON::XS;

my $num_args = $#ARGV + 1;
if ($num_args != 2) {
    print "Usage: hostd2json <a hostd log file> <maxSize>\n";
    exit;
}
my $json_file = "$ARGV[0].json";
my $maxSize = $ARGV[1] > 1000 ? 1000 : $ARGV[1];

open LOG, $ARGV[0] or die $!;

my $Strp = new DateTime::Format::Strptime(
    pattern => '%Y%m%d %H:%M:%S.%3N',
    time_zone   => '-0800',
);

my $content = "";
my @events = ();
my $eventHash = 0;
my $outputWc = `wc -l $ARGV[0]`;
my $line = 0;
if($outputWc =~ m/(\d+) (\w)/) {
    $line = $1;
    print "$ARGV[0] has $line lines!\n";
}
if($line == 0) {
    exit;
}
print "We are selecting $maxSize out of $line lines.\n";
my $i = 0;
my $unit = $line / $maxSize;
while(<LOG>) {
   if($_ =~ m/^(\d{4})-(\d{2})-(\d{2})T(\d{2}:\d{2}:\d{2}\.\d{3})Z \[[A-Z0-9]{8} ([a-z]+) [^\]]+\] (.+)$/g) {
       $i += 1;
       if (($i % $unit) == 0) {
           my $dt = $Strp->parse_datetime("$1$2$3 $4");
           my $epoch = $dt->epoch() * 1000 + $dt->millisecond();
           $content = $6;
           my $type = "dot";
           if ($5 eq "verbose") {
               $type = "box";
           }
           $eventHash = {"start" => $epoch,
               "loglevel" => $5,
               "type" => $type,
               "content" => $content
           };
           push @events, $eventHash;
       }
   } else {
       if (($i%$unit) == 0) {
           $eventHash->{"content"} .= $_;
       }
   }
}

my $json_text = encode_json \@events;
open JSON, ">$json_file" or diea $!;
print JSON $json_text;
close LOG;
print "Done. Check $json_file.\n";
